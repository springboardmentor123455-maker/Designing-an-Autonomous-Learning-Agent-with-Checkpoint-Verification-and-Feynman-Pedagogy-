from langgraph.graph import StateGraph, END
from state import AgentState

from nodes.define_checkpoint import define_checkpoint
from nodes.gather_context import gather_context
from nodes.context_processing import context_processing
from nodes.validate_context import validate_context
from nodes.decision import needs_refetch

from nodes.question_generation import question_generation
from nodes.answer_verification import answer_verification
from nodes.answer_decision import answer_decision
from nodes.feynman_teaching import feynman_teaching


def build_graph():
    """
    One execution = one attempt
    NO internal loops
    """

    graph = StateGraph(AgentState)

    graph.add_node("define_checkpoint", define_checkpoint)
    graph.add_node("gather_context", gather_context)
    graph.add_node("context_processing", context_processing)
    graph.add_node("validate_context", validate_context)

    graph.add_node("question_generation", question_generation)
    graph.add_node("answer_verification", answer_verification)
    graph.add_node("answer_decision", answer_decision)
    graph.add_node("feynman_teaching", feynman_teaching)

    graph.set_entry_point("define_checkpoint")

    graph.add_edge("define_checkpoint", "gather_context")
    graph.add_edge("gather_context", "context_processing")
    graph.add_edge("context_processing", "validate_context")

    graph.add_conditional_edges(
        "validate_context",
        needs_refetch,
        {
            "refetch": "gather_context",
            "done": "question_generation",
        },
    )

    graph.add_edge("question_generation", "answer_verification")
    graph.add_edge("answer_verification", "answer_decision")

    graph.add_conditional_edges(
        "answer_decision",
        lambda state: state.get("decision"),
        {
            "pass": END,
            "fail": "feynman_teaching",
        },
    )

    graph.add_edge("feynman_teaching", END)

    return graph.compile()
