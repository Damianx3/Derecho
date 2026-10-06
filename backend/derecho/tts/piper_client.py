from pathlib import Path
import subprocess


PIPER_BIN = Path.home() / "Projects" / "piper-venv" / "bin" / "piper"
VOICE_DIR = Path.home() / "Projects" / "piper-voices"

VOICES = {
    "English": VOICE_DIR / "en_US-lessac-medium.onnx",
    "Spanish": VOICE_DIR / "es_ES-davefx-medium.onnx",
}

SPEAKER_DEVICE = "plughw:3,0"


def speak_text(text: str, language: str) -> None:
    """Generate speech in the target language and play it."""

    if language not in VOICES:
        raise ValueError(f"No Piper voice configured for {language}")

    voice = VOICES[language]
    output_file = Path.home() / "derecho-tts.wav"

    subprocess.run(
        [
            str(PIPER_BIN),
            "-m",
            str(voice),
            "-f",
            str(output_file),
        ],
        input=text,
        text=True,
        check=True,
    )

    subprocess.run(
        [
            "aplay",
            "-D",
            SPEAKER_DEVICE,
            str(output_file),
        ],
        check=True,
    )


if __name__ == "__main__":
    speak_text(
        "¿Dónde está el hospital más cercano?",
        "Spanish",
    )
