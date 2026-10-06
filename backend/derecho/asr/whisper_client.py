from pathlib import Path
import subprocess


WHISPER_DIR = Path.home() / "Projects" / "whisper.cpp"
WHISPER_BIN = WHISPER_DIR / "build" / "bin" / "whisper-cli"
WHISPER_MODEL = WHISPER_DIR / "models" / "ggml-tiny.bin"


def transcribe_audio(audio_path: str, language_code: str) -> str:
    """Transcribe a WAV file using local whisper.cpp."""

    audio_file = Path(audio_path).expanduser()

    command = [
        str(WHISPER_BIN),
        "-m",
        str(WHISPER_MODEL),
        "-f",
        str(audio_file),
        "-l",
        language_code,
        "-bs",
        "1",
        "-bo",
        "1",
        "-nt",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"Whisper failed: {error.stderr}"
        ) from error

    transcript = result.stdout.strip()

    if not transcript:
        raise RuntimeError("Whisper returned an empty transcript.")

    return transcript


if __name__ == "__main__":
    transcript = transcribe_audio(
        "~/translator-test.wav",
        "en",
    )

    print("Transcript:", transcript)
