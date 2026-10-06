from pathlib import Path
import signal
import subprocess


MIC_DEVICE = "plughw:2,0"

_recording_process = None
_recording_path = None


def start_recording(
    output_path: str = "~/derecho-live-test.wav",
) -> str:
    """Start recording audio and keep recording until stop_recording() is called."""

    global _recording_process
    global _recording_path

    if _recording_process is not None:
        raise RuntimeError("A recording is already in progress.")

    _recording_path = Path(output_path).expanduser()

    command = [
        "arecord",
        "-D",
        MIC_DEVICE,
        "-f",
        "S16_LE",
        "-r",
        "16000",
        "-c",
        "1",
        str(_recording_path),
    ]

    _recording_process = subprocess.Popen(command)

    return str(_recording_path)


def stop_recording() -> str:
    """Stop the current recording and return its WAV file path."""

    global _recording_process
    global _recording_path

    if _recording_process is None:
        raise RuntimeError("No recording is currently in progress.")

    _recording_process.send_signal(signal.SIGINT)
    _recording_process.wait(timeout=5)

    _recording_process = None

    return str(_recording_path)


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
            MIC_DEVICE,
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
