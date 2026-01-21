from langchain_groq import ChatGroq
from state import AgentState

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.25,  # keeps it calm and non-verbose
)

def feynman_teaching(state: AgentState) -> AgentState:
    """
    FINAL Feynman Teaching Node 

    Output rules:
    - Exactly 3 to 4 short paragraphs
    - Story-based opening
    - Flowing, spoken explanation
    - No bullets, no headings, no lists
    - No exam-style definitions
    """

    topic = state["checkpoint"]["topic"]
    context = state.get("context", "")
    gaps = state.get("knowledge_gaps", [])

    prompt = f"""
Explain the topic below to a beginner in a natural, spoken way.

Topic:
{topic}

Learner confusion:
{gaps if gaps else "general understanding"}

STRICT OUTPUT REQUIREMENTS (DO NOT BREAK):

- Write EXACTLY 3 to 4 paragraphs.
- Each paragraph should be short (3–4 sentences max).
- Start the FIRST paragraph with a simple real-life example or imagination.
- Use smooth transitions between paragraphs.
- Do NOT use bullet points, numbering, or headings.
- Do NOT explain like a textbook.
- Avoid repeating the same idea in different words.
- End naturally, without a formal summary.

Style:
- Sound like a teacher explaining calmly.
- Leave small gaps so the reader can think.

Context you may refer to (do not copy):
{context[:1800]}

Now write the explanation following these rules exactly.
"""

    explanation = llm.invoke(prompt).content.strip()

    return {
        "feynman_explanation": explanation,
        "feynman_attempts": state.get("feynman_attempts", 0) + 1
    }
