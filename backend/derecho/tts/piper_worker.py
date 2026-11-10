"""Run inside the existing Piper virtualenv; reuse up to two loaded voices."""
from collections import OrderedDict
from contextlib import redirect_stdout
import json
import sys
import wave

def synthesize(voices, voice_class, model, text, output):
    if model in voices:
        voice = voices.pop(model)
    else:
        if len(voices) >= 2:
            voices.popitem(last=False)
        voice = voice_class.load(model)
    voices[model] = voice
    with wave.open(output, "wb") as writer:
        if hasattr(voice, "synthesize_wav"):
            voice.synthesize_wav(text, writer)
        else:
            voice.synthesize(text, writer)  # Older Piper Python API.

def main():
    try:
        with redirect_stdout(sys.stderr):
            from piper.voice import PiperVoice
    except Exception as error:
        print(json.dumps({"ready": False, "error": str(error)}), flush=True)
        return
    print(json.dumps({"ready": True}), flush=True)
    voices = OrderedDict()
    for line in sys.stdin:
        try:
            request = json.loads(line)
            with redirect_stdout(sys.stderr):
                synthesize(voices, PiperVoice, request["model"], request["text"], request["output"])
            print(json.dumps({"ok": True}), flush=True)
        except Exception as error:
            print(json.dumps({"ok": False, "error": str(error)}), flush=True)

if __name__ == "__main__":
    main()
