"""
Type definitions and state models for the Learning Agent System.

This module contains all TypedDict definitions and data models used
throughout the learning agent workflow.
"""

from typing import List, Dict, Any, TypedDict, Optional

class Checkpoint(TypedDict):
    """Learning checkpoint definition."""
    id: str
    title: str
    description: str
    requirements: List[str]

class Material(TypedDict):
    """Learning material definition."""
    id: str
    title: str
    content: str
    source: str

class ProcessedContext(TypedDict):
    """Processed context chunk with embeddings."""
    chunk_id: str
    text: str
    embedding: List[float]
    metadata: Dict[str, Any]

class GeneratedQuestion(TypedDict):
    """Generated question with context mapping."""
    question_id: str
    question: str
    context_chunks: List[str]
    expected_concepts: List[str]

class LearnerAnswer(TypedDict):
    """Simulated learner answer."""
    question_id: str
    answer_text: str
    confidence: float

class VerificationResult(TypedDict):
    """Question verification result with scoring."""
    question_id: str
    learner_answer: str
    score: float
    feedback: str
    scoring_details: Dict[str, Any]

class LearningPath(TypedDict):
    """Complete learning path with multiple checkpoints."""
    id: str
    title: str
    description: str
    checkpoints: List[Checkpoint]

class LearningAgentState(TypedDict):
    """Complete state for the learning agent workflow."""
    # Learning Path Management
    learning_path: LearningPath
    current_checkpoint_index: int
    completed_checkpoints: List[str]
    total_checkpoints: int
    
    # Milestone 1 state
    current_checkpoint: Checkpoint
    collected_materials: List[Material]
    summary: str
    milestone1_score: float
    
    # Milestone 2 extensions
    processed_context: List[ProcessedContext]
    generated_questions: List[GeneratedQuestion]
    verification_results: List[VerificationResult]
    score_percentage: float
    meets_threshold: bool
    
    # Feynman Teaching (Milestone 3)
    feynman_retry_count: int
    feynman_retry_requested: bool
    feynman_explanations: List[Dict[str, Any]]
    
    # User Materials & Validation
    user_uploaded_notes_path: Optional[List[str]]
    materials_validation: Optional[Dict[str, Any]]
    
    # Workflow management
    workflow_step: str
    workflow_history: List[str]
    errors: List[str]