from typing import List, TypedDict


class Checkpoint(TypedDict):
    id : str
    topic: str
    objectives: List[str]
    success_criteria: str
