# rag/chunking.py
from typing import List


def chunk_context(text: str, max_length: int = 400) -> List[str]:
    """
    Split context into manageable chunks.
    """
    if not text.strip():
        return []

    paragraphs = text.split("\n\n")
    chunks = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(para) <= max_length:
            chunks.append(para)
        else:
            sentences = para.split(". ")
            current = ""
            for sentence in sentences:
                if len(current) + len(sentence) <= max_length:
                    current += sentence + ". "
                else:
                    chunks.append(current.strip())
                    current = sentence + ". "
            if current.strip():
                chunks.append(current.strip())

    return chunks
