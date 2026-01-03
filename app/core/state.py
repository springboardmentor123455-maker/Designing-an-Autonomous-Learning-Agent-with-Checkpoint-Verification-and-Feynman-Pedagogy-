from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class LearningCheckpoint:
    id: str
    title: str
    goals: List[str]
    pass_score: float = 0.7


@dataclass
class LearningState:
    active_checkpoint: Optional[LearningCheckpoint] = None
    context: Optional[str] = None
    vector_index: Optional[object] = None

    questions: List[str] = field(default_factory=list)
    responses: Dict[int, str] = field(default_factory=dict)

    score: float = 0.0
    weak_topics: List[str] = field(default_factory=list)

    completed: List[str] = field(default_factory=list)
    flow_state: str = "select"   # select → study → quiz → feynman → result
