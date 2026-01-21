from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
)

def generate_checkpoints_from_topic(topic: str):
    """
    Dynamically generate 3 to 5 learning checkpoints for a given topic.
    Used as BACKUP when topic is not Machine Learning.
    """

    prompt = f"""
You are an educational planner.

Topic: {topic}

Task:
Generate between 3 and 5 learning checkpoints for this topic.

For each checkpoint provide:
- id (starting from 1, incremental)
- topic title
- 3 learning objectives

Rules:
- Use simple, beginner-friendly language
- Avoid jargon
- Ensure logical progression from basics to advanced concepts

Return the result in STRICT JSON format like this:

[
  {{
    "id": "1",
    "topic": "...",
    "objectives": ["...", "...", "..."]
  }},
  ...
]
"""

    response = llm.invoke(prompt)
    return response.content
