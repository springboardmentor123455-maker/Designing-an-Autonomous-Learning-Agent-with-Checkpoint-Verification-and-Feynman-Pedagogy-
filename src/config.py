import os
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_TEXT_MODEL = os.getenv("HF_TEXT_MODEL", "distilgpt2")
HF_EMBED_MODEL = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

if not HF_API_TOKEN:
    raise ValueError("HF_API_TOKEN missing in .env")
