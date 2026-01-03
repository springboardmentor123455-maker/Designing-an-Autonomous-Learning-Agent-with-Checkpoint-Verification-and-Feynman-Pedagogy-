from langgraph.graph import StateGraph, END
from ..state_types import AgentState
from .context_gatherer import define_checkpoint, gather_context, validate_context
from .context_processor import process_context
from .question_generator import generate_questions
from .verifier import verify_understanding


def build_graph():
    workflow = StateGraph(AgentState)

    # nodes
    workflow.add_node("define_checkpoint", define_checkpoint)
    workflow.add_node("gather_context", gather_context)
    workflow.add_node("validate_context", validate_context)
    workflow.add_node("process_context", process_context)
    workflow.add_node("generate_questions", generate_questions)
    workflow.add_node("verify_understanding", verify_understanding)

    # edges
    workflow.set_entry_point("define_checkpoint")
    workflow.add_edge("define_checkpoint", "gather_context")
    workflow.add_edge("gather_context", "validate_context")
    workflow.add_edge("validate_context", "process_context")
    workflow.add_edge("process_context", "generate_questions")
    workflow.add_edge("generate_questions", "verify_understanding")

    # conditional exit
    def route_after_verification(state: AgentState):
        if state.get("status") == "passed":
            return "passed"
        else:
            return "needs_help"

    workflow.add_conditional_edges(
        "verify_understanding",
        route_after_verification,
        {
            "passed": END,        # later this will go to next checkpoint
            "needs_help": END,    # later this will go to Feynman node
        },
    )

    return workflow.compile()
