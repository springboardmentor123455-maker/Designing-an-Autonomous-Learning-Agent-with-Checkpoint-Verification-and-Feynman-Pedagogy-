import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-1.5-pro"


def gemini_evaluate(topic, objectives, user_answer):
    prompt = f"""
You are an evaluator.

Topic: {topic}
Objectives:
{chr(10).join("- " + o for o in objectives)}

Student answer:
{user_answer}

Score the answer between 0 and 1 based on how well it meets the objectives.
Return ONLY valid JSON like:
{{"score": 0.0, "reason": "short explanation"}}
"""
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text
    except Exception:
        return '{"score": 0.0, "reason": "Gemini evaluation failed"}'


def gemini_feynman(topic, objectives):
    prompt = f"""
Explain the topic below using the Feynman technique.
Use very simple words and a real-life analogy.

Topic: {topic}
Objectives:
{chr(10).join("- " + o for o in objectives)}
"""
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text
    except Exception:
        return "Let us explain this topic using a very simple real-life example."
