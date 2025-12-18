"""
Workflow creation and routing for the Learning Agent System.

This module handles the creation of the complete unified workflow using LangGraph,
including node connections, conditional routing, and workflow orchestration.
"""

import logging
from langgraph.graph import StateGraph, END
from .models import LearningAgentState
from .workflow_nodes import (
    initialize_node,
    collect_materials_node, 
    summarize_materials_node,
    evaluate_milestone1_node,
    process_context_node,
    generate_questions_node,
    verify_understanding_node,
    check_threshold_node,
    complete_checkpoint_node,
    feynman_placeholder_node
)

logger = logging.getLogger(__name__)

def _route_after_threshold_check(state: LearningAgentState) -> str:
    """Route decision after threshold check."""
    meets_threshold = state.get("meets_threshold", False)
    
    if meets_threshold:
        logger.info("🎯 Routing to checkpoint completion")
        return "pass"
    else:
        logger.info("📚 Routing to Feynman teaching")
        return "fail"

def create_unified_workflow() -> StateGraph:
    """Create the complete unified workflow for Milestones 1 & 2."""
    
    logger.info("🏗️ Creating unified learning workflow...")
    
    # Create workflow
    workflow = StateGraph(LearningAgentState)
    
    # Add all nodes
    workflow.add_node("initialize", initialize_node)
    workflow.add_node("collect_materials", collect_materials_node)
    workflow.add_node("summarize_materials", summarize_materials_node)
    workflow.add_node("evaluate_milestone1", evaluate_milestone1_node)
    workflow.add_node("process_context", process_context_node)
    workflow.add_node("generate_questions", generate_questions_node)
    workflow.add_node("verify_understanding", verify_understanding_node)
    workflow.add_node("check_threshold", check_threshold_node)
    workflow.add_node("complete_checkpoint", complete_checkpoint_node)
    workflow.add_node("feynman_placeholder", feynman_placeholder_node)
    
    # Set entry point
    workflow.set_entry_point("initialize")
    
    # Define workflow edges
    workflow.add_edge("initialize", "collect_materials")
    workflow.add_edge("collect_materials", "summarize_materials")
    workflow.add_edge("summarize_materials", "evaluate_milestone1")
    workflow.add_edge("evaluate_milestone1", "process_context")
    workflow.add_edge("process_context", "generate_questions")
    workflow.add_edge("generate_questions", "verify_understanding")
    workflow.add_edge("verify_understanding", "check_threshold")
    
    # Conditional routing based on threshold
    workflow.add_conditional_edges(
        "check_threshold",
        _route_after_threshold_check,
        {
            "pass": "complete_checkpoint",
            "fail": "feynman_placeholder"
        }
    )
    
    # End points
    workflow.add_edge("complete_checkpoint", END)
    workflow.add_edge("feynman_placeholder", END)
    
    # Compile the workflow
    compiled_workflow = workflow.compile()
    
    logger.info("✅ Unified workflow created successfully")
    
    return compiled_workflow