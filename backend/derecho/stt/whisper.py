import threading

import numpy
import sherpa_onnx
import sounddevice as sd
from pynput import keyboard
from pathlib import Path
                                                                                                                                                                                                                                                                            
MODELS = Path(__file__).resolve().parent / "models"
WHISPER_DIR = MODELS / "sherpa-onnx-whisper-tiny"

recognizer = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=str(WHISPER_DIR / "tiny-encoder.onnx"),
    decoder=str(WHISPER_DIR / "tiny-decoder.onnx"),
    tokens=str(WHISPER_DIR / "tiny-tokens.txt"),
    language="",
)

fs = 16000
frame_duration_ms = 30
frame_samples = int(fs * frame_duration_ms / 1000)
min_frames = 10          # ignore taps shorter than ~0.3 s

PTT_KEY = keyboard.Key.space   # change to physical button later

recording = threading.Event()   # set while the key is held
quit_flag = threading.Event()


def on_press(key):
    if key == PTT_KEY and not recording.is_set():   # ignore key auto-repeat
        recording.set()
        print("Recording...")


def on_release(key):
    if key == PTT_KEY:
        recording.clear()
    elif key == keyboard.Key.esc:
        quit_flag.set()
        return False    # stops the listener


def transcribe(buffer):
    joined = b"".join(buffer)
    int16_array = numpy.frombuffer(joined, dtype=numpy.int16)
    audio_float = int16_array.astype(numpy.float32) / 32768.0
    recon_stream = recognizer.create_stream()
    recon_stream.accept_waveform(fs, audio_float)
    recognizer.decode_stream(recon_stream)
    print("Text:", recon_stream.result.text)
    print("Language:", recon_stream.result.lang)


listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

print("Hold SPACE to talk, release to transcribe.")

buffer = []
mic_stream = sd.RawInputStream(samplerate=fs, channels=1, dtype="int16")
mic_stream.start()
try:
    while not quit_flag.is_set():
        # Always read so the stream never backs up with stale audio
        frame_bytes, overflowed = mic_stream.read(frame_samples)

        if recording.is_set():
            buffer.append(bytes(frame_bytes))
        elif buffer:
            # Key was just released
            if len(buffer) >= min_frames:
                print("Transcribing...")
                transcribe(buffer)
            else:
                print("Too short, ignored.")
            buffer = []
except KeyboardInterrupt:
    pass
finally:
    print("\nStopping...")
    mic_stream.stop()
    mic_stream.close()
    listener.stop()