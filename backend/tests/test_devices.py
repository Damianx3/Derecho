from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from subprocess import CompletedProcess, TimeoutExpired

from derecho.audio import devices, recorder


class DeviceTests(unittest.TestCase):
    def test_expired_recording_can_be_replaced_with_bounded_capture(self):
        with TemporaryDirectory() as folder, \
                patch.object(recorder, '_recording_process') as expired, \
                patch.object(recorder, '_recording_path', None), \
                patch.object(recorder, 'resolve_device', return_value='plughw:CARD=Device,DEV=0'), \
                patch.object(recorder.subprocess, 'Popen') as spawn:
            expired.poll.return_value = 0
            spawn.return_value.wait.side_effect = TimeoutExpired('arecord', 0.2)
            path = str(Path(folder) / 'next.wav')
            self.assertEqual(recorder.start_recording(path), path)
            command = spawn.call_args.args[0]
            self.assertEqual(command[command.index('-d') + 1], '60')
            self.assertIs(recorder._recording_process, spawn.return_value)

    def test_preferred_usb_speaker_ignores_hdmi_and_card_number(self):
        for number in ('2', '7'):
            listing = (f'card {number}: UACDemoV10 [USB Audio], device 0: USB Audio\n'
                       'card 0: HDMI [HDMI], device 0: HDMI\n')
            with patch.dict(devices.os.environ, {}, clear=True), \
                    patch.object(devices, 'is_usb_card', side_effect=lambda n: n == number), \
                    patch.object(devices.subprocess, 'run', return_value=CompletedProcess([], 0, listing, '')) as run:
                self.assertEqual(devices.resolve_device('playback'), 'plughw:CARD=UACDemoV10,DEV=0')
                self.assertEqual(run.call_args.args[0], ['aplay', '-l'])

    def test_unique_replacement_capture_device(self):
        listing = 'card 5: Headset [USB Headset], device 1: USB Audio\n'
        with patch.dict(devices.os.environ, {}, clear=True), patch.object(devices, 'is_usb_card', return_value=True), \
                patch.object(devices.subprocess, 'run', return_value=CompletedProcess([], 0, listing, '')):
            self.assertEqual(devices.resolve_device('capture'), 'plughw:CARD=Headset,DEV=1')

    def test_missing_or_ambiguous_usb_capture_does_not_guess(self):
        for listing, message in [('', 'No USB capture'), (
            'card 2: Headset [USB], device 0: USB\ncard 3: Mic [USB], device 0: USB\n', 'Multiple USB capture')]:
            with patch.dict(devices.os.environ, {}, clear=True), patch.object(devices, 'is_usb_card', return_value=True), \
                    patch.object(devices.subprocess, 'run', return_value=CompletedProcess([], 0, listing, '')):
                with self.assertRaisesRegex(RuntimeError, message):
                    devices.resolve_device('capture')

    def test_failed_recorder_invalidates_previous_audio(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'recording.wav'
            path.write_bytes(b'old recording')
            with patch.object(recorder, 'resolve_device', return_value='plughw:CARD=Device,DEV=0'), \
                    patch.object(recorder.subprocess, 'Popen') as spawn:
                spawn.return_value.wait.return_value = 1
                with self.assertRaisesRegex(RuntimeError, 'Microphone recording failed'):
                    recorder.start_recording(str(path))
                self.assertEqual(path.read_bytes(), b'')
                with self.assertRaisesRegex(RuntimeError, 'No recording'):
                    recorder.stop_recording()
