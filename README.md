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

## Start here

On a configured Pi, run this from the repository root:

```sh
./start-derecho.sh
```

See [Pi setup and troubleshooting](docs/pi-setup.md) for prerequisites, model
paths, audio setup, and logs.

## Find your way around

| Path | What it contains |
| --- | --- |
| `start-derecho.sh` | The launcher for the Pi kiosk |
| `backend/derecho/` | FastAPI, recording, translation, speech, and legal retrieval |
| `frontend/src/` | Touchscreen app and interface translations |
| `data/legal_sources/` | Source PDFs, source metadata, and searchable chunks |
| `docs/` | Setup, architecture, walkthroughs, and testing notes |

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

See the [architecture map](docs/architecture.md), [translator walkthrough](docs/translation-walkthrough.md) for the data
flow and [contribution guide](CONTRIBUTING.md) for the branch and review workflow.
