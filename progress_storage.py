import json
from datetime import datetime
from pathlib import Path

PROGRESS_FILE = Path("student_progress.json")

def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return []

def save_progress(data):
    progress = load_progress()
    progress.append(data)
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2))
