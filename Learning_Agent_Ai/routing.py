# =========================
# MILESTONE 1
# =========================
from langsmith import traceable
from state import LearningState


@traceable(name="route_after_validation")
def route_after_validation(state: LearningState) -> str:
    """
    Decide what to do after context validation.

    Rules:
    - If relevance score < 4 and retries < 2 → retry gathering context
    - Otherwise → accept context and move forward
    """
    if state["context_evalution"] == 'approved' or state["context_iteration"]>=state["max_iteration"]:
        return 'approved'
    
    return 'need improment'
   
# =========================
# MILESTONE 2 & 3
# =========================
@traceable(name="route_after_scoring")
def route_after_scoring(state: LearningState) -> str:
    """
    Decide next step after answer evaluation.

    Rules:
    - Score ≥ 70% → PASS (end checkpoint)
    - Score < 70% → Trigger Feynman teaching
    """
    if state["passed"] == True or state["feynman_iteration"] >= state["max_iteration"] :
        return "pass"
    return "feynman"
