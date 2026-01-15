from typing import TypedDict, List

class Checkpoint(TypedDict):
    """
    Represents a single learning checkpoint.
    This matches Milestone 1 requirements:
    - topic
    - objectives
    - success criteria
    """
    id: str
    topic: str
    objectives: List[str]
    success_criteria: str

 
class AgentState(TypedDict, total=False):
    """
    State that flows through the LangGraph.

    Fields we need for Milestone 1:
    - checkpoint: current checkpoint we are working on
    - user_notes: raw text provided by learner (can be empty)
    - context: aggregated learning materials (notes + web search)
    - relevance_score: how relevant the context is to objectives
    - attempts: how many times we tried to gather context
    """
    selected_checkpoint: str  
    checkpoint: Checkpoint
    user_notes: str
    context: str
    relevance_score: float  
    attempts: int
    
    # Milestone 2: Quiz & Verification
    quiz_questions: List[dict]  # List of generated MCQs
    quiz_answers: dict          # User/Simulated answers
    quiz_score: float           # Final percentage
    quiz_result: str            # "PASSED" or "FAILED"
    # Milestone 3: Feynman Remediation
    knowledge_gaps: List[str]   # Concepts the user missed
    feynman_explanation: str    # The simplified explanation
    loop_count: int             # Track remediation loops

