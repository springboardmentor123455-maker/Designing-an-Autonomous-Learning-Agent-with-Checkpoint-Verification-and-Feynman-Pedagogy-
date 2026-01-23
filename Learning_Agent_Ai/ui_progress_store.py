import json
from pathlib import Path


class ProgressStore:
    """
    File-based persistence for learner progress.
    """

    def __init__(self, file_path: str = "progress.json"):
        self.file = Path(file_path)
        self.file.parent.mkdir(parents=True, exist_ok=True)

    def save(self, user_id: str, checkpoint_index: int) -> None:
        """
        Save learner progress.
        """
        data = {
            "user_id": user_id,
            "checkpoint": checkpoint_index
        }

        with self.file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self):
        """
        Load learner progress.

        Returns:
            dict | None
        """
        if not self.file.exists():
            return None

        try:
            with self.file.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
