# pylint: disable=missing-function-docstring, missing-module-docstring, unused-import, unused-argument, multiple-statements, broad-exception-caught

import math
import json
from pathlib import Path

# trail definitions: name, unlock score (0 = default), color_fn(frac, tick) -> (r,g,b)
# frac: 0=tail, 1=head   tick: pygame.time.get_ticks() for animated trails

def _default(frac, tick):
    return (int(160 + 95 * frac), int(100 * frac), 255)

def _fire(frac, tick):
    # tail=dark red, head=bright yellow-white
    r = int(255 * frac)
    g = int(140 * frac ** 1.6)
    b = int(20  * frac)
    return (min(255,r), min(255,g), b)

def _ice(frac, tick):
    # tail=dark blue, head=bright cyan-white
    r = int(80  * frac)
    g = int(180 * frac)
    b = 255
    return (r, g, b)

def _rainbow(frac, tick):
    # hue shifts based on position + time
    hue = (frac * 180 + tick * 0.12) % 360
    h   = hue / 60
    x   = 1 - abs(h % 2 - 1)
    if   h < 1: r,g,b = 1,  x,  0
    elif h < 2: r,g,b = x,  1,  0
    elif h < 3: r,g,b = 0,  1,  x
    elif h < 4: r,g,b = 0,  x,  1
    elif h < 5: r,g,b = x,  0,  1
    else:       r,g,b = 1,  0,  x
    return (int(r*255), int(g*255), int(b*255))

def _gold(frac, tick):
    # tail=dark brown, head=bright gold
    r = int(220 * frac)
    g = int(160 * frac ** 1.2)
    b = int(10  * frac)
    return (min(255,r), min(255,g), b)

def _ghost_trail(frac, tick):
    # pale white-lavender for ghost mode feel
    v = int(180 * frac)
    return (v, v, min(255, v + 60))

TRAIL_DEFS = [
    {"id": "default",  "name": "Default",  "unlock": 0,   "fn": _default},
    {"id": "fire",     "name": "Fire",     "unlock": 15,  "fn": _fire},
    {"id": "ice",      "name": "Ice",      "unlock": 30,  "fn": _ice},
    {"id": "rainbow",  "name": "Rainbow",  "unlock": 50,  "fn": _rainbow},
    {"id": "gold",     "name": "Gold",     "unlock": 75,  "fn": _gold},
    {"id": "ghost",    "name": "Ghost",    "unlock": 100, "fn": _ghost_trail},
]

TRAIL_FILE = Path(__file__).resolve().parent / "trails.json"

def _load_save() -> dict:
    if TRAIL_FILE.exists():
        try:
            return json.loads(TRAIL_FILE.read_text())
        except Exception:
            pass
    return {"active": "default", "unlocked": ["default"]}

def _save_save(data: dict):
    TRAIL_FILE.write_text(json.dumps(data, indent=2))

def get_unlocked() -> list:
    return _load_save().get("unlocked", ["default"])

def get_active() -> str:
    return _load_save().get("active", "default")

def set_active(trail_id: str):
    data = _load_save()
    data["active"] = trail_id
    _save_save(data)

def check_and_unlock(score: int) -> list:
    """Unlock any trails the score qualifies for. Returns list of newly unlocked trail names."""
    data     = _load_save()
    unlocked = set(data.get("unlocked", ["default"]))
    newly    = []
    for td in TRAIL_DEFS:
        if td["id"] not in unlocked and score >= td["unlock"]:
            unlocked.add(td["id"])
            newly.append(td["name"])
    if newly:
        data["unlocked"] = list(unlocked)
        _save_save(data)
    return newly

def get_color_fn(trail_id: str):
    for td in TRAIL_DEFS:
        if td["id"] == trail_id:
            return td["fn"]
    return _default

def trail_alpha(frac: float) -> int:
    return int(155 * frac ** 2)
