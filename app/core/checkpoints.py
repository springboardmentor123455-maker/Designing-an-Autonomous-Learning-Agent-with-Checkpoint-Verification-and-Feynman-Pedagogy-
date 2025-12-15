# app/core/checkpoints.py
import json
from pathlib import Path
from typing import Dict, Any, List

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CHECKPOINTS_PATH = DATA_DIR / "checkpoints.json"


def load_checkpoints() -> Dict[str, Any]:
    with open(CHECKPOINTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def list_checkpoint_ids() -> List[str]:
    data = load_checkpoints()
    return [cp["id"] for cp in data["checkpoints"]]


def get_checkpoint_by_id(cp_id: str) -> Dict[str, Any]:
    data = load_checkpoints()
    for cp in data["checkpoints"]:
        if cp["id"] == cp_id:
            return cp
    raise ValueError(f"Checkpoint with id={cp_id} not found.")
