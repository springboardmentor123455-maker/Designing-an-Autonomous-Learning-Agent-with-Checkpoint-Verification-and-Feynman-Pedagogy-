# src/verifier.py

import json
import time
import re
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage


# ----------------------------
# Utility helpers
# ----------------------------

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def is_meaningless(answer: str) -> bool:
    """
    Reject ONLY truly meaningless answers.
    """
    a = normalize(answer)

    if len(a) < 3:
        return True

    if a in {"s", "ss", "ok", "yes", "no", "idk", "dont know"}:
        return True

    # Must contain at least one alphabetic word
    if not re.search(r"[a-zA-Z]{3,}", a):
        return True

    return False


# ----------------------------
# Main verifier
# ----------------------------

def verify_answers(state):
    print("🧪 Verifying answers (Groq-based, fixed)...")

    questions = state.get("questions", [])
    user_answers = state.get("user_answers") or {}
    context = state.get("context", "")
    topic = state.get("checkpoint", {}).get("topic", "")

    # Interactive mode: no grading yet
    if not user_answers:
        state["score"] = 0
        state["per_question_scores"] = []
        state["feedback"] = []
        return state

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.0
    )

    scores = []
    feedbacks = []

    for idx, q in enumerate(questions):
        q_text = q["text"] if isinstance(q, dict) else str(q)

        # 🔒 SAFE retrieval (index-based fallback)
        answer = user_answers.get(q_text)
        if answer is None and isinstance(user_answers, dict):
            if idx < len(user_answers.values()):
                answer = list(user_answers.values())[idx]
        answer = (answer or "").strip()

        # ❌ Truly empty
        if not answer:
            scores.append(0)
            feedbacks.append("No answer provided.")
            continue

        # ❌ Meaningless
        if is_meaningless(answer):
            scores.append(10)
            feedbacks.append("Answer is too vague or meaningless.")
            continue

        time.sleep(0.4)

        prompt = f"""
You are a strict but fair computer science examiner.

TOPIC:
{topic}

REFERENCE CONTEXT:
{context[:1500]}

QUESTION:
{q_text}

STUDENT ANSWER:
{answer}

GRADING RULES:
- Correct but short → 70–80
- Correct with explanation → 85–100
- Partial understanding → 40–69
- Incorrect → below 40
- Do NOT reward random answers
- Judge concept correctness, not length

Return ONLY valid JSON:
{{ "score": number, "feedback": "brief justification" }}
"""

        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            data = json.loads(response.content)

            score = int(data.get("score", 0))
            feedback = data.get("feedback", "No feedback provided.")

        except Exception as e:
            score = 40
            feedback = "Answer evaluated conservatively due to parsing issue."

        score = max(0, min(score, 100))
        scores.append(score)
        feedbacks.append(feedback)

    final_score = round(sum(scores) / len(scores), 2)

    state["score"] = final_score
    state["per_question_scores"] = scores
    state["feedback"] = feedbacks

    print(f"📊 Final score: {final_score}%")
    return state
