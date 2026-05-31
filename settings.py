# pylint: disable=missing-function-docstring, missing-module-docstring, broad-exception-caught

import json
from pathlib import Path

SETTINGS_FILE = Path(__file__).resolve().parent / "settings.json"

PLAYER_COLORS = [
    {"name": "White",   "color": (255, 255, 255)},
    {"name": "Cyan",    "color": (0,   240, 255)},
    {"name": "Green",   "color": (40,  230, 100)},
    {"name": "Yellow",  "color": (255, 210, 30)},
    {"name": "Orange",  "color": (255, 140, 20)},
    {"name": "Pink",    "color": (255, 60,  180)},
    {"name": "Red",     "color": (255, 55,  55)},
    {"name": "Purple",  "color": (180, 60,  255)},
]

DEFAULTS = {
    "fullscreen":    True,
    "player_color":  0,      # index into PLAYER_COLORS
    "sfx_volume":    0.7,
    "music_volume":  0.45,
}

def load() -> dict:
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text())
            # fill missing keys with defaults
            for k, v in DEFAULTS.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(DEFAULTS)

def save(data: dict):
    SETTINGS_FILE.write_text(json.dumps(data, indent=2))

def get_player_color() -> tuple:
    idx = load().get("player_color", 0)
    return PLAYER_COLORS[idx % len(PLAYER_COLORS)]["color"]
