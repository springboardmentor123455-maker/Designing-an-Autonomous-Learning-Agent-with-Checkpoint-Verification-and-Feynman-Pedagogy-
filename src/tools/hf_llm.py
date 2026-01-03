from langchain_huggingface import HuggingFaceEndpoint
from src.config import HF_API_TOKEN, HF_TEXT_MODEL

def get_text_llm():
    return HuggingFaceEndpoint(
        huggingfacehub_api_token=HF_API_TOKEN,
        repo_id=HF_TEXT_MODEL,
        task="text-generation",
        max_new_tokens=512,
        temperature=0.4,
        repetition_penalty=1.1,
    )
