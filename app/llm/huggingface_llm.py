from huggingface_hub import InferenceClient
import os


def call_llm(prompt: str) -> str:
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

    if not token:
        return "HF API key not found."

    client = InferenceClient(token=token)

    try:
        response = client.chat_completion(
            model="meta-llama/Llama-3.2-3B-Instruct",
            messages=[
                {"role": "system", "content": "You are a helpful tutor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"LLM Error: {str(e)}"
