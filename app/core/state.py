# app/core/state.py
from typing import List, Optional, TypedDict, Dict, Any
from langchain_core.documents import Document


class LearningState(TypedDict, total=False):
    # Selected checkpoint
    cp_key: str                      # was: checkpoint_id (renamed to avoid reserved name)
    checkpoint: Dict[str, Any]

    # RAG / context
    query: str
    gathered_context: List[Document]
    context_source: str            # "notes" or "web" or "mixed" or "none"
    context_relevance_score: float
    context_validation_feedback: str
    context_attempts: int

    # Debug / logs
    trace: List[str]
