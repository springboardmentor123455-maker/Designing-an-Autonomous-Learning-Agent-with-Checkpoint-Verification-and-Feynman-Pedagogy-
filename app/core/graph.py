# app/core/graph.py
from __future__ import annotations

from typing import Callable
from langgraph.graph import StateGraph, END

from app.core.state import LearningState
from app.core.context_gatherer import gather_context_for_checkpoint
from app.core.context_validator import validate_context
from app.config import CONTEXT_RELEVANCE_THRESHOLD, MAX_CONTEXT_ATTEMPTS


def node_define_checkpoint(state: LearningState) -> LearningState:
    cp = state["checkpoint"]
    trace = state.get("trace", [])
    trace.append(f"Starting checkpoint: {cp['id']} - {cp['title']}")
    state["trace"] = trace

    state["query"] = f"{cp['title']} - " + "; ".join(cp["objectives"])
    state["context_attempts"] = 0
    return state


def node_gather_context(state: LearningState) -> LearningState:
    cp = state["checkpoint"]
    topic = cp["title"]
    objectives = cp["objectives"]

    attempts = state.get("context_attempts", 0) + 1
    state["context_attempts"] = attempts

    docs, source = gather_context_for_checkpoint(topic, objectives, attempts, user_query=state.get("user_query"))

    state["gathered_context"] = docs
    state["context_source"] = source

    trace = state.get("trace", [])
    trace.append(
        f"Gathered {len(docs)} docs from source: {source} (attempt {attempts})"
    )
    state["trace"] = trace
    return state


def node_validate_context(state: LearningState) -> LearningState:
    cp = state["checkpoint"]
    topic = cp["title"]
    objectives = cp["objectives"]
    docs = state.get("gathered_context", [])
    score, feedback = validate_context(topic, objectives, docs, state.get("user_query"), state.get("validation_backend"))



    state["context_relevance_score"] = score
    state["context_validation_feedback"] = feedback

    trace = state.get("trace", [])
    trace.append(f"Validation score={score:.2f}, feedback='{feedback}'")
    state["trace"] = trace
    return state


def route_after_validation(state: LearningState) -> str:
    score = state.get("context_relevance_score", 0.0)
    attempts = state.get("context_attempts", 0)

    if score >= CONTEXT_RELEVANCE_THRESHOLD:
        return END

    if attempts >= MAX_CONTEXT_ATTEMPTS:
        trace = state.get("trace", [])
        trace.append(
            f"Reached MAX_CONTEXT_ATTEMPTS ({attempts}) with score={score:.2f}; ending with suboptimal context."
        )
        state["trace"] = trace
        return END

    return "gather_context"


def build_graph() -> Callable[[LearningState], LearningState]:
    graph = StateGraph(LearningState)

    graph.add_node("define_checkpoint", node_define_checkpoint)
    graph.add_node("gather_context", node_gather_context)
    graph.add_node("validate_context", node_validate_context)

    graph.set_entry_point("define_checkpoint")
    graph.add_edge("define_checkpoint", "gather_context")
    graph.add_edge("gather_context", "validate_context")

    graph.add_conditional_edges(
        "validate_context",
        route_after_validation,
        {
            "gather_context": "gather_context",
            END: END,
        },
    )

    return graph.compile()
