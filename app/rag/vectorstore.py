# app/rag/vectorstore.py
from pathlib import Path
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from app.config import EMBEDDING_MODEL_NAME

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
NOTES_PATH = DATA_DIR / "sample_notes.txt"


def load_user_notes() -> List[Document]:
    if not NOTES_PATH.exists():
        return []

    text = NOTES_PATH.read_text(encoding="utf-8")
    # Simple split; you can replace with RecursiveCharacterTextSplitter later
    chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    docs = [Document(page_content=chunk, metadata={"source": "user_notes"}) for chunk in chunks]
    return docs


def build_notes_vectorstore() -> Optional[FAISS]:
    docs = load_user_notes()
    if not docs:
        return None

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vs = FAISS.from_documents(docs, embeddings)
    return vs
