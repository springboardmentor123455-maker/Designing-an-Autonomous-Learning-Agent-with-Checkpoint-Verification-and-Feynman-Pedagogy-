from typing import TypedDict, List
import numpy as np
from checkpoints import Checkpoint


class AgentState(TypedDict, total=False):
    
    selected_cp_id: str
    checkpoint: Checkpoint
    user_notes: str
    context: str
    relevance_score: float
    attempts: int
    chunks: List[str]
    embeddings: np.ndarray
    questions: List[str]
    answers: List[str]
    per_question_scores: List[int]
    knowledge_gaps: List[str]
    score_percent: float
    question_relevance: List[str]
    relevant_question_count: int
    feynman_explanation: str
    decision: str
    learning_path: List[str]
    current_checkpoint_index: int
    completed_checkpoints: List[str]
