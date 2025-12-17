"""
LangGraph workflow nodes for Milestone 1: Context Gathering and Validation.
Implements the core workflow nodes for checkpoint initialization and context management.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from src.agents.state import LearningAgentState
from src.models import GatheredContext, ContextSource
from src.tools.web_search import context_gatherer
from src.tools.llm_integration import llm_service
from config.settings import settings

logger = logging.getLogger(__name__)


async def initialize_checkpoint_node(state: LearningAgentState) -> LearningAgentState:
    """
    Initialize a checkpoint and prepare for context gathering.
    This is the entry point of the workflow.
    """
    logger.info(f"Initializing checkpoint: {state['current_checkpoint'].title}")
    
    # Update workflow tracking
    state["workflow_step"] = "checkpoint_initialized"
    state["workflow_history"].append(f"initialize_checkpoint: {datetime.now().isoformat()}")
    state["timestamp"] = datetime.now()
    
    # Start the checkpoint attempt
    if state["checkpoint_progress"]:
        state["checkpoint_progress"].start_attempt()
    
    # Initialize gathered context
    state["gathered_context"] = GatheredContext(
        checkpoint_id=state["current_checkpoint"].id
    )
    
    # Check if we have user notes
    if state["user_notes"] and state["user_notes"].strip():
        logger.info("User notes provided, will prioritize them")
        state["needs_web_search"] = False  # Start with user notes, may need web search later
    else:
        logger.info("No user notes provided, will rely on web search")
        state["needs_web_search"] = True
    
    return state


async def gather_context_node(state: LearningAgentState) -> LearningAgentState:
    """
    Gather context from user notes and/or web search.
    Prioritizes user notes but falls back to web search as needed.
    """
    logger.info("Starting context gathering")
    
    state["workflow_step"] = "gathering_context"
    state["workflow_history"].append(f"gather_context: {datetime.now().isoformat()}")
    
    checkpoint = state["current_checkpoint"]
    
    try:
        # Extract objectives as strings for the gathering process
        objectives = [obj.description for obj in checkpoint.objectives]
        
        # Gather context using the context gatherer service
        context_sources = await context_gatherer.gather_context_for_checkpoint(
            checkpoint_title=checkpoint.title,
            objectives=objectives,
            user_notes=state["user_notes"],
            prioritize_user_notes=True
        )
        
        # Update state with gathered sources
        state["context_sources"] = context_sources
        
        # Update the gathered context object
        gathered_context = state["gathered_context"]
        if gathered_context:
            for source in context_sources:
                gathered_context.add_source(source)
        
        logger.info(f"Gathered {len(context_sources)} context sources")
        
        # Log source types for debugging
        source_types = [source.source_type for source in context_sources]
        logger.info(f"Context source types: {source_types}")
        
    except Exception as e:
        error_msg = f"Context gathering failed: {str(e)}"
        logger.error(error_msg)
        state["errors"].append(error_msg)
        state["retry_count"] += 1
    
    state["timestamp"] = datetime.now()
    return state


async def validate_context_node(state: LearningAgentState) -> LearningAgentState:
    """
    Validate the quality and relevance of gathered context.
    Uses LLM to score context against checkpoint objectives.
    """
    logger.info("Starting context validation")
    
    state["workflow_step"] = "validating_context"
    state["workflow_history"].append(f"validate_context: {datetime.now().isoformat()}")
    
    checkpoint = state["current_checkpoint"]
    context_sources = state["context_sources"]
    
    if not context_sources:
        error_msg = "No context sources available for validation"
        logger.warning(error_msg)
        state["errors"].append(error_msg)
        state["context_quality_sufficient"] = False
        state["context_validation_complete"] = True
        return state
    
    try:
        # Extract objectives as strings
        objectives = [obj.description for obj in checkpoint.objectives]
        
        # Validate and score each context source
        validated_sources = await context_gatherer.validate_and_score_context(
            context_sources, objectives
        )
        
        # Update sources with validation scores
        state["context_sources"] = validated_sources
        
        # Calculate overall quality metrics
        total_sources = len(validated_sources)
        scored_sources = [s for s in validated_sources if s.relevance_score is not None]
        
        if not scored_sources:
            logger.warning("No sources could be scored")
            state["context_quality_sufficient"] = False
        else:
            # Calculate average score
            avg_score = sum(s.relevance_score for s in scored_sources) / len(scored_sources)
            
            # Count high-quality sources (score >= threshold)
            high_quality_count = len([
                s for s in scored_sources 
                if s.relevance_score >= settings.relevance_threshold
            ])
            
            # Determine if quality is sufficient
            quality_sufficient = (
                avg_score >= settings.relevance_threshold and
                high_quality_count >= 1  # At least one high-quality source
            )
            
            state["context_quality_sufficient"] = quality_sufficient
            
            logger.info(f"Context validation complete:")
            logger.info(f"  - Average relevance score: {avg_score:.2f}")
            logger.info(f"  - High-quality sources: {high_quality_count}/{total_sources}")
            logger.info(f"  - Quality sufficient: {quality_sufficient}")
        
        # Update gathered context with final metrics
        if state["gathered_context"]:
            state["gathered_context"].sources = validated_sources
            state["gathered_context"]._update_average_relevance()
        
        state["context_validation_complete"] = True
        
    except Exception as e:
        error_msg = f"Context validation failed: {str(e)}"
        logger.error(error_msg)
        state["errors"].append(error_msg)
        state["context_quality_sufficient"] = False
        state["retry_count"] = state["retry_count"] + 1
    
    state["timestamp"] = datetime.now()
    return state


async def check_context_quality_node(state: LearningAgentState) -> LearningAgentState:
    """
    Check if context quality meets requirements and decide next steps.
    This is a decision node that determines workflow direction.
    """
    logger.info("Checking context quality")
    
    state["workflow_step"] = "checking_context_quality"
    state["workflow_history"].append(f"check_context_quality: {datetime.now().isoformat()}")
    
    context_sources = state["context_sources"]
    quality_sufficient = state["context_quality_sufficient"]
    retry_count = state["retry_count"]
    
    # Log current state for debugging
    logger.info(f"Context quality check:")
    logger.info(f"  - Sources available: {len(context_sources)}")
    logger.info(f"  - Quality sufficient: {quality_sufficient}")
    logger.info(f"  - Retry count: {retry_count}")
    
    if quality_sufficient:
        logger.info("Context quality is sufficient, proceeding to next phase")
        state["workflow_step"] = "context_ready"
    else:
        # Check if we should retry or if we've exceeded retry limit
        max_retries = 2
        
        if retry_count < max_retries:
            logger.info(f"Context quality insufficient, will retry (attempt {retry_count + 1})")
            state["workflow_step"] = "retry_context_gathering"
            state["needs_web_search"] = True  # Try web search on retry
            state["retry_count"] = retry_count + 1  # Increment retry count
        else:
            logger.warning("Maximum retries exceeded, proceeding with available context")
            state["workflow_step"] = "context_ready"
            # Add warning about context quality
            state["errors"].append(
                f"Context quality below threshold after {max_retries} retries. "
                f"Proceeding with available content."
            )
    
    state["timestamp"] = datetime.now()
    return state


async def finalize_context_node(state: LearningAgentState) -> LearningAgentState:
    """
    Finalize context gathering and prepare for the next phase.
    This completes Milestone 1 workflow.
    """
    logger.info("Finalizing context gathering")
    
    state["workflow_step"] = "context_finalized" 
    state["workflow_history"].append(f"finalize_context: {datetime.now().isoformat()}")
    
    # Filter to high-quality sources if available
    context_sources = state["context_sources"]
    high_quality_sources = await context_gatherer.filter_high_quality_context(
        context_sources, min_relevance=settings.relevance_threshold
    )
    
    # Use high-quality sources if available, otherwise use all sources
    if high_quality_sources:
        final_sources = high_quality_sources
        logger.info(f"Using {len(final_sources)} high-quality sources")
    else:
        final_sources = context_sources
        logger.info(f"Using all {len(final_sources)} sources (no high-quality sources available)")
    
    # Update gathered context with final sources
    if state["gathered_context"]:
        state["gathered_context"].sources = final_sources
        state["gathered_context"]._update_average_relevance()
    
    state["context_sources"] = final_sources
    
    # Log final summary
    total_content_length = sum(len(s.content) for s in final_sources)
    avg_relevance = state["gathered_context"].average_relevance if state["gathered_context"] else None
    
    logger.info("Context gathering completed:")
    logger.info(f"  - Total sources: {len(final_sources)}")
    logger.info(f"  - Total content length: {total_content_length}")
    logger.info(f"  - Average relevance: {avg_relevance}")
    
    # Update checkpoint progress
    if state["checkpoint_progress"]:
        state["checkpoint_progress"].context_used = state["gathered_context"]
        state["checkpoint_progress"].last_updated = datetime.now()
    
    state["timestamp"] = datetime.now()
    return state


# Workflow routing functions
def should_retry_context_gathering(state: LearningAgentState) -> bool:
    """Determine if we should retry context gathering."""
    return (
        state["workflow_step"] == "retry_context_gathering" and
        state["retry_count"] < 2
    )


def is_context_ready(state: LearningAgentState) -> bool:
    """Determine if context is ready for next phase."""
    return state["workflow_step"] == "context_ready"


def is_context_finalized(state: LearningAgentState) -> bool:
    """Determine if context gathering is complete."""
    return state["workflow_step"] == "context_finalized"