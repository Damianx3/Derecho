"""Select an ALSA USB endpoint by direction, independent of card number."""

import os
from pathlib import Path
import re
import subprocess


CARD_LINE = re.compile(r'^card (\d+):\s+(\w+)\s+\[.*?\],\s+device (\d+):', re.MULTILINE)


def is_usb_card(number):
    device = Path(f'/sys/class/sound/card{number}/device').resolve()
    return any((p / 'idVendor').is_file() and (p / 'idProduct').is_file()
               for p in (device, *device.parents))


def resolve_device(direction):
    command, setting, preferred = {
        'capture': ('arecord', 'DERECHO_MIC_DEVICE', 'Device'),
        'playback': ('aplay', 'DERECHO_SPEAKER_DEVICE', 'UACDemoV10'),
    }[direction]
    override = os.environ.get(setting, '').strip()
    if override:
        return override

    result = subprocess.run([command, '-l'], capture_output=True, text=True,
                            timeout=5, env={**os.environ, 'LC_ALL': 'C'})
    candidates = [(card, device) for number, card, device in CARD_LINE.findall(result.stdout)
                  if is_usb_card(number)]
    preferred_devices = [entry for entry in candidates if entry[0] == preferred]
    choices = preferred_devices or candidates
    if len(choices) == 1:
        card, device = choices[0]
        return f'plughw:CARD={card},DEV={device}'
    if not choices:
        raise RuntimeError(f'No USB {direction} device found. Check the connection and run {command} -l.')
    raise RuntimeError(f'Multiple USB {direction} devices found. Set {setting} to the intended ALSA endpoint.')
