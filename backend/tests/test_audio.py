import io
import sys
from array import array
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import wave

from derecho.tts import piper_client as audio
from derecho.languages import get_language, public_languages

class AudioTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.original = Path(self.directory.name) / 'original.wav'
        self.frames = array('h', [10000, -10000, 32767, -32768, 0]).tobytes()
        if sys.byteorder != 'little':
            samples = array('h', self.frames); samples.byteswap(); self.frames = samples.tobytes()
        with wave.open(str(self.original), 'wb') as writer:
            writer.setnchannels(1); writer.setsampwidth(2); writer.setframerate(22050)
            writer.writeframes(self.frames)
        audio.set_volume(80, False)
        resolver = patch.object(audio, 'resolve_device', return_value='plughw:CARD=UACDemoV10,DEV=0')
        resolver.start()
        self.addCleanup(resolver.stop)

    def samples(self, frames):
        samples = array('h', frames)
        if sys.byteorder != 'little': samples.byteswap()
        return list(samples)

    def test_volume_scaling_and_boundaries(self):
        self.assertEqual(self.samples(audio.scale_frames(self.frames, 50)), [5000,-5000,16384,-16384,0])
        self.assertEqual(self.samples(audio.scale_frames(self.frames, 0)), [0]*5)
        self.assertEqual(audio.scale_frames(self.frames, 100), self.frames)
        with self.assertRaises(ValueError): audio.set_volume(101, False)

    def test_replay_uses_saved_audio_without_resynthesis(self):
        before = self.original.read_bytes()
        audio.set_volume(50, False)
        def playback(command, **kwargs):
            self.assertEqual(command[:3], ['aplay', '-D', 'plughw:CARD=UACDemoV10,DEV=0'])
            self.assertEqual(len(command), 4)
            with wave.open(command[3], 'rb') as reader:
                self.assertEqual(self.samples(reader.readframes(reader.getnframes()))[0], 5000)
        with patch.object(audio, 'OUTPUT_FILE', self.original), patch.object(audio, '_has_audio', True):
            with patch.object(audio.subprocess, 'run', side_effect=playback) as launch:
                audio.replay_audio()
                launch.assert_called_once()
        self.assertEqual(before, self.original.read_bytes())

    def test_volume_changes_apply_to_next_playback_and_mute_skips_audio(self):
        levels = []
        def playback(command, **kwargs):
            with wave.open(command[3], 'rb') as reader:
                levels.append(self.samples(reader.readframes(reader.getnframes()))[0])
        with patch.object(audio, 'OUTPUT_FILE', self.original), patch.object(audio.subprocess, 'run', side_effect=playback):
            audio.set_volume(50, False); audio._play_latest()
            audio.set_volume(100, False); audio._play_latest()
            audio.set_volume(100, True); audio._play_latest()
        self.assertEqual(levels, [5000,10000])

    def test_failed_playback_releases_replay_lock(self):
        with patch.object(audio, '_has_audio', True), patch.object(audio, 'OUTPUT_FILE', self.original):
            with patch.object(audio, '_play_latest', side_effect=OSError('speaker unavailable')):
                with self.assertRaises(OSError): audio.replay_audio()
        self.assertFalse(audio._playback_lock.locked())

    def test_no_audio_and_busy_replay(self):
        with patch.object(audio, '_has_audio', False):
            with self.assertRaises(ValueError): audio.replay_audio()
        audio._playback_lock.acquire()
        try:
            with self.assertRaises(RuntimeError): audio.replay_audio()
        finally: audio._playback_lock.release()

    def test_registry_and_unknown_language(self):
        self.assertEqual(get_language('Spanish')['code'], 'es')
        self.assertEqual(len(public_languages()), 5)
        self.assertTrue(get_language('French')['testing'])
        with self.assertRaises(ValueError): get_language('Unknown')

if __name__ == '__main__': unittest.main()
