from state import AgentState

def answer_decision(state: AgentState) -> dict:
    score = state.get("score_percent", 0.0)

    if score >= 70:
        return {
            "decision": "pass"
        }

    return {
        "decision": "fail"
    }
