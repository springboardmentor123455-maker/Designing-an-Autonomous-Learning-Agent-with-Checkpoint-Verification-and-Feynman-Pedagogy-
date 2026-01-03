from app.llm.huggingface_llm import call_llm


def build_assessment_questions(checkpoint, count=2):
    prompt = f"""
Generate exactly {count} short questions.
Do NOT add explanations.
Do NOT add headings.
Return only the questions as numbered list.

Topic: {checkpoint.title}
"""

    response = call_llm(prompt)

    questions = []

    for line in response.split("\n"):
        line = line.strip()

        # Skip empty or intro lines
        if not line:
            continue
        if "question" in line.lower():
            continue
        if line.startswith(("1.", "2.", "3.", "-")):
            q = line.lstrip("1234567890.- ").strip()
            if len(q) > 10:
                questions.append(q)

    # Fallback (important for demo safety)
    if not questions:
        questions = checkpoint.goals[:count]

    return questions[:count]
