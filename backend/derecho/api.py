from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from derecho.audio.recorder import start_recording, stop_recording
from derecho.integration.translator_pipeline import process_audio


from derecho.languages import get_language, public_languages
from derecho.tts.piper_client import audio_state, set_volume, replay_audio
import os
import logging
import subprocess
import threading

from derecho.asr.live_transcription import LiveTranscription
from derecho.asr.whisper_client import WHISPER_SERVER

app = FastAPI()
_live = None
LIVE_PREVIEW = os.environ.get("DERECHO_LIVE_STT", "0") == "1" and bool(WHISPER_SERVER)

class StartRecordingRequest(BaseModel):
    source_language_code: str = "en"

@app.get("/api/record/status")
def recording_status():
    preview = _live
    return {"live_enabled": LIVE_PREVIEW, **(preview.status() if preview is not None else
            {"partial_transcript": "", "preview_warning": ""})}

_operation_lock = threading.Lock()
logger = logging.getLogger("uvicorn.error")

def operation(function):
    if not _operation_lock.acquire(blocking=False):
        raise HTTPException(409, "Please wait for the current operation to finish")
    try:
        return function()
    except ValueError as error:
        logger.exception("Derecho operation failed: %s", function.__name__)
        raise HTTPException(400, str(error)) from error
    except RuntimeError as error:
        logger.exception("Derecho operation failed: %s", function.__name__)
        raise HTTPException(409, str(error)) from error
    except (OSError, subprocess.SubprocessError) as error:
        logger.exception("Derecho operation failed: %s", function.__name__)
        raise HTTPException(503, "Local audio or model service failed. Check the device logs.") from error
    finally:
        _operation_lock.release()

class VolumeRequest(BaseModel):
    volume: int = Field(ge=0, le=100)
    muted: bool = False

@app.get("/api/languages")
def languages():
    return public_languages()

@app.get("/api/audio")
def get_audio_state():
    return audio_state()

@app.post("/api/audio/volume")
def volume(request: VolumeRequest):
    return set_volume(request.volume, request.muted)

@app.post("/api/audio/replay")
def replay():
    operation(replay_audio)
    return audio_state()



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StopRecordingRequest(BaseModel):
    source_language_code: str
    source_language_name: str
    target_language_name: str


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/record/start")
def record_start(request: StartRecordingRequest = None):
    language_code = request.source_language_code if request else "en"
    if language_code not in {item["code"] for item in public_languages() if item["enabled"]}:
        raise HTTPException(400, "Unsupported source language")

    def start():
        global _live
        audio_path = start_recording()
        if _live is not None:
            _live.cancel()
        _live = LiveTranscription(audio_path, language_code) if LIVE_PREVIEW else None
        if _live is not None:
            _live.start()
        return audio_path

    audio_path = operation(start)

    return {
        "status": "recording",
        "audio_path": audio_path,
    }


@app.post("/api/record/stop")
def record_stop(request: StopRecordingRequest):
    try:
        source = get_language(request.source_language_name)
        get_language(request.target_language_name)
        if source["code"] != request.source_language_code:
            raise ValueError("Source language code does not match its name")
        if request.source_language_name == request.target_language_name:
            raise ValueError("Choose two different languages")
    except ValueError as error:
        raise HTTPException(400, str(error)) from error

    def translate():
        global _live
        preview, _live = _live, None
        try:
            audio_path = stop_recording()
            timings = {}
            transcript, translation = process_audio(
                audio_path, source["code"], request.source_language_name, request.target_language_name,
                finalize_transcript=preview.finalize if preview is not None and preview.language_code == source["code"] else None, timings=timings)
            return {"transcript": transcript, "translation": translation, "timings": timings, **audio_state()}
        finally:
            if preview is not None:
                preview.cancel()

    return operation(translate)
