# =====================================================
# Semantic Analysis Module
# (Chunking + Embeddings + Case-based Scoring)
# =====================================================

from typing import List, Dict
import numpy as np
import random
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------------------------------
# Load embedding model
# -----------------------------------------------------
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------------------------------
# 1. Word / Text Chunking
# -----------------------------------------------------
def chunk_text(text: str, chunk_size: int = 80) -> List[str]:
    words = text.split()
    return [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]

# -----------------------------------------------------
# 2. Generate Embeddings
# -----------------------------------------------------
def embed_chunks(chunks: List[str]) -> np.ndarray:
    return embedding_model.encode(chunks)

# -----------------------------------------------------
# 3. Semantic Similarity
# -----------------------------------------------------
def compute_similarity(context: str, answers: str) -> float:
    context_chunks = chunk_text(context)
    answer_chunks = chunk_text(answers)

    context_emb = embed_chunks(context_chunks)
    answer_emb = embed_chunks(answer_chunks)

    similarity_matrix = cosine_similarity(answer_emb, context_emb)
    return float(np.max(similarity_matrix))

# -----------------------------------------------------
# 4. Case-Based Score Adjustment
# -----------------------------------------------------
def apply_case_based_scoring(
    llm_score: int,
    similarity_score: float,
    confidence: int
) -> Dict[str, str | int]:

    final_score = llm_score
    reason = "Base LLM evaluation"

    if confidence >= 4 and similarity_score < 0.4:
        final_score -= 10
        reason = "High confidence but weak semantic alignment"

    elif confidence <= 2 and similarity_score > 0.7:
        final_score += 10
        reason = "Low confidence but strong semantic understanding"

    if similarity_score > 0.85:
        final_score += 5
        reason = "Excellent semantic alignment with reference content"

    final_score = max(0, min(100, final_score))

    return {
        "final_score": final_score,
        "case_reason": reason
    }

if __name__ == "__main__":

    print("\n🔍 SEMANTIC ANALYSIS MODULE DEMO\n")

    # -------------------------------------------------
    # Random CV topics
    # -------------------------------------------------
    samples = [
        (
            "Edge detection identifies object boundaries using gradient operators.",
            "Edges are detected using Sobel and Canny methods."
        ),
        (
            "Image segmentation divides an image into meaningful regions.",
            "Segmentation groups pixels based on similarity."
        ),
        (
            "Convolution is used in CNNs to extract spatial features.",
            "Convolution applies filters to detect patterns."
        ),
        (
            "Histogram equalization improves image contrast.",
            "Contrast enhancement spreads pixel intensity values."
        )
    ]

    sample_context, sample_answer = random.choice(samples)

    llm_score = random.randint(60, 90)
    confidence = random.randint(1, 5)

    print("🎯 Randomly Selected Topic")
    print("-------------------------")
    print("Context:", sample_context)
    print("Answer :", sample_answer)
    print("LLM Score:", llm_score)
    print("Confidence Level:", confidence)

    # -------------------------------------------------
    # Chunking
    # -------------------------------------------------
    print("\n📦 CONTEXT CHUNKS:")
    for i, c in enumerate(chunk_text(sample_context), 1):
        print(f"  Chunk {i}: {c}")

    print("\n📦 ANSWER CHUNKS:")
    for i, c in enumerate(chunk_text(sample_answer), 1):
        print(f"  Chunk {i}: {c}")

    # -------------------------------------------------
    # Embeddings
    # -------------------------------------------------
    context_emb = embed_chunks(chunk_text(sample_context))
    answer_emb = embed_chunks(chunk_text(sample_answer))

    print("\n🧠 EMBEDDING SHAPES:")
    print("  Context:", context_emb.shape)
    print("  Answer :", answer_emb.shape)

    # -------------------------------------------------
    # Similarity
    # -------------------------------------------------
    similarity = compute_similarity(sample_context, sample_answer)
    print("\n🔗 SEMANTIC SIMILARITY SCORE:")
    print(f"  Similarity: {similarity:.4f}")

    # -------------------------------------------------
    # Case-Based Scoring
    # -------------------------------------------------
    result = apply_case_based_scoring(
        llm_score=llm_score,
        similarity_score=similarity,
        confidence=confidence
    )

    print("\n📊 FINAL SCORE ANALYSIS:")
    print("  Initial Score :", llm_score)
    print("  Final Score   :", result["final_score"])
    print("  Decision Rule :", result["case_reason"])

    print("\n✅ Semantic analysis demo completed.\n")
