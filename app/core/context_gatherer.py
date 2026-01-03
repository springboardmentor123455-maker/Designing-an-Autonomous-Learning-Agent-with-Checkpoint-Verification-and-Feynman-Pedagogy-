# app/core/context_gatherer.py

from typing import Tuple
from app.llm.huggingface_llm import call_llm


# ------------------------------
# Local notes (can be extended)
# ------------------------------
USER_NOTES = {
    "cp1": """
Generative AI refers to a class of artificial intelligence models that are capable of
creating new content rather than only analyzing existing data. Unlike traditional AI
systems that follow fixed rules or make predictions, Generative AI can generate text,
images, audio, code, and even videos.

Examples of Generative AI include ChatGPT for text generation, DALL·E for image
creation, and GitHub Copilot for code assistance. These models learn patterns from
large datasets and use probability to generate new outputs that resemble human-created
content.

Generative AI is widely used today in education, content creation, healthcare,
chatbots, and software development because it increases productivity and enables
automation of creative tasks.
""",

    "cp2": """
Large Language Models (LLMs) are a type of Generative AI model trained on massive
amounts of text data. They learn language patterns, grammar, facts, and reasoning
abilities using deep neural networks called transformers.

LLMs work by predicting the next word in a sentence based on previous words.
During training, they process billions of sentences and adjust internal parameters
to minimize prediction errors. Examples of popular LLMs include GPT (OpenAI),
LLaMA (Meta), Gemini (Google), and Claude (Anthropic).

LLMs are used in chatbots, document summarization, question answering, translation,
and code generation. Their performance depends heavily on data quality and model size.
""",

    "cp5": """
Generative AI is widely used across industries. In education, it helps with tutoring,
content generation, and personalized learning. In software development, it assists
with code generation, debugging, and documentation.

In healthcare, Generative AI supports medical report generation and drug discovery.
In business, it helps with customer support, marketing content, and data analysis.

Despite its benefits, Generative AI also raises ethical concerns such as data privacy,
bias, misinformation, and misuse. Responsible AI practices are required to ensure
safe and ethical usage of these technologies.
"""
}


def collect_learning_context(checkpoint) -> Tuple[str, str]:
    """
    Fetch learning material for a checkpoint.
    Priority:
    1. User notes
    2. LLM-generated explanation
    """

    # Use local notes if available
    if checkpoint.id in USER_NOTES:
        return USER_NOTES[checkpoint.id], "Loaded from local notes"

    # Otherwise generate using LLM
    prompt = f"""
    Explain the topic '{checkpoint.title}' clearly.
    Cover these points:
    {", ".join(checkpoint.goals)}
    """

    content = call_llm(prompt)
    return content, "Generated using LLM"
