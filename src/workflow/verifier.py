from typing import List, Dict
from ..state_types import AgentState


def verify_understanding(state: AgentState) -> AgentState:
    """
    Milestone 2 verifier without any LLM.
    - Uses the generated questions.
    - Simulates learner answers.
    - Computes an average score.
    - Sets status to 'passed' or 'needs_help' based on threshold.
    """
    qa_pairs: List[Dict[str, str]] = state.get("questions", [])

    if not qa_pairs:
        # No questions => can't verify understanding
        state["score"] = 0.0
        state["status"] = "needs_help"
        return state

    # For now, simulate answers as if learner did pretty well.
    # Later you will replace this with real user input and smarter scoring.
    simulated_answers = [qa["answer"] for qa in qa_pairs]

    # Simple fixed score per question (e.g. 0.9 = 90% correct)
    scores = [0.9 for _ in simulated_answers]

    avg_score = sum(scores) / len(scores)
    state["score"] = avg_score

    threshold = state["checkpoint"].get("success_threshold", 0.7)
    state["status"] = "passed" if avg_score >= threshold else "needs_help"

    return state
