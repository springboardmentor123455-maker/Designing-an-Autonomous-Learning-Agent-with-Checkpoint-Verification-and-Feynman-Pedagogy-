"""
State definitions for the LangGraph workflow.
Defines the state structure that flows through the learning agent workflow.
"""

from typing import List, Optional, Dict, Any, Annotated
from typing_extensions import TypedDict
from datetime import datetime

from src.models import (
    Checkpoint, 
    CheckpointProgress, 
    GatheredContext, 
    ContextSource,
    LearningSession
)


class LearningAgentState(TypedDict):
    """Complete state for the learning agent workflow."""
    
    # Session information
    session_id: str
    learner_id: str
    
    # Current checkpoint
    current_checkpoint: Optional[Checkpoint]
    checkpoint_progress: Optional[CheckpointProgress]
    
    # Context gathering
    user_notes: Optional[str]
    gathered_context: Optional[GatheredContext]
    context_sources: List[ContextSource]
    context_validation_complete: bool
    
    # Workflow control
    workflow_step: str  # Current step in the workflow
    needs_web_search: bool
    context_quality_sufficient: bool
    
    # Error handling
    errors: List[str]
    retry_count: int
    
    # Metadata
    timestamp: datetime
    workflow_history: List[str]  # Track workflow path for debugging


def create_initial_state(
    session_id: str,
    checkpoint: Checkpoint,
    learner_id: str = "default",
    user_notes: Optional[str] = None
) -> LearningAgentState:
    """Create initial state for a learning session."""
    return LearningAgentState(
        session_id=session_id,
        learner_id=learner_id,
        current_checkpoint=checkpoint,
        checkpoint_progress=CheckpointProgress(checkpoint_id=checkpoint.id, learner_id=learner_id),
        user_notes=user_notes,
        gathered_context=None,
        context_sources=[],
        context_validation_complete=False,
        workflow_step="initialize",
        needs_web_search=True,
        context_quality_sufficient=False,
        errors=[],
        retry_count=0,
        timestamp=datetime.now(),
        workflow_history=[]
    )