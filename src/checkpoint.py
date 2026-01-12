from dataclasses import dataclass

@dataclass
class Checkpoint:
    id: int
    title: str
    objective: str
    success_threshold: float = 0.7
