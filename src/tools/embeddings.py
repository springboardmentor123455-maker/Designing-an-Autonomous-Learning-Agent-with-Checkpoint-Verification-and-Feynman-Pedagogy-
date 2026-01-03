from langchain_huggingface import HuggingFaceEmbeddings
from src.config import HF_EMBED_MODEL

def get_embeddings():
    return HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)
