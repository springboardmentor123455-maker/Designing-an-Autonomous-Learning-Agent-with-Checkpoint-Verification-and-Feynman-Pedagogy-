from typing import List
from state import AgentState
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
)

def question_generation(state: AgentState) -> AgentState:
    """
    Milestone 2 – Step 2:
    Generate 3–5 questions based on context + objectives.
    """

    print("\n[question_generation] Generating questions...")

    checkpoint = state["checkpoint"]
    context = state.get("context", "")

    objectives = "\n".join(f"- {o}" for o in checkpoint["objectives"])

    prompt = f"""
You are a tutor preparing assessment questions.

Topic:
{checkpoint['topic']}

Learning Objectives:
{objectives}

Context:
\"\"\"{context[:3000]}\"\"\"

Task:
Generate 3 to 5 clear, simple questions that test understanding of the topic.
Return ONLY the questions, each on a new line.
"""

    response = llm.invoke(prompt)
    raw = response.content.strip()

    questions: List[str] = [
        q.strip("- ").strip()
        for q in raw.split("\n")
        if q.strip()
    ]

    questions = questions[:5]

    print(f"[question_generation] Generated {len(questions)} questions:\n")
    for i, q in enumerate(questions, 1):
        print(f"  Q{i}: {q}")

    return {
        "questions": questions
    }
