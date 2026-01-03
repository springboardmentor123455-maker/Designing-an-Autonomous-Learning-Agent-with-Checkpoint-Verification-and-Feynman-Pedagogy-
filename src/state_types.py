from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict, total=False):
    # Which checkpoint are we on?
    cp_id: int
    checkpoint: Dict[str, Any]

    # User-provided notes
    user_notes: Optional[str]

    # Raw gathered context (notes + web)
    raw_context: str
    context_docs: List[str]

    # Relevance info for Milestone 1
    context_relevance_score: float       # 1.0–5.0
    context_relevance_ratio: float       # 0.0–1.0 (match ratio)
    context_retries: int                 # how many times we re-fetched

    # Vectorization (used in Milestone 2)
    vector_store: Any

    # Questions & answers (Milestone 2)
    questions: List[Dict[str, str]]
    learner_answers: List[str]
    score: float

    # Overall status of the checkpoint
    status: str
