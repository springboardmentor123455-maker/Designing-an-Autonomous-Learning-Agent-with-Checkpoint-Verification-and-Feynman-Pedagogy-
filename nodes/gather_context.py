from typing import List

from state import AgentState
from config import tavily_client


def gather_context(state: AgentState) -> AgentState:
    """
    Gather learning context from:
    1. User-provided notes (highest priority)
    2. Tavily web search (fallback / enrichment)
    """
    checkpoint = state["checkpoint"]
    user_notes = state.get("user_notes", "").strip()

    prev_attempts = state.get("attempts", 0)
    attempts = prev_attempts + 1

    print("\n[gather_context] Gathering context...")
    print(f"[gather_context] This is attempt #{attempts}")

    chunks: List[str] = []

    # Tier 1: User notes
    if user_notes:
        print("[gather_context] Using user-provided notes.")
        chunks.append("USER NOTES:\n" + user_notes)

    # Tier 2: Web search via Tavily
    search_query = f"{checkpoint['topic']} - " + "; ".join(checkpoint["objectives"])
    print(f"[gather_context] Tavily search query: {search_query}")

    try:
        result = tavily_client.search(
            query=search_query,
            max_results=4,
            search_depth="basic",
        )
        web_items = result.get("results", [])

        if web_items:
            pages = [item.get("content", "") for item in web_items]
            chunks.append("WEB SEARCH RESULTS:\n" + "\n\n".join(pages))
        else:
            print("[gather_context] No Tavily results.")

    except Exception as e:
        print(f"[gather_context] Tavily error: {e}")

    combined_context = "\n\n".join(chunks)

    return {
        "context": combined_context,
        "attempts": attempts,
    }
