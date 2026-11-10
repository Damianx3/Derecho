# Translation audio and language setup

Replay uses the latest translated WAV from the current backend session. It does
not run Whisper, Gemma, or Piper again. The original WAV remains unchanged.

Speech volume (0–100) and mute apply to Derecho playback, not the Raspberry Pi's
system mixer. A temporary WAV is scaled to the selected volume, then played with
the original aplay WAV-file command. Volume changes apply to the next playback,
not a sentence already playing. The original latest WAV stays unchanged.

## USB audio device selection

Derecho checks the capture and playback inventories separately when recording
or playing audio. It prefers the known USB microphone (ALSA ID `Device`) and
speaker (`UACDemoV10`), using card IDs rather than numeric card assignments.
If the known device is absent, it uses the sole USB endpoint for that direction.
If no USB endpoint exists or several are equally eligible, it reports an error
instead of picking HDMI or guessing. Optional overrides are documented in
`.env.example`. The launcher still records the ALSA inventory for diagnostics.

## Add a language

backend/derecho/languages.py is the enabled-language registry. The frontend reads
GET /api/languages; it contains no independent voice or Whisper-code mapping.
Existing English and Spanish entries are preserved, but require Pi validation.

Candidate next voices from the Piper catalog:

- French: fr_FR-siwis-medium.onnx and its .onnx.json file.
  https://huggingface.co/rhasspy/piper-voices/tree/main/fr/fr_FR/siwis/medium
- Brazilian Portuguese: pt_BR-faber-medium.onnx and its .onnx.json file.
  https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR/faber/medium

These are selectable testing languages, not yet verified on the Pi. Inspect the voice's
MODEL_CARD, install its model/configuration on the Pi, then check:

1. Actual whisper-cli transcription of representative speech with the requested
   language code and the installed tiny model.
2. Gemma translation in both directions, reviewed by a fluent speaker, including
   numbers, names, negation, and conversational phrases.
3. Local Piper synthesis and USB-speaker playback, with understandable pronunciation.
4. A full recorded conversation, swapped languages, Take Turn, Speak Again,
   Replay, volume, and mute on the physical touchscreen while offline.

French, Portuguese, and German are already in the registry with testing=True.
After successful evaluation, remove their testing flags. Choosing a regional Piper voice does not establish broader dialect
coverage. Their UI labels clearly indicate Still testing.

## Local checks

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=backend python3 -m unittest discover -s backend/tests
cd frontend
npm run build
```

Audio unit tests use generated samples and mocked aplay; they do not establish
hardware compatibility. UI fixture responses are also not translation validation.

## Launch everything with one command

Run ./start-derecho.sh on the Pi desktop as before. It checks local files and
executables, starts Gemma/API/Vite, waits for HTTP readiness, and opens Firefox.
Existing healthy services are reused, so restart the Pi once after deploying
updated code to prevent an older Python process from remaining in memory.
Vite uses --strictPort to avoid silently moving the UI to another port.
Optional Whisper/live/Piper-worker experiments are disabled for this launcher.
The launcher saves `arecord -l` and `aplay -l` output to
`~/derecho-audio-devices.log` without changing audio settings.
Readiness does not prove microphone or speaker operation.

If startup fails, the script prints the service name and recent log output.
Logs remain ~/gemma.log, ~/derecho-api.log, and ~/derecho-ui.log. It does not
install dependencies, download models, or kill existing services automatically.
