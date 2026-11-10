"""Optional rolling preview; finalize the complete recording before translation."""
from pathlib import Path
import hashlib
import io
import threading
import wave

from derecho.asr.whisper_client import transcribe_audio, transcribe_wav

def snapshot_wav(path):
    # arecord finalizes its header on stop. Rebuild a valid header for the bytes
    # currently available instead of uploading its unfinished WAV directly.
    output = io.BytesIO()
    with wave.open(str(path), "rb") as reader:
        params = reader.getparams()
        chunks = []
        while frames := reader.readframes(4096):
            chunks.append(frames)
    frames = b"".join(chunks)
    with wave.open(output, "wb") as writer:
        writer.setparams(params._replace(nframes=len(frames) // (params.sampwidth * params.nchannels)))
        writer.writeframes(frames)
    seconds = len(frames) / (params.sampwidth * params.nchannels * params.framerate)
    return output.getvalue(), hashlib.sha256(frames).hexdigest(), seconds

class LiveTranscription:
    def __init__(self, path, language_code, interval=3):
        self.path = Path(path)
        self.language_code = language_code
        self.interval = interval
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.preview = ""
        self.warning = ""
        self.fingerprint = None
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def status(self):
        with self.lock:
            return {"partial_transcript": self.preview, "preview_warning": self.warning}

    def _run(self):
        while not self.stop_event.wait(self.interval):
            try:
                wav, fingerprint, seconds = snapshot_wav(self.path)
            except (OSError, EOFError, wave.Error):
                # A new recording may not have a complete header yet.
                continue
            if seconds < 1 or fingerprint == self.fingerprint or self.stop_event.is_set():
                continue
            try:
                text = transcribe_wav(wav, self.language_code)
                with self.lock:
                    self.preview, self.fingerprint, self.warning = text, fingerprint, ""
            except Exception:
                with self.lock:
                    self.warning = "Live preview unavailable; transcription will finish after release."
                return

    def finalize(self):
        self.stop_event.set()
        if self.thread.ident is not None:
            self.thread.join(timeout=95)
            if self.thread.is_alive():
                raise RuntimeError("Live transcription did not finish in time")
        _, fingerprint, _ = snapshot_wav(self.path)
        with self.lock:
            if self.fingerprint == fingerprint and self.preview:
                return self.preview
        # A preview can omit trailing words or revise an earlier phrase. Never
        # translate stale partial text: decode the final complete WAV when changed.
        return transcribe_audio(str(self.path), self.language_code)

    def cancel(self):
        self.stop_event.set()
