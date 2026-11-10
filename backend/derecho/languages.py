"""Shared language registry. New languages are selectable with an explicit testing label."""
from pathlib import Path
import os

VOICE_DIR = Path(os.environ.get("DERECHO_VOICE_DIR", str(Path.home() / "Projects/piper-voices"))).expanduser()
LANGUAGES = {
    "English": {"code": "en", "display_name": "English", "voice": "en_US-lessac-medium.onnx", "enabled": True},
    "Spanish": {"code": "es", "display_name": "Español", "voice": "es_ES-davefx-medium.onnx", "enabled": True},
    "French": {"code": "fr", "display_name": "Français", "voice": "fr_FR-siwis-medium.onnx", "enabled": True, "testing": True},
    "Portuguese": {"code": "pt", "display_name": "Português (Brasil)", "voice": "pt_BR-faber-medium.onnx", "enabled": True, "testing": True},
    "German": {"code": "de", "display_name": "Deutsch", "voice": "de_DE-thorsten-medium.onnx", "enabled": True, "testing": True},
}

def get_language(name):
    if name not in LANGUAGES:
        raise ValueError(f"Unsupported language: {name}")
    if not LANGUAGES[name]["enabled"]:
        raise ValueError(f"{name} needs Pi validation before it can be enabled")
    return LANGUAGES[name]

def public_languages():
    return [{"name": name, "code": item["code"], "display_name": item["display_name"],
             "enabled": item["enabled"], "testing": item.get("testing", False)} for name, item in LANGUAGES.items()]
