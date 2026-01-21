import numpy as np
from config import llm, embedding_model


def answer_with_rag(question, chunks, embeddings):
    if not chunks or embeddings.size == 0:
        return "I don't have enough context to answer that."

    q_vec = embedding_model.encode([question], normalize_embeddings=True)[0]
    scores = embeddings @ q_vec

    top_k = min(3, len(chunks))
    top_idx = np.argsort(-scores)[:top_k]

    context = "\n\n".join(chunks[i] for i in top_idx)

    prompt = f"""
Use ONLY the context below to answer the question.
If the answer is not in the context, say you are not sure.

Context:
\"\"\"{context}\"\"\"

Question:
{question}
"""

    response = llm.invoke(prompt)
    return str(response.content).strip()
