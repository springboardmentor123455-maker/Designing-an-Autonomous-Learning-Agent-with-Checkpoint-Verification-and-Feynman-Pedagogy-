from typing import TypedDict, Annotated, List, Dict, Any
import operator
from src.models import LearningCheckpoint

class AgentState(TypedDict):
    active_checkpoint: LearningCheckpoint
    user_notes: str
    gathered_context: str
    relevance_score: int
    feedback: str
    retry_count: int
    logs: Annotated[List[str], operator.add]

    processed_context: List[str] 
    
    quiz_questions: List[Dict[str, Any]] # List of {question, correct_answer}
    
    user_answers: Dict[str, str]
    quiz_score: int # 0-100