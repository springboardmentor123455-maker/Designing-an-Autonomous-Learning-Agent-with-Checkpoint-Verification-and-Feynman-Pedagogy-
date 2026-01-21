import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from tavily import TavilyClient
from sentence_transformers import SentenceTransformer

# ---------- ENV SETUP ----------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is missing in .env")

# ---------- MODELS & CLIENTS ----------

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
)

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# RAG embedding model (loaded once)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
