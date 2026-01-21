from state import AgentState
from rag.chunking import chunk_context
from rag.embeddings import build_embeddings


def context_processing(state: AgentState) -> AgentState:
    """
    Milestone 2 – Step 1
    Process context into chunks and embeddings
    """
    context = state.get("context", "").strip()

    if not context:
        print("[context_processing] No context available.")
        return {}

    print("\n[context_processing] Processing context...")

    chunks = chunk_context(context)
    print(f"[context_processing] Created {len(chunks)} chunks.")

    embeddings = build_embeddings(chunks)
    print("[context_processing] Embeddings generated.")

    return {
        "chunks": chunks,
        "embeddings": embeddings,
    }
