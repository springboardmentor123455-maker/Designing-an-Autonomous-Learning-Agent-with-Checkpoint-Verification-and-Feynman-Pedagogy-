# app/core/feynman_explainer.py

from app.llm.huggingface_llm import call_llm


def simplify_with_feynman(question, wrong_answer, context):
    prompt = f"""
    Explain this in very simple words like teaching a child.

    Question: {question}
    Student mistake: {wrong_answer}

    Use examples and avoid technical words.
    """

    return call_llm(prompt)
