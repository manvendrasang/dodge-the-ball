# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import
# pylint: disable=missing-class-docstring, no-member, broad-exception-caught, unspecified-encoding

import json
from datetime import datetime
from pathlib import Path
from constants import MODES

SCORE_FILE  = Path(__file__).resolve().parent / "scores.json"
MAX_ENTRIES = 10

def _load() -> dict:
    if SCORE_FILE.exists():
        try:
            return json.loads(SCORE_FILE.read_text())
        except Exception:
            pass
    return {m: [] for m in MODES}

def _save(data: dict):
    SCORE_FILE.write_text(json.dumps(data, indent=2))

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

def get_scores(mode: str) -> list:
    return _load().get(mode, [])

def get_personal_best(mode: str) -> int:
    entries = get_scores(mode)
    if not entries:
        return 0
    first = entries[0]
    return first[0] if isinstance(first, (list, tuple)) else first
