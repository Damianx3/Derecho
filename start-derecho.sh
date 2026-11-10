#!/bin/bash
# Start the normal offline pipeline and show failures before opening the kiosk.
set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
GEMMA_DIR="$HOME/Projects/gemma-translator"
GEMMA_BIN="$GEMMA_DIR/venv/bin/litert-lm"
BACKEND_PYTHON="$PROJECT_DIR/.venv/bin/python"

fail() {
  echo "Derecho could not start: $*" >&2
  exit 1
}

require_file() {
  [[ -f "$1" ]] || fail "Missing $1. Copy the complete code bundle to the Pi."
}

ready() {
  curl --fail --silent --max-time 2 "$1" >/dev/null 2>&1
}

wait_for_service() {
  local name="$1" url="$2" pid="$3" log="$4"
  echo "Waiting for $name..."
  for ((attempt=0; attempt<90; attempt++)); do
    if ! kill -0 "$pid" 2>/dev/null; then
      tail -n 30 "$log" >&2
      fail "$name exited. Full log: $log"
    fi
    if ready "$url"; then
      echo "$name ready."
      return
    fi
    sleep 1
  done
  tail -n 30 "$log" >&2
  fail "$name did not become ready. Full log: $log"
}

for command in curl npm firefox arecord aplay; do
  command -v "$command" >/dev/null || fail "Required command not found: $command"
done
[[ -x "$GEMMA_BIN" ]] || fail "Gemma executable missing: $GEMMA_BIN"
[[ -x "$BACKEND_PYTHON" ]] || fail "Backend Python missing: $BACKEND_PYTHON"
for file in backend/derecho/api.py backend/derecho/languages.py \
  backend/derecho/asr/live_transcription.py backend/derecho/tts/piper_worker.py \
  frontend/package.json frontend/src/App.jsx frontend/src/style.css frontend/src/i18n.mjs; do
  require_file "$PROJECT_DIR/$file"
done
[[ -d "$PROJECT_DIR/frontend/node_modules" ]] || fail "Frontend dependencies are missing. Existing node_modules is required for offline startup."

# Diagnostic output only: never change device numbers or system volume here.
{
  echo "Microphone inventory:"
  arecord -l || true
  echo "Speaker inventory:"
  aplay -l || true
} > "$HOME/derecho-audio-devices.log" 2>&1

echo "Derecho project: $PROJECT_DIR"
echo "Audio inventory saved to $HOME/derecho-audio-devices.log"

if ready http://127.0.0.1:9379/v1/models; then
  echo "Gemma is already running; reusing it."
else
  (cd "$GEMMA_DIR" && exec "$GEMMA_BIN" serve --host 127.0.0.1 --port 9379) \
    > "$HOME/gemma.log" 2>&1 &
  wait_for_service Gemma http://127.0.0.1:9379/v1/models "$!" "$HOME/gemma.log"
fi

if ready http://127.0.0.1:8000/api/health; then
  if ! ready http://127.0.0.1:8000/api/languages; then
    fail "An older backend is still running. Restart the Pi once after installing the update, then run this script."
  fi
  echo "Derecho API is already running; reusing it. Restart it after code changes."
else
  # Use the working CLI pipeline; optional experiments require separate testing.
  (cd "$PROJECT_DIR" && exec env PYTHONPATH="$PROJECT_DIR/backend" \
    DERECHO_WHISPER_SERVER= DERECHO_LIVE_STT=0 DERECHO_PIPER_PERSISTENT=0 \
    "$BACKEND_PYTHON" -m uvicorn derecho.api:app --host 0.0.0.0 --port 8000) \
    > "$HOME/derecho-api.log" 2>&1 &
  wait_for_service "Derecho API" http://127.0.0.1:8000/api/health "$!" "$HOME/derecho-api.log"
fi

if ready http://127.0.0.1:5173; then
  echo "Frontend is already running; reusing it."
else
  (cd "$PROJECT_DIR/frontend" && exec npm run dev -- --host 0.0.0.0 --strictPort) \
    > "$HOME/derecho-ui.log" 2>&1 &
  wait_for_service Frontend http://127.0.0.1:5173 "$!" "$HOME/derecho-ui.log"
fi

echo "Derecho ready. Opening the touchscreen UI."
DISPLAY="${DISPLAY:-:0}" firefox --kiosk http://127.0.0.1:5173
