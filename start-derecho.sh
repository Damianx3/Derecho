#!/bin/bash

# -----------------------------
# DERECHO startup script
# -----------------------------

# Give the desktop and USB devices time to initialize.
sleep 5

# Start Gemma
cd /home/damian/Projects/gemma-translator
source venv/bin/activate

litert-lm serve \
  --host 127.0.0.1 \
  --port 9379 \
  > /home/damian/gemma.log 2>&1 &


# Give Gemma time to initialize.
sleep 8


# Start Derecho FastAPI
cd /home/damian/Projects/Derecho
source .venv/bin/activate

PYTHONPATH=backend uvicorn derecho.api:app \
  --host 0.0.0.0 \
  --port 8000 \
  > /home/damian/derecho-api.log 2>&1 &


# Start React/Vite UI
cd /home/damian/Projects/Derecho/frontend

npm run dev -- --host 0.0.0.0 \
  > /home/damian/derecho-ui.log 2>&1 &


# Give the servers time to start.
sleep 5


# Open Derecho on the Pi touchscreen.
DISPLAY=:0 firefox --kiosk http://127.0.0.1:5173
