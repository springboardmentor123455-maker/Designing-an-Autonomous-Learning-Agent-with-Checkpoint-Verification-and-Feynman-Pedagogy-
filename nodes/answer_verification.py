from state import AgentState
import re

CORE_KEYWORDS = [
    "data", "learn", "learning", "model", "algorithm",
    "patterns", "prediction", "training", "examples",
    "performance", "decision", "improve"
]

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()

def answer_verification(state: AgentState) -> AgentState:
    """
    FINAL SCORING LOGIC:
    - Length-based + keyword-based
    - No strict keyword matching
    - No zero-division
    - Prevents copy-paste cheating
    """

    print("\n[answer_verification] Running improved verification...")

    questions = state.get("questions", [])
    answers = state.get("answers", [])

    per_question_scores = []
    knowledge_gaps = []

    if not questions or not answers:
        return {
            "score_percent": 0.0,
            "per_question_scores": [],
            "knowledge_gaps": questions,
        }

    for q, ans in zip(questions, answers):
        ans_norm = normalize(ans)
        q_norm = normalize(q)

        if len(ans_norm.split()) < 20:
            per_question_scores.append(0)
            knowledge_gaps.append(q)
            continue

        if ans_norm == q_norm or q_norm in ans_norm:
            per_question_scores.append(0)
            knowledge_gaps.append(q)
            continue

        keyword_hits = sum(1 for k in CORE_KEYWORDS if k in ans_norm)

        if keyword_hits >= 1:
            per_question_scores.append(1)
        else:
            per_question_scores.append(0)
            knowledge_gaps.append(q)

    total = len(per_question_scores)
    score_percent = (sum(per_question_scores) / total) * 100 if total > 0 else 0.0

    print(f"[answer_verification] Score = {score_percent:.2f}%")

    return {
        "per_question_scores": per_question_scores,
        "knowledge_gaps": knowledge_gaps,
        "score_percent": score_percent,
    }
