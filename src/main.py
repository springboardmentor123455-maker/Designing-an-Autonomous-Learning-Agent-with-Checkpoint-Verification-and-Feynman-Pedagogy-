from .workflow.graph import build_graph
from .state_types import AgentState


def run_checkpoint(checkpoint_id: int = 1, user_notes: str | None = None):
    app = build_graph()
    initial_state: AgentState = {
        "cp_id": checkpoint_id,
        "user_notes": user_notes,
    }
    final_state = app.invoke(initial_state)
    return final_state


if __name__ == "__main__":
    notes = """d/dx of (3x^2 + 2x + 1)^5 is 5(3x^2+2x+1)^4 * (6x + 2)
    chain rule is derivative of outer function times derivative of inner function
    """

    result = run_checkpoint(checkpoint_id=1, user_notes=notes)

    # ---- Milestone 1: context relevance info ----
    print("Context Relevance Score (1–5):", result.get("context_relevance_score"))
    print("Context Relevance Ratio (0–1):", round(result.get("context_relevance_ratio", 0.0), 2))
    print("Context Retries:", result.get("context_retries"))

    # ---- Milestone 2: understanding verification ----
    print("Status:", result.get("status"))
    print("Score:", round(result.get("score", 0.0) * 100, 2), "%")
    print("Questions:")
    for i, qa in enumerate(result.get("questions", []), 1):
        print(f"{i}. {qa['question']}")
