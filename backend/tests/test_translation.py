from collections import OrderedDict
from pathlib import Path
import io
import json
import struct
import tempfile
import threading
import unittest
from unittest.mock import patch
import wave
import urllib.error

from derecho.asr import whisper_client as whisper
from derecho.asr.live_transcription import LiveTranscription, snapshot_wav
from derecho.integration import translator_pipeline as pipeline
from derecho.translation import gemma_client as gemma
from derecho.tts import piper_client as piper
from derecho.tts.piper_worker import synthesize

class RecognitionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'recording.wav'
        self.write_audio(16000)

    def write_audio(self, frames):
        with wave.open(str(self.path), 'wb') as writer:
            writer.setnchannels(1); writer.setsampwidth(2); writer.setframerate(16000)
            writer.writeframes(b'\x01\x00' * frames)

    def test_snapshot_repairs_unfinished_header(self):
        data = bytearray(self.path.read_bytes())
        data[4:8] = struct.pack('<I', 0xffffffff)
        data[40:44] = struct.pack('<I', 0xffffffff)
        self.path.write_bytes(data)
        wav, _, seconds = snapshot_wav(self.path)
        with wave.open(io.BytesIO(wav), 'rb') as reader:
            self.assertEqual(reader.getnframes(), 16000)
        self.assertEqual(seconds, 1)

    def test_finalized_audio_reuses_exact_preview(self):
        live = LiveTranscription(self.path, 'es')
        live.preview = 'Hola'
        _, live.fingerprint, _ = snapshot_wav(self.path)
        with patch('derecho.asr.live_transcription.transcribe_audio') as transcribe:
            self.assertEqual(live.finalize(), 'Hola')
            transcribe.assert_not_called()

    def test_changed_audio_always_gets_final_pass(self):
        live = LiveTranscription(self.path, 'es')
        live.preview = 'No'
        _, live.fingerprint, _ = snapshot_wav(self.path)
        self.write_audio(20000)
        with patch('derecho.asr.live_transcription.transcribe_audio', return_value='No quiero eso') as transcribe:
            self.assertEqual(live.finalize(), 'No quiero eso')
            transcribe.assert_called_once_with(str(self.path), 'es')

    def test_preview_runs_while_recording_and_finalizes_once(self):
        received = threading.Event()
        def recognize(wav, language):
            self.assertEqual(language, 'es')
            received.set()
            return 'Hola mundo'
        live = LiveTranscription(self.path, 'es', interval=.01)
        with patch('derecho.asr.live_transcription.transcribe_wav', side_effect=recognize) as transcribe:
            live.start()
            try:
                self.assertTrue(received.wait(1))
                self.assertEqual(live.finalize(), 'Hola mundo')
                self.assertEqual(transcribe.call_count, 1)
            finally:
                live.cancel(); live.thread.join(1)

    def test_preview_connection_error_is_visible(self):
        live = LiveTranscription(self.path, 'es', interval=.01)
        with patch('derecho.asr.live_transcription.transcribe_wav', side_effect=urllib.error.URLError('offline')):
            live.start()
            try:
                live.thread.join(1)
                self.assertFalse(live.thread.is_alive())
                self.assertIn('unavailable', live.status()['preview_warning'])
            finally:
                live.cancel()

    def test_server_request_contains_language_and_valid_audio(self):
        with patch.object(whisper, 'WHISPER_SERVER', 'http://127.0.0.1:8080/inference'):
            with patch.object(whisper.urllib.request, 'urlopen', return_value=io.BytesIO(b'{"text":" Bonjour "}')) as send:
                self.assertEqual(whisper.transcribe_wav(self.path.read_bytes(), 'fr'), 'Bonjour')
                request = send.call_args.args[0]
                self.assertIn(b'name="language"\r\n\r\nfr', request.data)
                self.assertIn(self.path.read_bytes(), request.data)
                self.assertEqual(send.call_args.kwargs['timeout'], 90)

class TranslationTests(unittest.TestCase):
    def response(self, content, reason='stop'):
        return io.BytesIO(json.dumps({'choices':[{'message':{'content':content}, 'finish_reason':reason}]}).encode())

    def test_prompt_preserves_names_numbers_and_negation(self):
        with patch.object(gemma.urllib.request, 'urlopen', return_value=self.response('No quiero eso')) as send:
            self.assertEqual(gemma.translate_text('I do not want that', 'English', 'Spanish'), 'No quiero eso')
            payload = json.loads(send.call_args.args[0].data)
            self.assertIn('names, numbers, and negation', payload['messages'][0]['content'])
            self.assertEqual(payload['messages'][1]['content'], 'I do not want that')

    def test_empty_and_truncated_translations_rejected(self):
        for content, reason in [('', 'stop'), ('A partial', 'length')]:
            with self.subTest(reason=reason), patch.object(gemma.urllib.request, 'urlopen', return_value=self.response(content, reason)):
                with self.assertRaises(RuntimeError): gemma.translate_text('Hello', 'English', 'Spanish')

    def test_pipeline_uses_final_transcript_and_calls_translation_once(self):
        timings = {}
        with patch.object(pipeline, 'transcribe_audio') as stt, patch.object(pipeline, 'translate_text', return_value='Hola') as translate, patch.object(pipeline, 'speak_text') as speak, patch.object(pipeline, 'perf_counter', side_effect=range(7)):
            result = pipeline.process_audio('unused.wav', 'en', 'English', 'Spanish', finalize_transcript=lambda:'Hello', timings=timings)
            self.assertEqual(result, ('Hello','Hola'))
            stt.assert_not_called()
            translate.assert_called_once_with('Hello','English','Spanish')
            speak.assert_called_once_with('Hola','Spanish')
            self.assertEqual(timings['after_release_seconds'],6)

class VoiceCacheTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output = str(Path(self.directory.name)/'speech.wav')

    def test_current_api_reuses_voice_and_limits_cache(self):
        loaded = []
        class Voice:
            @staticmethod
            def load(model):
                loaded.append(model); return Voice()
            def synthesize_wav(self, text, writer):
                writer.setnchannels(1); writer.setsampwidth(2); writer.setframerate(22050)
                writer.writeframes(b'\x01\x00')
        voices = OrderedDict()
        for model in ['en','es','en','fr']:
            synthesize(voices,Voice,model,'Hello',self.output)
        self.assertEqual(loaded,['en','es','fr'])
        self.assertEqual(list(voices),['en','fr'])
        with wave.open(self.output,'rb') as reader: self.assertEqual(reader.getnframes(),1)

    def test_legacy_piper_api_supported(self):
        class Voice:
            @staticmethod
            def load(model): return Voice()
            def synthesize(self,text,writer):
                writer.setnchannels(1); writer.setsampwidth(2); writer.setframerate(22050)
                writer.writeframes(b'\x01\x00')
        synthesize(OrderedDict(),Voice,'es','Hola',self.output)
        self.assertTrue(Path(self.output).exists())

    def test_worker_startup_failure_falls_back_to_existing_cli(self):
        with patch.object(piper,'PERSISTENT_PIPER',True), patch.object(piper,'_worker_unavailable',False), patch.object(piper,'_worker',None):
            with patch.object(piper.subprocess,'Popen',side_effect=FileNotFoundError), patch.object(piper.subprocess,'run') as run:
                piper.generate_speech('Hola',Path('spanish.onnx'))
                run.assert_called_once()
                self.assertEqual(run.call_args.kwargs['input'],'Hola')

if __name__ == '__main__': unittest.main()
