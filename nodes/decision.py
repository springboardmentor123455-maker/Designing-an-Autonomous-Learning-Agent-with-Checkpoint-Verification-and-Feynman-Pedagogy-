from state import AgentState


def needs_refetch(state: AgentState) -> str:
    """
    Decide whether to refetch context or end the workflow.
    """
    score = state.get("relevance_score", 0.0)
    attempts = state.get("attempts", 0)

    print(f"\n[decision] score={score}, attempts={attempts}")

    if score < 4 and attempts < 3:
        print("[decision] Context insufficient. Refetching...")
        return "refetch"

    print("[decision] Context acceptable or max attempts reached. Ending.")
    return "done"
