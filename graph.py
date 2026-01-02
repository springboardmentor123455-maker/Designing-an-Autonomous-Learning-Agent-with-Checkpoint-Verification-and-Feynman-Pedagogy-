from dotenv import load_dotenv
load_dotenv()

import os
import re
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from checkpoints import CHECKPOINTS
from langchain_groq import ChatGroq
from tavily import TavilyClient

# ---------------- ENV ----------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0
)

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ---------------- STATE ----------------
class LearningState(TypedDict, total=False):
    checkpoint_index: int
    checkpoint: object
    raw_context: str
    relevance_score: int
    weak_areas: List[str]
    feynman_explanation: Optional[str]
    next_checkpoint_index: int
    retrieval_mode: str
    data_source: str

# ---------------- NODES ----------------
def define_checkpoint(state: LearningState):
    state["checkpoint"] = CHECKPOINTS[state["checkpoint_index"]]
    return state


def gather_context(state: LearningState):
    if state.get("retrieval_mode") == "Local":
        state["data_source"] = "Local Notes"
        return state

    query = f"{state['checkpoint'].topic} for beginners"
    results = tavily.search(query=query, max_results=3)

    combined = []
    for r in results.get("results", []):
        if "content" in r:
            combined.append(r["content"])

    state["raw_context"] = "\n".join(combined)
    state["data_source"] = "Web RAG"
    return state


def validate_context(state: LearningState):
    prompt = f"""
Rate the relevance of the content for the topic on a scale of 1 to 5.

IMPORTANT RULE:
- Respond with ONLY ONE DIGIT between 1 and 5.
- No sentences.

Topic: {state['checkpoint'].topic}
Objectives: {state['checkpoint'].objectives}

Content:
{state['raw_context'][:3000]}
"""

    response = llm.invoke(prompt).content

    # ✅ SAFE REGEX EXTRACTION (THE FIX)
    match = re.search(r"\b([1-5])\b", response)

    if match:
        score = int(match.group(1))
    else:
        score = 1  # safe fallback

    state["relevance_score"] = score
    return state


def detect_gaps(state: LearningState):
    prompt = f"""
Identify weak learning areas.

Objectives:
{state['checkpoint'].objectives}

Relevance Score:
{state['relevance_score']}

Return bullet points only.
"""
    resp = llm.invoke(prompt).content

    state["weak_areas"] = [
        line.strip("- ").strip()
        for line in resp.splitlines()
        if line.strip()
    ]
    return state


def feynman_explain(state: LearningState):
    if state["relevance_score"] >= 4:
        return state

    prompt = f"""
Explain the topic using Feynman technique.
Use simple words and examples.

Topic: {state['checkpoint'].topic}
Weak Areas: {state['weak_areas']}
"""
    state["feynman_explanation"] = llm.invoke(prompt).content
    return state


def decide_next_checkpoint(state: LearningState):
    idx = state["checkpoint_index"]

    if state["relevance_score"] >= 4:
        state["next_checkpoint_index"] = min(idx + 1, len(CHECKPOINTS) - 1)
    else:
        state["next_checkpoint_index"] = idx

    return state


# ---------------- GRAPH ----------------
def build_graph():
    g = StateGraph(LearningState)

    g.add_node("define_checkpoint", define_checkpoint)
    g.add_node("gather_context", gather_context)
    g.add_node("validate_context", validate_context)
    g.add_node("detect_gaps", detect_gaps)
    g.add_node("feynman_explain", feynman_explain)
    g.add_node("decide_next_checkpoint", decide_next_checkpoint)

    g.set_entry_point("define_checkpoint")

    g.add_edge("define_checkpoint", "gather_context")
    g.add_edge("gather_context", "validate_context")
    g.add_edge("validate_context", "detect_gaps")
    g.add_edge("detect_gaps", "feynman_explain")
    g.add_edge("feynman_explain", "decide_next_checkpoint")
    g.add_edge("decide_next_checkpoint", END)

    return g.compile()
