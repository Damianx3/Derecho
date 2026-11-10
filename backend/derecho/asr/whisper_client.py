from pathlib import Path
import json
import os
import subprocess
import urllib.request
import uuid

WHISPER_DIR = Path.home() / "Projects" / "whisper.cpp"
WHISPER_BIN = Path(os.environ.get("DERECHO_WHISPER_BIN", str(WHISPER_DIR / "build/bin/whisper-cli"))).expanduser()
WHISPER_MODEL = Path(os.environ.get("DERECHO_WHISPER_MODEL", str(WHISPER_DIR / "models/ggml-tiny.bin"))).expanduser()
WHISPER_SERVER = os.environ.get("DERECHO_WHISPER_SERVER", "")
WHISPER_THREADS = int(os.environ.get("DERECHO_WHISPER_THREADS", "4"))
WHISPER_TIMEOUT = 90

def transcribe_wav(wav_bytes: bytes, language_code: str) -> str:
    """Use a separately started local whisper-server, keeping its model warm."""
    if not WHISPER_SERVER:
        raise RuntimeError("Live transcription requires a local Whisper server")
    boundary = "derecho-" + uuid.uuid4().hex
    body = bytearray()
    for key, value in {"language": language_code, "response_format": "json"}.items():
        body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode())
    body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="recording.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode())
    body.extend(wav_bytes)
    body.extend(f'\r\n--{boundary}--\r\n'.encode())
    request = urllib.request.Request(WHISPER_SERVER, data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
    with urllib.request.urlopen(request, timeout=WHISPER_TIMEOUT) as response:
        result = json.loads(response.read())
    text = result.get("text", "").strip()
    if not text:
        raise RuntimeError("Whisper returned an empty transcript")
    return text

def transcribe_audio(audio_path: str, language_code: str) -> str:
    audio_file = Path(audio_path).expanduser()
    if WHISPER_SERVER:
        return transcribe_wav(audio_file.read_bytes(), language_code)
    command = [str(WHISPER_BIN), "-m", str(WHISPER_MODEL), "-f", str(audio_file),
               "-l", language_code, "-t", str(WHISPER_THREADS), "-bs", "1", "-bo", "1", "-nt"]
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                check=True, timeout=WHISPER_TIMEOUT)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"Whisper failed: {error.stderr}") from error
    transcript = result.stdout.strip()
    if not transcript:
        raise RuntimeError("Whisper returned an empty transcript")
    return transcript
