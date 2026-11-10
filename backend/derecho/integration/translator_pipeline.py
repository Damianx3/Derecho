import logging
from time import perf_counter

from derecho.audio.recorder import record_audio
from derecho.asr.whisper_client import transcribe_audio
from derecho.translation.gemma_client import translate_text
from derecho.tts.piper_client import speak_text


def process_audio(
    audio_path: str,
    source_language_code: str,
    source_language_name: str,
    target_language_name: str,
    *,
    finalize_transcript=None,
    timings=None,
) -> tuple[str, str]:
    """Transcribe, translate, and speak an existing audio file."""

    measurements = timings if timings is not None else {}
    started = perf_counter()
    transcript = (finalize_transcript() if finalize_transcript is not None
                  else transcribe_audio(audio_path, source_language_code))
    measurements["stt_seconds"] = round(perf_counter() - started, 3)

    translated = perf_counter()
    translation = translate_text(transcript, source_language_name, target_language_name)
    measurements["translation_seconds"] = round(perf_counter() - translated, 3)

    spoken = perf_counter()
    speak_text(translation, target_language_name)
    measurements["speech_and_playback_seconds"] = round(perf_counter() - spoken, 3)
    measurements["after_release_seconds"] = round(perf_counter() - started, 3)
    # Timing only: keep transcripts and translations out of performance logs.
    logging.getLogger(__name__).info("Translation timings: %s", measurements)

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
