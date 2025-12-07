from typing import TypedDict, Annotated, List
import operator
from src.models import LearningCheckpoint  # Importing our new structure

class AgentState(TypedDict):
    # The Formal "Map" (Required by spec)
    active_checkpoint: LearningCheckpoint
    
    # Inputs & Outputs
    user_notes: str
    gathered_context: str
    
    # Validation Logic
    relevance_score: int
    feedback: str
    retry_count: int
    
    # Logs for the UI
    logs: Annotated[List[str], operator.add]