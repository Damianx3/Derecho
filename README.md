# Derecho

Derecho is a Raspberry Pi 5 senior-design project for offline speech translation
and source-grounded immigration-rights information. The translator runs locally
once its tools and models are installed.

## Current status

- **Translator Mode:** Hold to speak, then release. Whisper recognizes the selected
  source language, Gemma 4 E2B translates the text, and Piper speaks the result.
  The touchscreen shows the transcript and translation, with Replay and volume.
  USB capture and playback devices are selected automatically.
- **Languages:** English and Spanish are the baseline. French, Brazilian Portuguese,
  and German are selectable and labeled **Still testing**. Interface language is
  separate from the two speech languages.
- **Know Your Rights:** English and Spanish source files, PDF ingestion, and BM25
  retrieval are in the repository. The application screen is still a placeholder;
  cited answers are not yet connected to it.

## Run on the Pi

Use the Pi desktop session with a USB microphone and speaker connected. The
launcher expects these components to be installed:

| Component | Expected location or requirement |
| --- | --- |
| Backend environment | Repository `.venv/bin/python` with FastAPI and Uvicorn |
| Frontend | Node 22.12+ on the 22.x line (or another version supported by the lockfile); run `npm ci` in `frontend/` during setup |
| Whisper | `~/Projects/whisper.cpp/build/bin/whisper-cli` and `~/Projects/whisper.cpp/models/ggml-tiny.bin` |
| Gemma | `~/Projects/gemma-translator/venv/bin/litert-lm`, with `gemma4-e2b` available locally |
| Piper | `~/Projects/piper-venv/bin/piper` and the required model/config pairs in `~/Projects/piper-voices/` |
| System commands | `curl`, `arecord`, `aplay`, and `firefox` |

Once those prerequisites are in place, run from the repository root:

```sh
./start-derecho.sh
```

The launcher waits for Gemma, FastAPI, and Vite, then opens Firefox in kiosk mode.
It can reuse already-running services. After updating backend code, stop the
previous backend before relaunching so it loads the new version.

If a test fails, check `~/derecho-api.log`, `~/gemma.log`, or `~/derecho-ui.log`.
The launcher writes the audio inventory to `~/derecho-audio-devices.log`.
See [audio setup](docs/translation-audio.md) for device overrides and voice setup.

Normal operation requires no internet connection. The latest input and output
WAVs remain on the device; **Done** clears the conversation display.

## Verify a change

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=backend python3 -m unittest discover -s backend/tests
cd frontend
npm ci
npm test
npm run build
```

Automated checks do not validate physical audio or model accuracy. For a Pi smoke
test, launch the app, run one English → Spanish turn, and verify the transcript,
translation, playback, and Replay.

See the [translator walkthrough](docs/translation-walkthrough.md) for the data
flow and [contribution guide](CONTRIBUTING.md) for the branch and review workflow.
