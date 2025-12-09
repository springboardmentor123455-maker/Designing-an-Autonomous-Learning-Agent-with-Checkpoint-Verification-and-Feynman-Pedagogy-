"""LangGraph state definition for the learning workflow."""
from typing import List, Optional, TypedDict, Annotated
import operator
from src.models.checkpoint import Checkpoint, GatheredContext


class LearningState(TypedDict):
    """
    State object for the LangGraph learning workflow (Week 1-2).
    
    This state is passed between nodes in the graph and maintains
    all information about the current learning session.
    """
    # Current checkpoint being worked on
    checkpoint: Optional[Checkpoint]
    
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


def create_initial_state(
    checkpoint: Checkpoint,
    user_notes: Optional[str] = None
) -> LearningState:
    """
    Create an initial state for the learning workflow (Week 1-2).
    
    Args:
        checkpoint: The checkpoint to start with
        user_notes: Optional user-provided learning materials
        
    Returns:
        Initial LearningState
    """
    return LearningState(
        checkpoint=checkpoint,
        user_notes=user_notes,
        gathered_contexts=[],
        context_valid=False,
        validation_message=None,
        retry_count=0,
        error=None,
        current_stage="initialized",
        messages=[]
    )
