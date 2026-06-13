# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import
# pylint: disable=missing-class-docstring, no-member, broad-exception-caught, unspecified-encoding

import json
from datetime import datetime, date
from pathlib import Path
from constants import MODES

SCORE_FILE  = Path(__file__).resolve().parent / "scores.json"
MAX_ENTRIES = 10
MAX_DAILY   = 5

def _load() -> dict:
    if SCORE_FILE.exists():
        try:
            return json.loads(SCORE_FILE.read_text())
        except Exception:
            pass
    return {m: [] for m in MODES}

def _save(data: dict):
    SCORE_FILE.write_text(json.dumps(data, indent=2))

def _today() -> str:
    return date.today().isoformat()  # YYYY-MM-DD

def submit_score(mode: str, score: int):
    data = _load()
    if mode not in data:
        data[mode] = []
    ts = datetime.now().strftime("%d %b %Y  %H:%M")
    data[mode].append([score, ts])
    # sort by score descending, keep top N
    data[mode].sort(key=lambda e: e[0] if isinstance(e, (list,tuple)) else e, reverse=True)
    data[mode] = data[mode][:MAX_ENTRIES]
    _save(data)
    _submit_daily(data, mode, score, ts)

def _submit_daily(data: dict, mode: str, score: int, ts: str):
    """Track today's best scores per mode under data['daily'][YYYY-MM-DD][mode]."""
    today = _today()
    daily = data.setdefault("daily", {})
    # prune old days — keep only today
    for old_day in list(daily.keys()):
        if old_day != today:
            del daily[old_day]
    day_entry = daily.setdefault(today, {})
    mode_list = day_entry.setdefault(mode, [])
    mode_list.append([score, ts])
    mode_list.sort(key=lambda e: e[0], reverse=True)
    day_entry[mode] = mode_list[:MAX_DAILY]
    _save(data)

def get_scores(mode: str) -> list:
    return _load().get(mode, [])

def get_daily_scores(mode: str) -> list:
    """Return today's top scores for the given mode, empty if none yet."""
    data  = _load()
    today = _today()
    return data.get("daily", {}).get(today, {}).get(mode, [])

def get_personal_best(mode: str) -> int:
    entries = get_scores(mode)
    if not entries:
        return 0
    first = entries[0]
    return first[0] if isinstance(first, (list, tuple)) else first
