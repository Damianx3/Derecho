# Pi setup and startup

Use a Raspberry Pi 5 with a touchscreen, USB microphone, and USB speaker.
Start the launcher from a session that can access the Pi desktop. The
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
See [audio setup](translation-audio.md) for device overrides and voice setup.

Normal operation requires no internet connection. The latest input and output
WAVs remain on the device; **Done** clears the conversation display.
