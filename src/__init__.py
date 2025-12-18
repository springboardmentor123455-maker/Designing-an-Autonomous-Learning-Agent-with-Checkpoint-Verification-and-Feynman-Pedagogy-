"""
Learning Agent Source Package

This package contains all the modular components for the unified learning agent
that combines Milestone 1 and Milestone 2 functionality.

Modules:
- models: Core type definitions and state models
- context_processor: Text chunking and embedding functionality
- llm_service: LLM interactions for questions and scoring
- workflow_nodes: All workflow node functions
- workflow: LangGraph workflow creation and routing
- main: Main execution logic and user interface
- sample_data: Sample checkpoints and materials for testing
"""

from .models import (
    Checkpoint,
    Material,
    ProcessedContext,
    GeneratedQuestion,
    LearningAgentState
)

from .context_processor import ContextProcessor
from .llm_service import LLMService
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
from .workflow import create_unified_workflow
from .main import run_learning_session, interactive_mode, process_user_answers
from .sample_data import create_sample_checkpoint, create_sample_materials, create_multiple_checkpoints
from .interactive import (
    display_welcome, select_checkpoint, display_question, 
    display_results, get_user_evaluation, display_system_metrics
)

__all__ = [
    # Models
    'Checkpoint',
    'Material',
    'ProcessedContext',
    'GeneratedQuestion',
    'LearningAgentState',
    
    # Services
    'ContextProcessor',
    'LLMService',
    
    # Workflow nodes
    'initialize_node',
    'collect_materials_node',
    'summarize_materials_node',
    'evaluate_milestone1_node',
    'process_context_node',
    'generate_questions_node',
    'verify_understanding_node',
    'check_threshold_node',
    'complete_checkpoint_node',
    'feynman_placeholder_node',

    
    # Workflow and execution
    'create_unified_workflow',
    'run_learning_session',
    'interactive_mode',
    'process_user_answers',
    
    # Sample data
    'create_sample_checkpoint',
    'create_sample_materials',
    'create_multiple_checkpoints',
    
    # Interactive functions
    'display_welcome',
    'select_checkpoint', 
    'display_question',
    'display_results',
    'get_user_evaluation',
    'display_system_metrics'
]