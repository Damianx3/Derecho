# How Derecho Translation Mode works

## A short explanation you can say aloud

Derecho is a local push-to-talk translator. React handles the touchscreen,
FastAPI coordinates the work, ALSA records microphone audio, Whisper recognizes
the source speech, Gemma translates the text, and Piper produces speech in the
target language. No cloud service is needed during normal operation.

## Follow one turn

1. The UI loads /api/languages. languages.py contains the names, Whisper codes,
   Piper filenames, and enablement flags, so frontend/backend mappings agree.
2. Pressing Hold to Speak sends /api/record/start with the selected speaker's
   source-language code. recorder.py starts arecord: mono, 16 kHz, 16-bit PCM WAV.
   This is the format the recognition stage expects.
3. If the optional live path is enabled, live_transcription.py reads snapshots
   of the growing WAV. A background thread sends them to local whisper-server.
   App.jsx polls /api/record/status once a second for replaceable preview text.
4. Releasing sends /api/record/stop. Recording stops and the WAV is finalized.
   If the preview recognized exactly those audio bytes, its result is reused.
   Otherwise Whisper recognizes the complete recording again for context.
5. translator_pipeline.py sends exactly one final transcript to Gemma on
   loopback port 9379. The prompt requests only translation and preservation of
   names, numbers, and negation. It tells Gemma to translate a question rather
   than answer it. This is a prompt instruction, not a correctness guarantee.
6. Piper selects the target-language voice and creates derecho-tts.wav. Its
   optional worker lives in the existing Piper virtualenv and keeps two voices
   loaded, avoiding repeated loading on subsequent turns. It uses the same Piper
   models; the older CLI remains the default/fallback path.
7. piper_client.py scales a temporary copy of the WAV by volume/100, then uses
   the original aplay WAV-file command. Mute skips playback. The original WAV
   stays intact. Replay skips recognition, translation, and synthesis.
8. After playback finishes, the API returns transcript, translation, timings,
   and audio state. React adds the conversation bubbles. Take Turn reverses the
   source/target roles; Speak Again keeps the same speaker; Done clears UI history.

## Why the code is separated

App.jsx controls screens and touch events. api.py defines the HTTP contract.
recorder.py owns the microphone process. whisper_client.py talks to Whisper.
live_transcription.py manages previews and their finalization. gemma_client.py
owns translation requests. piper_worker.py owns voice caching; piper_client.py
owns synthesis requests, volume, and playback. translator_pipeline.py joins
the stages and measures them. languages.py is the shared language registry.

## Questions a reviewer might ask

**Is this word-by-word real-time translation?** No. It is push-to-talk with an
optional rolling transcript. Whisper processes audio windows and can revise
earlier words. Translation runs once after release on finalized text.

**Does live transcription definitely make it faster?** No. Warm models avoid
reload costs, but repeated previews and a final pass consume CPU. Compare
release-to-result latency with previews on/off on the actual Pi.

**Why not use a bigger Whisper model immediately?** Recognition quality and
latency trade off. Tiny remains the default; an environment setting selects an
installed multilingual base model for a measured comparison. No faster/better
hardware result has been established yet.

**Why final-pass transcription?** It protects trailing words and sentence
context. A SHA-256 fingerprint compares exact recorded PCM bytes; it is an
identity check for cache reuse, not an accuracy or confidence score.

**What is the worker/thread difference?** Live recognition uses a background
thread for I/O while FastAPI serves status requests. Piper's worker is a child
process in another virtualenv, allowing reuse of its already installed packages
and loaded voice models. Both operate locally.

**How is volume implemented?** Software attenuation of signed PCM samples in a temporary WAV before aplay.
It controls Derecho speech, not the system mixer. Changes apply to the next
playback; they do not change a sentence already playing.

**Are all listed languages supported?** English/Spanish were the reported working
prototype. French/Portuguese/German are selectable with a Still testing label. Their
transcription, translation, and speech playback still need validation on Pi.

**What was tested?** Frontend compilation, UI with sample responses, and automated
tests with generated WAVs and fake model responses. Actual Pi latency, installed
model compatibility, dialect quality, and physical touch behavior still need tests.

**Does offline mean no audio remains on disk?** No. Current input/output WAVs
remain locally. Done clears UI history; audio deletion is still separate work.

## Interface language versus speech languages

The home selector chooses uiLanguage, which changes buttons, headings, status
messages, accessibility labels, and known error messages immediately. English is
the default. i18n.mjs contains all five UI translations; no model or network is
needed to translate the interface. document.lang changes for accessibility.

The two speaker selectors remain separate. Changing the interface to French
does not silently change English-to-Spanish translation. Transcripts and model
translations stay in their original languages. The brand name Derecho remains
the same. Native language names in the home menu help users find their language.
