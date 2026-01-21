from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langsmith import traceable


@traceable(name="generate_questions")
def generate_questions(state):
    print("❓ Generating questions...")

    checkpoint = state["checkpoint"]
    topic = checkpoint["topic"]
    objectives = checkpoint.get("objectives", [])
    context = state.get("context", "")[:2000]

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3
    )

    prompt = f"""
Topic: {topic}

Objectives:
{chr(10).join(objectives)}

Context:
{context}

Generate exactly 4 assessment questions.
Do NOT include answers.
Number them.
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    questions = [
        {"text": line.strip()}
        for line in response.content.split("\n")
        if line.strip() and line.strip()[0].isdigit()
    ]

    state["questions"] = questions
    return state
