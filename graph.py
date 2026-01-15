from langgraph.graph import StateGraph, END
from models import AgentState
from nodes import (
    define_checkpoint, 
    gather_context, 
    validate_context,   
    needs_refetch,
    process_context,
    generate_quiz,
    take_quiz,
    evaluate_quiz,
    check_progression,
    feynman_remediation,
    create_study_guide
) 

# ---------- BUILD THE LANGGRAPH ----------

def build_graph():
    """
    Constructs the LangGraph for Milestone 2:
    
    1. Define Checkpoint
    2. Gather Context -> Validate
    3. If valid -> Process Context -> Generate Quiz -> Simulate -> Evaluate
    4. If Pass -> END (Success)
       If Fail -> END (Halt)
    """
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("define_checkpoint", define_checkpoint)
    workflow.add_node("gather_context", gather_context)
    workflow.add_node("validate_context", validate_context)
    
    # Milestone 2 Nodes
    workflow.add_node("process_context", process_context)
    workflow.add_node("generate_quiz", generate_quiz)
    workflow.add_node("take_quiz", take_quiz)
    workflow.add_node("evaluate_quiz", evaluate_quiz)
    workflow.add_node("feynman_remediation", feynman_remediation)
    workflow.add_node("create_study_guide", create_study_guide)

    # Entry point
    workflow.set_entry_point("define_checkpoint")

    # Edges
    workflow.add_edge("define_checkpoint", "gather_context")
    workflow.add_edge("gather_context", "validate_context")

    # Conditional logic after validation
    workflow.add_conditional_edges(
        "validate_context",
        needs_refetch,
        {
            "refetch": "gather_context",
            "process": "process_context",
        },
    )
    
    # Linear flow for Milestone 2 components
    workflow.add_edge("process_context", "create_study_guide")
    workflow.add_edge("create_study_guide", "generate_quiz")
    workflow.add_edge("generate_quiz", "take_quiz")
    workflow.add_edge("take_quiz", "evaluate_quiz")
    
    # Remediation loop
    workflow.add_edge("feynman_remediation", "generate_quiz")
    
    # Conditional logic after quiz evaluation
    workflow.add_conditional_edges(
        "evaluate_quiz",
        check_progression,
        {
            "pass": END,
            "fail": END,
            "remediate": "feynman_remediation",
        }
    )

    return workflow.compile()
