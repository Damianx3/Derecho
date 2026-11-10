from array import array
from pathlib import Path
import os
import atexit
import json
import logging
import select
import subprocess
import sys
import threading
import tempfile
import wave

from derecho.languages import VOICE_DIR, get_language
from derecho.audio.devices import resolve_device

PIPER_BIN = Path.home() / "Projects" / "piper-venv" / "bin" / "piper"
OUTPUT_FILE = Path.home() / "derecho-tts.wav"
_playback_lock = threading.Lock()
_state_lock = threading.Lock()
_volume = 80
_muted = False
_has_audio = False
_worker = None
_worker_unavailable = False
PERSISTENT_PIPER = os.environ.get("DERECHO_PIPER_PERSISTENT", "0") == "1"
PIPER_PYTHON = Path(os.environ.get("DERECHO_PIPER_PYTHON", str(PIPER_BIN.with_name("python")))).expanduser()

def close_worker():
    global _worker
    process, _worker = _worker, None
    if process is None:
        return
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait()
    process.stdin.close(); process.stdout.close()

atexit.register(close_worker)

def worker_reply(timeout):
    if not select.select([_worker.stdout], [], [], timeout)[0]:
        raise RuntimeError("Piper worker timed out")
    line = _worker.stdout.readline()
    if not line:
        raise RuntimeError("Piper worker stopped unexpectedly")
    return json.loads(line)

def generate_speech(text, voice):
    global _worker, _worker_unavailable
    if PERSISTENT_PIPER and not _worker_unavailable:
        if _worker is None:
            try:
                _worker = subprocess.Popen([str(PIPER_PYTHON), str(Path(__file__).with_name("piper_worker.py"))],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
                if not worker_reply(30).get("ready"):
                    raise RuntimeError("Piper Python API unavailable")
            except (OSError, RuntimeError, ValueError):
                close_worker()
                _worker_unavailable = True
                logging.getLogger(__name__).warning("Persistent Piper unavailable; using the existing CLI")
        if _worker is not None:
            try:
                _worker.stdin.write(json.dumps({"model": str(voice), "text": text, "output": str(OUTPUT_FILE)}) + "\n")
                _worker.stdin.flush()
                reply = worker_reply(180)
                if not reply.get("ok"):
                    raise RuntimeError("Piper synthesis failed: " + reply.get("error", "unknown error"))
                return
            except (OSError, RuntimeError, ValueError):
                close_worker()
                raise
    subprocess.run([str(PIPER_BIN), "-m", str(voice), "-f", str(OUTPUT_FILE)],
                   input=text, text=True, check=True, timeout=180)

def audio_state():
    with _state_lock:
        return {"volume": _volume, "muted": _muted, "has_audio": _has_audio}

def set_volume(volume: int, muted: bool):
    global _volume, _muted
    if not 0 <= volume <= 100:
        raise ValueError("Volume must be between 0 and 100")
    with _state_lock:
        _volume, _muted = volume, muted
    return audio_state()

def scale_frames(frames, volume):
    """Piper emits little-endian signed 16-bit PCM; never modify its saved WAV."""
    samples = array("h", frames)
    if sys.byteorder != "little":
        samples.byteswap()
    samples = array("h", (round(sample * volume / 100) for sample in samples))
    if sys.byteorder != "little":
        samples.byteswap()
    return samples.tobytes()

def _play_latest():
    state = audio_state()
    if state["muted"] or state["volume"] == 0:
        return
    # Preserve the prototype's aplay WAV-file path. Apply volume to a temporary
    # copy, leaving the original intact for future replay at any volume.
    with tempfile.TemporaryDirectory(prefix="derecho-playback-") as directory:
        playback = Path(directory) / "playback.wav"
        with wave.open(str(OUTPUT_FILE), "rb") as reader:
            if reader.getsampwidth() != 2 or reader.getcomptype() != "NONE":
                raise RuntimeError("Playback volume requires 16-bit PCM Piper audio")
            with wave.open(str(playback), "wb") as writer:
                writer.setparams(reader.getparams())
                while frames := reader.readframes(4096):
                    writer.writeframes(scale_frames(frames, state["volume"]))
        subprocess.run(["aplay", "-D", resolve_device('playback'), str(playback)],
                       check=True, timeout=180)

def replay_audio():
    if not _playback_lock.acquire(blocking=False):
        raise RuntimeError("Audio is already playing")
    try:
        if not audio_state()["has_audio"] or not OUTPUT_FILE.is_file():
            raise ValueError("No translated audio to replay yet")
        _play_latest()
    finally:
        _playback_lock.release()

def speak_text(text: str, language: str) -> None:
    global _has_audio
    voice = VOICE_DIR / get_language(language)["voice"]
    if not voice.is_file() or not Path(str(voice) + ".json").is_file():
        raise ValueError(f"Piper model or configuration missing for {language}")
    with _playback_lock:
        with _state_lock:
            _has_audio = False
        generate_speech(text, voice)
        with _state_lock:
            _has_audio = True
        _play_latest()
