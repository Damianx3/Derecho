from pathlib import Path
import signal
import subprocess
import wave

from derecho.audio.devices import resolve_device

MAX_RECORDING_SECONDS = 60
_recording_process = None
_recording_path = None


def start_recording(
    output_path: str = "~/derecho-live-test.wav",
) -> str:
    """Start recording audio and keep recording until stop_recording() is called."""

    global _recording_process
    global _recording_path

    if _recording_process is not None:
        if _recording_process.poll() is None:
            raise RuntimeError("A recording is already in progress.")
        _recording_process, _recording_path = None, None

    path = Path(output_path).expanduser()
    device = resolve_device('capture')

    command = [
        "arecord",
        "-D",
        device,
        "-f",
        "S16_LE",
        "-r",
        "16000",
        "-c",
        "1",
        "-d",
        str(MAX_RECORDING_SECONDS),
        str(path),
    ]

    # Invalidate the last turn before spawning: an open failure may leave it untouched.
    path.write_bytes(b'')
    process = subprocess.Popen(command)
    try:
        status = process.wait(timeout=0.2)
    except subprocess.TimeoutExpired:
        _recording_process, _recording_path = process, path
    else:
        raise RuntimeError(f'Microphone recording failed on {device} (arecord exit {status}).')

    return str(_recording_path)


def stop_recording() -> str:
    """Stop the current recording and return its WAV file path."""

    global _recording_process
    global _recording_path

    if _recording_process is None:
        raise RuntimeError("No recording is currently in progress.")

    process, path = _recording_process, _recording_path
    try:
        if process.poll() is not None:
            raise RuntimeError('Microphone recording ended before release.')
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise RuntimeError('Microphone recording did not stop in time.')
        try:
            with wave.open(str(path), 'rb') as recording:
                if recording.readframes(1):
                    return str(path)
        except (wave.Error, EOFError):
            pass
        raise RuntimeError('Microphone recording produced no usable audio.')
    finally:
        _recording_process, _recording_path = None, None


def record_audio(
    output_path: str,
    duration: int = 5,
) -> str:
    """Record for a fixed duration. Kept for command-line testing."""

    output_file = Path(output_path).expanduser()

    subprocess.run(
        [
            "arecord",
            "-D",
            resolve_device('capture'),
            "-f",
            "S16_LE",
            "-r",
            "16000",
            "-c",
            "1",
            "-d",
            str(duration),
            str(output_file),
        ],
        check=True,
    )

    return str(output_file)
