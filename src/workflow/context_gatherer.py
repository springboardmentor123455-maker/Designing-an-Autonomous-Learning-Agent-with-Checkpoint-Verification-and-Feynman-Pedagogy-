import re
from typing import List, Tuple

from ..state_types import AgentState
from ..checkpoints import get_checkpoint
from ..tools.web_search import web_search


# ---------- helpers for relevance scoring ----------

_STOPWORDS = {
    "the", "a", "an", "of", "and", "or", "to", "in", "is", "are",
    "for", "on", "with", "by", "at", "be", "this", "that", "it",
    "as", "from", "about", "into", "their", "your", "you",
}


def _extract_keywords(topic: str, objectives: List[str]) -> List[str]:
    """
    Extract simple keyword list from topic + objectives.
    Lowercase, remove very short words and stopwords.
    """
    text = topic + " " + " ".join(objectives)
    words = re.findall(r"[a-zA-Z]+", text.lower())
    keywords = [
        w for w in words
        if len(w) > 3 and w not in _STOPWORDS
    ]
    # remove duplicates but keep order
    seen = set()
    result = []
    for w in keywords:
        if w not in seen:
            seen.add(w)
            result.append(w)
    return result


def _compute_relevance_score(text: str, topic: str, objectives: List[str]) -> Tuple[float, float]:
    """
    Compute a simple relevance score between 1 and 5 based on
    how many keyword matches appear in the gathered context.

    Returns:
        (score_1_to_5, match_ratio_0_to_1)
    """
    if not text.strip():
        return 1.0, 0.0

    keywords = _extract_keywords(topic, objectives)
    if not keywords:
        return 3.0, 0.5  # neutral if no keywords

    text_lower = text.lower()
    matches = 0
    for kw in keywords:
        if kw in text_lower:
            matches += 1

    ratio = matches / len(keywords)  # 0.0–1.0

    # Map ratio → 1–5 scale
    if ratio >= 0.8:
        score = 5.0
    elif ratio >= 0.6:
        score = 4.0
    elif ratio >= 0.4:
        score = 3.0
    elif ratio >= 0.2:
        score = 2.0
    else:
        score = 1.0

    return score, ratio


# ---------- LangGraph nodes ----------

def define_checkpoint(state: AgentState) -> AgentState:
    """
    Select the current checkpoint from cp_id in the state.
    """
    cp_id = state.get("cp_id", 1)
    checkpoint = get_checkpoint(cp_id)
    state["checkpoint"] = checkpoint
    state["status"] = "in_progress"
    # initialize retries
    state["context_retries"] = state.get("context_retries", 0)
    return state


def gather_context(state: AgentState) -> AgentState:
    """
    1. Use user notes if present.
    2. If not enough text, call web_search once.
    """
    checkpoint = state["checkpoint"]
    topic = checkpoint["topic"]
    objectives = checkpoint["objectives"]

    combined = ""

    # 1) user notes
    if state.get("user_notes"):
        combined += "User notes:\n" + state["user_notes"] + "\n\n"

    # 2) initial web search (only if context is tiny)
    if len(combined) < 400:
        query = f"{topic} - {'; '.join(objectives)} explanation for beginners"
        web_text = web_search(query)
        if web_text:
            combined += "Web search results:\n" + web_text

    state["raw_context"] = combined
    return state


def validate_context(state: AgentState) -> AgentState:
    """
    Context validation for Milestone 1:

    - Compute a Context Relevance Score (1–5) based on keyword match.
    - If the score is low (<= 2) and we haven't retried yet:
        - Trigger a second, more focused web search.
        - Recompute the score once.
    - Store score and ratio in state for evaluation.
    """
    checkpoint = state["checkpoint"]
    topic = checkpoint["topic"]
    objectives = checkpoint["objectives"]

    raw = state.get("raw_context", "")
    retries = state.get("context_retries", 0)

    # 1) compute initial relevance
    score, ratio = _compute_relevance_score(raw, topic, objectives)

    # 2) if relevance is low and we haven't retried yet, try one re-fetch
    if score <= 2.0 and retries < 1:
        print("[CONTEXT] Low relevance detected (score "
              f"{score}/5, ratio {ratio:.2f}). Re-fetching context...")
        retries += 1
        refined_query = f"{topic} detailed explanation, focus on: " + ", ".join(objectives)
        extra_text = web_search(refined_query)
        if extra_text:
            raw = (raw + "\n\nAdditional web search results:\n" + extra_text).strip()
        # recompute score after re-fetch
        score, ratio = _compute_relevance_score(raw, topic, objectives)

    # 3) log a warning if still low after retry
    if score <= 2.0:
        print(f"[CONTEXT] Warning: context still seems weakly relevant "
              f"(score {score}/5, ratio {ratio:.2f}).")

    # 4) save back to state
    state["raw_context"] = raw
    state["context_docs"] = [raw if raw else ""]
    state["context_relevance_score"] = score
    state["context_relevance_ratio"] = ratio
    state["context_retries"] = retries

    # also keep a simple length warning
    if len(raw) < 200:
        print("[CONTEXT] Warning: very little context available.")

    return state
