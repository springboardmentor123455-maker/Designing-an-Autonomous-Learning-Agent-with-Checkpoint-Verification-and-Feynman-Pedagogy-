from typing import List, Dict
from ..state_types import AgentState


def generate_questions(state: AgentState) -> AgentState:
    """
    Simple, fully local question generator.
    No Hugging Face, no API calls.
    Uses the checkpoint topic and objectives to build 3–4 questions.
    """
    checkpoint = state["checkpoint"]
    topic = checkpoint.get("topic", "this topic")
    objectives = checkpoint.get("objectives", [])

    questions: List[Dict[str, str]] = []

    # Q1: Basic conceptual question
    questions.append({
        "question": f"What is the {topic.lower()} in your own words?",
        "answer": (
            "The chain rule is a differentiation rule for composite functions: "
            "differentiate the outer function and multiply by the derivative of the inner function."
            if "chain rule" in topic.lower()
            else f"It is a key idea in calculus related to {topic.lower()}."
        ),
    })

    # Q2+: One question per objective
    for obj in objectives:
        q = f"Explain or give an example of this objective: {obj}"
        a = f"This objective means: {obj}. You should be able to describe and apply it with an example."
        questions.append({"question": q, "answer": a})

    # Limit to at most 4 questions for now
    state["questions"] = questions[:4]
    return state
