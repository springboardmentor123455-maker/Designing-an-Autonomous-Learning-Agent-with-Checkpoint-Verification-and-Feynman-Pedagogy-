from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage


def feynman_teach(state):
    print("🧠 Feynman teaching...")

    questions = state.get("questions", [])
    scores = state.get("per_question_scores", [])
    feedback = state.get("feedback", [])

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3)

    explanations = []

    for q, s, fb in zip(questions, scores, feedback):
        if s >= 70:
            continue

        prompt = f"""
Explain simply using Feynman technique.

Question:
{q['text']}

Student issue:
{fb}
"""

        res = llm.invoke([HumanMessage(content=prompt)])
        explanations.append({
            "question": q["text"],
            "explanation": res.content.strip()
        })

    state["feynman_explanations"] = explanations
    return state
