# storage.py
import json, os
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

HISTORY_FILE = DATA_DIR / "history.json"
BASELINE_FILE = DATA_DIR / "baseline.json"

def load_history() -> list:
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return []

def save_entry(entry: dict):
    history = load_history()
    # One entry per day — replace if same date
    today = entry["date"][:10]
    history = [h for h in history if h["date"][:10] != today]
    history.append(entry)
    HISTORY_FILE.write_text(json.dumps(history[-90:], indent=2))  # keep 90 days

def load_baseline() -> dict | None:
    if BASELINE_FILE.exists():
        return json.loads(BASELINE_FILE.read_text())
    return None

def save_baseline(baseline: dict):
    BASELINE_FILE.write_text(json.dumps(baseline, indent=2))

def reset_all():
    for f in [HISTORY_FILE, BASELINE_FILE]:
        if f.exists():
            f.unlink()