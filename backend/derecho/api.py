from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from derecho.audio.recorder import start_recording, stop_recording
from derecho.integration.translator_pipeline import process_audio


app = FastAPI()


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
def record_start():
    audio_path = start_recording()

    return {
        "status": "recording",
        "audio_path": audio_path,
    }


@app.post("/api/record/stop")
def record_stop(request: StopRecordingRequest):
    audio_path = stop_recording()

    transcript, translation = process_audio(
        audio_path,
        request.source_language_code,
        request.source_language_name,
        request.target_language_name,
    )

    return {
        "transcript": transcript,
        "translation": translation,
    }
