# pylint: disable=missing-module-docstring, missing-function-docstring, broad-exception-caught

import json
from pathlib import Path

ACHIEVEMENTS_FILE = Path(__file__).resolve().parent / "achievements.json"

# Each achievement: id, name, description, icon (emoji), condition_fn(stats, mode) -> bool
# condition_fn receives the stats dict + mode string from the session
ACHIEVEMENTS = [
    # general milestones
    {
        "id": "first_blood",
        "name": "First Blood",
        "desc": "Play your first game",
        "icon": "🩸",
        "modes": ["classic", "shrink", "hardcore"],
        "fn": lambda s, m: True,
    },
    {
        "id": "survivor_25",
        "name": "Survivor I",
        "desc": "Reach a score of 25",
        "icon": "🛡",
        "modes": ["classic", "shrink", "hardcore"],
        "fn": lambda s, m: s.get("score", 0) >= 25,
    },
    {
        "id": "survivor_50",
        "name": "Survivor II",
        "desc": "Reach a score of 50",
        "icon": "⚔",
        "modes": ["classic", "shrink", "hardcore"],
        "fn": lambda s, m: s.get("score", 0) >= 50,
    },
    {
        "id": "survivor_100",
        "name": "Century",
        "desc": "Reach a score of 100",
        "icon": "💯",
        "modes": ["classic", "shrink", "hardcore"],
        "fn": lambda s, m: s.get("score", 0) >= 100,
    },
    {
        "id": "untouchable",
        "name": "Untouchable",
        "desc": "Score 20+ without collecting any powerup",
        "icon": "👻",
        "modes": ["shrink", "hardcore"],
        "fn": lambda s, m: s.get("score", 0) >= 20 and s.get("powerups", 0) == 0,
    },
    {
        "id": "speedrun",
        "name": "Speedrunner",
        "desc": "Score 15 in under 20 seconds",
        "icon": "⚡",
        "modes": ["classic", "shrink", "hardcore"],
        "fn": lambda s, m: s.get("score", 0) >= 15 and s.get("time_s", 999) < 20,
    },
    {
        "id": "combo_king",
        "name": "Combo King",
        "desc": "Reach max combo in any mode",
        "icon": "🔥",
        "modes": ["classic", "shrink", "hardcore"],
        "fn": lambda s, m: (
            (m == "classic"  and s.get("peak_combo", 0) >= 4) or
            (m == "shrink"   and s.get("peak_combo", 0) >= 6) or
            (m == "hardcore" and s.get("peak_combo", 0) >= 8)
        ),
    },
    {
        "id": "long_haul",
        "name": "Long Haul",
        "desc": "Survive for 3 minutes",
        "icon": "⏱",
        "modes": ["classic", "shrink", "hardcore"],
        "fn": lambda s, m: s.get("time_s", 0) >= 180,
    },
    {
        "id": "level_10",
        "name": "Veteran",
        "desc": "Reach Level 10",
        "icon": "🎖",
        "modes": ["classic", "shrink", "hardcore"],
        "fn": lambda s, m: s.get("level", 1) >= 10,
    },
    {
        "id": "level_20",
        "name": "Elite",
        "desc": "Reach Level 20",
        "icon": "🏆",
        "modes": ["classic", "shrink", "hardcore"],
        "fn": lambda s, m: s.get("level", 1) >= 20,
    },
    # classic specific
    {
        "id": "classic_master",
        "name": "Classic Master",
        "desc": "Score 75 in Classic mode",
        "icon": "🥇",
        "modes": ["classic"],
        "fn": lambda s, m: m == "classic" and s.get("score", 0) >= 75,
    },
    # shrink specific
    {
        "id": "shrinker",
        "name": "Shrinker",
        "desc": "Survive 5 zone shrinks",
        "icon": "🌀",
        "modes": ["shrink"],
        "fn": lambda s, m: m == "shrink" and s.get("shrinks", 0) >= 5,
    },
    {
        "id": "powerup_hoarder",
        "name": "Powerup Hoarder",
        "desc": "Collect 10 powerups in one game",
        "icon": "✨",
        "modes": ["shrink", "hardcore"],
        "fn": lambda s, m: s.get("powerups", 0) >= 10,
    },
    # hardcore specific
    {
        "id": "wall_dodger",
        "name": "Wall Dodger",
        "desc": "Survive 10 walls in Hardcore",
        "icon": "🧱",
        "modes": ["hardcore"],
        "fn": lambda s, m: m == "hardcore" and s.get("walls", 0) >= 10,
    },
    {
        "id": "hardcore_survivor",
        "name": "Hardcore Survivor",
        "desc": "Score 30 in Hardcore mode",
        "icon": "💀",
        "modes": ["hardcore"],
        "fn": lambda s, m: m == "hardcore" and s.get("score", 0) >= 30,
    },
    {
        "id": "second_chance",
        "name": "Second Chance",
        "desc": "Use your extra life in Hardcore",
        "icon": "❤",
        "modes": ["hardcore"],
        "fn": lambda s, m: m == "hardcore" and s.get("used_extra_life", False),
    },
    # dodging feats
    {
        "id": "matrix",
        "name": "The Matrix",
        "desc": "Dodge 10,000 ball-frames in one game",
        "icon": "🕶",
        "modes": ["classic", "shrink", "hardcore"],
        "fn": lambda s, m: s.get("balls_dodged", 0) >= 10000,
    },
]

# lookup by id
_BY_ID = {a["id"]: a for a in ACHIEVEMENTS}

def _load() -> dict:
    if ACHIEVEMENTS_FILE.exists():
        try:
            return json.loads(ACHIEVEMENTS_FILE.read_text())
        except Exception:
            pass
    return {"unlocked": []}

def _save(data: dict):
    ACHIEVEMENTS_FILE.write_text(json.dumps(data, indent=2))

def get_unlocked() -> set:
    return set(_load().get("unlocked", []))

def check_and_unlock(stats: dict, mode: str) -> list:
    """
    Evaluate all achievements against session stats.
    Returns list of newly unlocked achievement dicts.
    """
    data     = _load()
    unlocked = set(data.get("unlocked", []))
    newly    = []
    for ach in ACHIEVEMENTS:
        if ach["id"] in unlocked:
            continue
        if mode not in ach["modes"]:
            continue
        try:
            if ach["fn"](stats, mode):
                unlocked.add(ach["id"])
                newly.append(ach)
        except Exception:
            pass
    if newly:
        data["unlocked"] = list(unlocked)
        _save(data)
    return newly

def get_all_for_display() -> list:
    """Return all achievements with unlocked status for leaderboard/display."""
    unlocked = get_unlocked()
    return [{"unlocked": a["id"] in unlocked, **a} for a in ACHIEVEMENTS]
