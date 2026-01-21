# rag/embeddings.py
import numpy as np
from sentence_transformers import SentenceTransformer

# Load once
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def build_embeddings(chunks: list[str]) -> np.ndarray:
    """
    Generate embeddings for text chunks.
    Stored temporarily for the session.
    """
    if not chunks:
        return np.array([])

    embeddings = EMBED_MODEL.encode(
        chunks,
        normalize_embeddings=True
    )

    return embeddings
