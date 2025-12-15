# app/llm/huggingface_llm.py
from langchain_community.llms import HuggingFaceHub
from app.config import HUGGINGFACEHUB_API_TOKEN

_llm = None  # cache singleton


def get_llm():
    """
    Use HuggingFaceHub (Inference API) for Bloom.
    This avoids provider issues seen with HuggingFaceEndpoint.
    """
    global _llm
    if _llm is not None:
        return _llm

    if not HUGGINGFACEHUB_API_TOKEN:
        raise ValueError("HUGGINGFACEHUB_API_TOKEN is not set in .env")

    _llm = HuggingFaceHub(
        repo_id="bigscience/bloom-560m",
        huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
        model_kwargs={
            "temperature": 0.2,
            "max_new_tokens": 256,
        },
    )
    return _llm
