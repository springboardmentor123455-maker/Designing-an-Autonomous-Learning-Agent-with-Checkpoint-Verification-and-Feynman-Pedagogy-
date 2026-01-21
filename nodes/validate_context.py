from state import AgentState
from config import llm


def _build_relevance_prompt(checkpoint, context: str) -> str:
    objectives = "\n".join(f"- {o}" for o in checkpoint["objectives"])
    return f"""
Evaluate how relevant this context is to the learning objectives.

Topic:
{checkpoint['topic']}

Objectives:
{objectives}

Success criteria:
{checkpoint['success_criteria']}

Context:
\"\"\"{context[:4000]}\"\"\" 

Reply ONLY with a number from 1 to 5.
"""


def validate_context(state: AgentState) -> AgentState:
    """
    Ask LLM to score how relevant the gathered context is (1–5).
    """
    checkpoint = state["checkpoint"]
    context = state.get("context", "")

    if not context.strip():
        print("[validate_context] No context found. Score = 1")
        return {"relevance_score": 1.0}

    print("\n[validate_context] Evaluating context relevance...")

    response = llm.invoke(_build_relevance_prompt(checkpoint, context))
    raw_text = str(response.content).strip()

    try:
        score = float(raw_text)
    except Exception:
        print(
            f"[validate_context] Could not parse '{raw_text}'. "
            "Defaulting score = 2"
        )
        score = 2.0

    print(f"[validate_context] Score = {score}/5")

    return {"relevance_score": score}
