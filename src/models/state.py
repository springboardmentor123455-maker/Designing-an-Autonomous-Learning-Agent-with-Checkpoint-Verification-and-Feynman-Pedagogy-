"""LangGraph state definition for the learning workflow."""
from typing import List, Optional, TypedDict, Annotated, Dict, Any
import operator
from src.models.checkpoint import Checkpoint, GatheredContext


class LearningState(TypedDict):
    """
    State object for the LangGraph learning workflow (Milestones 1-4).
    
    This state is passed between nodes in the graph and maintains
    all information about the current learning session.
    """
    # All checkpoints in the learning path (Milestone 4)
    all_checkpoints: List[Checkpoint]
    
    # Index of current checkpoint being worked on (Milestone 4)
    current_checkpoint_index: int
    
    # Current checkpoint being worked on
    checkpoint: Optional[Checkpoint]
    
    # Completed checkpoint indices (Milestone 4)
    completed_checkpoints: Annotated[List[int], operator.add]
    
    # User-provided notes/materials
    user_notes: Optional[str]
    
    # Gathered context from various sources
    gathered_contexts: Annotated[List[GatheredContext], operator.add]
    
    # Whether gathered context is valid/relevant
    context_valid: bool
    
    # Context validation message
    validation_message: Optional[str]
    
    # Number of context gathering retries
    retry_count: int
    
    # Error messages
    error: Optional[str]
    
    # Current stage in the workflow
    current_stage: str
    
    # Workflow messages/logs
    messages: Annotated[List[str], operator.add]
    
    # --- Milestone 2 additions ---
    
    # Processed context chunks
    context_chunks: List[str]
    
    # Vector store for embeddings (temporary session storage)
    vector_store: Optional[Any]
    
    # Generated questions for assessment
    questions: List[Dict[str, Any]]
    
    # Learner answers to questions
    answers: List[Dict[str, Any]]
    
    # Understanding verification score (0-100)
    understanding_score: Optional[float]
    
    # Whether learner passed (>= 70%)
    passed_checkpoint: bool
    
    # --- Milestone 3 additions ---
    
    # Weak concepts that need Feynman teaching
    weak_concepts: List[str]
    
    # Feynman explanations generated
    feynman_explanations: List[Dict[str, Any]]
    
    # Number of times Feynman teaching has been applied
    feynman_attempts: int
    
    # Maximum Feynman teaching attempts allowed
    max_feynman_attempts: int


def create_initial_state(
    checkpoints: List[Checkpoint],
    user_notes: Optional[str] = None
) -> LearningState:
    """
    Create an initial state for the learning workflow (Milestones 1-4).
    
    Args:
        checkpoints: List of checkpoints to progress through (Milestone 4)
        user_notes: Optional user-provided learning materials
        
    Returns:
        Initial LearningState
    """
    return LearningState(
        # Milestone 4: Multiple checkpoints
        all_checkpoints=checkpoints,
        current_checkpoint_index=0,
        checkpoint=checkpoints[0] if checkpoints else None,
        completed_checkpoints=[],
        user_notes=user_notes,
        gathered_contexts=[],
        context_valid=False,
        validation_message=None,
        retry_count=0,
        error=None,
        current_stage="initialized",
        messages=[],
        # Milestone 2 fields
        context_chunks=[],
        vector_store=None,
        questions=[],
        answers=[],
        understanding_score=None,
        passed_checkpoint=False,
        # Milestone 3 fields
        weak_concepts=[],
        feynman_explanations=[],
        feynman_attempts=0,
        max_feynman_attempts=3  # Allow up to 3 Feynman teaching cycles
    )
