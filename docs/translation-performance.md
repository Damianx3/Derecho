# Translation performance experiments

Defaults preserve whisper-cli + tiny and Piper CLI. No models or dependencies
are automatically installed. All inference remains local.

## Measure before choosing a model

The stop response includes timings: stt_seconds, translation_seconds,
speech_and_playback_seconds, and after_release_seconds. The last value excludes
recording and recorder shutdown; speech time includes the spoken audio duration.
Compare the same 5–10 second recordings over several cold/warm runs. Separately
check transcription and translation with a fluent speaker. Timings alone do not
measure accuracy. Backend performance logs contain timings, not spoken text.

Set DERECHO_WHISPER_MODEL to compare installed tiny/base models. The default
remains ggml-tiny.bin. Use multilingual base, not base.en, for Spanish and the
additional languages. Larger models may improve accuracy at a latency cost.
DERECHO_WHISPER_THREADS defaults to four; benchmark rather than assuming more
threads are faster. No changed model has been benchmarked on this Pi yet.

## Persistent Whisper and live preview

If the existing whisper.cpp build includes whisper-server, start it separately:

```sh
cd /home/damian/Projects/whisper.cpp
./build/bin/whisper-server -m models/ggml-tiny.bin -t 4 -bs 1 -bo 1 --host 127.0.0.1 --port 8080
```

Then export in the backend shell before starting uvicorn:

```sh
export DERECHO_WHISPER_SERVER='http://127.0.0.1:8080/inference'
export DERECHO_LIVE_STT=1
```

The server's -m option selects its model; DERECHO_WHISPER_MODEL only selects the
CLI model. Check your installed server's --help for supported flags. No Whisper server build is installed automatically. The startup script intentionally
uses the baseline CLI pipeline; run the backend separately to test these options.

While holding the microphone button, Derecho snapshots the growing WAV about
every three seconds and submits the complete available recording. It rebuilds
the unfinished WAV header and displays a replaceable partial transcript. There
is only one preview inference in flight. On release it reuses that transcript
only if the audio bytes match exactly; otherwise it performs a complete final
transcription. Gemma receives exactly one finalized transcript per turn.

This preserves final-context recognition instead of stitching possibly incorrect
words together. It is NOT word-by-word streaming or guaranteed faster. A final
pass and an in-flight preview can increase release latency and CPU usage. The
persistent server avoids repeated model loading; measure previews separately by
turning DERECHO_LIVE_STT off while leaving the server configured. Prefer the
server without previews if that wins on the Pi. Preview failures are visible;
final transcription still uses the configured server and surfaces its errors.

## Persistent Piper

```sh
export DERECHO_PIPER_PERSISTENT=1
export DERECHO_PIPER_PYTHON='/home/damian/Projects/piper-venv/bin/python'
```

A child process in the existing Piper environment keeps at most two voices
loaded and synthesizes the next WAV. Both old synthesize and new synthesize_wav
Python APIs are supported. If its startup/import fails, the backend logs a
warning and uses the original CLI. Inference errors are reported rather than
silently translated into success. Replay and volume use the existing playback
path. Voices are loaded on first use, so the first turn can still be slower.

These optional paths were tested with fake models, not the Pi's installed Piper
or Whisper versions. No measured hardware speedup is claimed.

## New language candidates

French, Brazilian Portuguese, and German are selectable with a Still testing
label. Their registry entries are enabled at the user's request, but none has
been validated on the Pi. Copy each ONNX and matching JSON into piper-voices
before using them. Then evaluate actual Whisper, Gemma, and Piper output on Pi.
The testing flag is separate from enabled, so the UI can expose a language without
claiming verified quality. Available downloads alone are not evidence of quality.
Existing English and Spanish remain enabled based on the working prototype.
