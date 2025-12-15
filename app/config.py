# app/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file at project root
load_dotenv()

# ---- API KEYS ----
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
HF_MODEL_REPO_ID = os.getenv("HF_MODEL_REPO_ID", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")

if not HUGGINGFACEHUB_API_TOKEN:
    raise ValueError("HUGGINGFACEHUB_API_TOKEN is not set in .env")

# Optional: only needed if you use Tavily/web search
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# ---- RAG / VECTORSTORE CONFIG ----
# This is the constant your error is complaining about
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# ---- CONTEXT VALIDATION CONFIG ----
# Used in Milestone 1 loop
CONTEXT_RELEVANCE_THRESHOLD = 4.0  # 1–5 scale
MAX_CONTEXT_ATTEMPTS = 3
