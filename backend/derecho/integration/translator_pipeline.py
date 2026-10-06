from derecho.audio.recorder import record_audio
from derecho.asr.whisper_client import transcribe_audio
from derecho.translation.gemma_client import translate_text
from derecho.tts.piper_client import speak_text


def process_audio(
    audio_path: str,
    source_language_code: str,
    source_language_name: str,
    target_language_name: str,
) -> tuple[str, str]:
    """Transcribe, translate, and speak an existing audio file."""

    transcript = transcribe_audio(
        audio_path,
        source_language_code,
    )

    translation = translate_text(
        transcript,
        source_language_name,
        target_language_name,
    )

    speak_text(
        translation,
        target_language_name,
    )

    return transcript, translation


def run_translation(
    source_language_code: str,
    source_language_name: str,
    target_language_name: str,
    duration: int = 5,
) -> tuple[str, str]:
    """Record for a fixed duration, then process the audio."""

    audio_path = record_audio(
        "~/derecho-live-test.wav",
        duration=duration,
    )

    return process_audio(
        audio_path,
        source_language_code,
        source_language_name,
        target_language_name,
    )
