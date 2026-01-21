from langgraph.graph import StateGraph, END

from .context_gather import gather_context
from .validator import validate_context
from .context_process import process_context
from .question_gen import generate_questions
from .verifier import verify_answers
from .feynman_teacher import feynman_teach

PASS_THRESHOLD = 70
MAX_CONTEXT_RETRIES = 3


def should_retry(state):
    retries = state.get("context_retry", 0)
    if state.get("relevance_score", 0) < 0.5:
        if retries >= MAX_CONTEXT_RETRIES:
            return "process"
        state["context_retry"] = retries + 1
        return "retry"
    return "process"


def route_after_verification(state):
    if state.get("score", 0) >= PASS_THRESHOLD:
        return "end"
    return "feynman"



def build_graph():
    g = StateGraph(dict)

    g.add_node("gather_context", gather_context)
    g.add_node("validate_context", validate_context)
    g.add_node("process_context", process_context)
    g.add_node("generate_questions", generate_questions)
    g.add_node("verify_answers", verify_answers)
    g.add_node("feynman_teach", feynman_teach)

    g.set_entry_point("gather_context")
    g.add_edge("gather_context", "validate_context")

    g.add_conditional_edges(
        "validate_context",
        should_retry,
        {"retry": "gather_context", "process": "process_context"}
    )

    g.add_edge("process_context", "generate_questions")
    g.add_edge("generate_questions", "verify_answers")

    g.add_conditional_edges(
        "verify_answers",
        route_after_verification,
        {"end": END, "feynman": "feynman_teach"}
    )

    g.add_edge("feynman_teach", END)

    return g.compile()
