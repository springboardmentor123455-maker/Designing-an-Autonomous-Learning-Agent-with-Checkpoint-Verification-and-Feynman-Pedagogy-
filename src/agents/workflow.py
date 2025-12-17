"""
LangGraph workflow definition for Milestone 1.
Builds the complete workflow graph for checkpoint initialization and context gathering.
"""

import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from src.agents.state import LearningAgentState
from src.agents.milestone1_nodes import (
    initialize_checkpoint_node,
    gather_context_node,
    validate_context_node,
    check_context_quality_node,
    finalize_context_node,
    should_retry_context_gathering,
    is_context_ready,
    is_context_finalized
)

logger = logging.getLogger(__name__)


def create_milestone1_workflow() -> CompiledStateGraph:
    """
    Create the LangGraph workflow for Milestone 1: Context Gathering and Validation.
    
    Workflow:
    1. Initialize checkpoint
    2. Gather context (user notes + web search)
    3. Validate context quality
    4. Check if quality is sufficient
    5. If not sufficient and retries available, retry gathering
    6. Finalize context for next phase
    """
    
    # Create the state graph
    workflow = StateGraph(LearningAgentState)
    
    # Add nodes
    workflow.add_node("initialize_checkpoint", initialize_checkpoint_node)
    workflow.add_node("gather_context", gather_context_node) 
    workflow.add_node("validate_context", validate_context_node)
    workflow.add_node("check_context_quality", check_context_quality_node)
    workflow.add_node("finalize_context", finalize_context_node)
    
    # Define the workflow edges
    
    # Start with checkpoint initialization
    workflow.add_edge(START, "initialize_checkpoint")
    
    # After initialization, always gather context
    workflow.add_edge("initialize_checkpoint", "gather_context")
    
    # After gathering, always validate
    workflow.add_edge("gather_context", "validate_context")
    
    # After validation, check quality
    workflow.add_edge("validate_context", "check_context_quality")
    
    # Conditional edges from quality check
    workflow.add_conditional_edges(
        "check_context_quality",
        _route_after_quality_check,
        {
            "retry": "gather_context",     # Retry context gathering
            "finalize": "finalize_context", # Proceed to finalization
        }
    )
    
    # From finalize_context to END
    workflow.add_edge("finalize_context", END)
    
    # Compile the workflow
    compiled_workflow = workflow.compile()
    
    logger.info("Milestone 1 workflow created successfully")
    return compiled_workflow


def _route_after_quality_check(state: LearningAgentState) -> str:
    """Route decision after context quality check."""
    
    workflow_step = state["workflow_step"]
    retry_count = state["retry_count"]
    
    # Fix: Check both retry step AND retry count
    if workflow_step == "retry_context_gathering" and retry_count <= 2:
        logger.info(f"Routing to retry context gathering (attempt {retry_count + 1})")
        return "retry"
    else:
        logger.info(f"Routing to finalize context (retries: {retry_count})")
        return "finalize"


class Milestone1WorkflowManager:
    """High-level manager for running the Milestone 1 workflow."""
    
    def __init__(self):
        self.workflow = create_milestone1_workflow()
    
    async def run_context_gathering(
        self,
        initial_state: LearningAgentState,
        config: Dict[str, Any] = None
    ) -> LearningAgentState:
        """
        Run the complete context gathering workflow.
        
        Args:
            initial_state: Initial state with checkpoint and optional user notes
            config: Optional configuration for the workflow run
            
        Returns:
            Final state with gathered and validated context
        """
        logger.info("Starting Milestone 1 workflow execution")
        
        try:
            # Execute the workflow
            final_state = await self.workflow.ainvoke(
                initial_state,
                config=config or {}
            )
            
            # Log execution summary
            self._log_execution_summary(final_state)
            
            return final_state
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            
            # Update state with error information
            initial_state["errors"].append(f"Workflow execution failed: {str(e)}")
            initial_state["workflow_step"] = "failed"
            
            return initial_state
    
    def _log_execution_summary(self, final_state: LearningAgentState) -> None:
        """Log a summary of the workflow execution."""
        
        checkpoint_title = final_state["current_checkpoint"].title if final_state["current_checkpoint"] else "Unknown"
        workflow_step = final_state["workflow_step"]
        context_sources_count = len(final_state["context_sources"])
        errors_count = len(final_state["errors"])
        retry_count = final_state["retry_count"]
        
        logger.info("Workflow execution completed:")
        logger.info(f"  - Checkpoint: {checkpoint_title}")
        logger.info(f"  - Final step: {workflow_step}")
        logger.info(f"  - Context sources: {context_sources_count}")
        logger.info(f"  - Retry count: {retry_count}")
        logger.info(f"  - Errors: {errors_count}")
        
        # Log workflow path for debugging
        history = final_state["workflow_history"]
        logger.debug(f"  - Workflow path: {' -> '.join(history)}")
        
        if final_state["gathered_context"]:
            avg_relevance = final_state["gathered_context"].average_relevance
            total_length = final_state["gathered_context"].total_length
            logger.info(f"  - Average relevance: {avg_relevance}")
            logger.info(f"  - Total content length: {total_length}")
        
        # Log any errors
        if final_state["errors"]:
            for error in final_state["errors"]:
                logger.warning(f"  - Error: {error}")
    
    async def get_workflow_status(self, state: LearningAgentState) -> Dict[str, Any]:
        """Get current workflow status for monitoring."""
        
        gathered_context = state["gathered_context"]
        
        status = {
            "workflow_step": state["workflow_step"],
            "context_sources_count": len(state["context_sources"]),
            "context_validation_complete": state["context_validation_complete"],
            "context_quality_sufficient": state["context_quality_sufficient"],
            "retry_count": state["retry_count"],
            "error_count": len(state["errors"]),
            "has_user_notes": bool(state["user_notes"] and state["user_notes"].strip()),
            "timestamp": state["timestamp"].isoformat(),
        }
        
        if gathered_context:
            status.update({
                "total_content_length": gathered_context.total_length,
                "average_relevance": gathered_context.average_relevance,
                "gathered_at": gathered_context.gathered_at.isoformat()
            })
        
        return status


# Global workflow manager instance
milestone1_manager = Milestone1WorkflowManager()