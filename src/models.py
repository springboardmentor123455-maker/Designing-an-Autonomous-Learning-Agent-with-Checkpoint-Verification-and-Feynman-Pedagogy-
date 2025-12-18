"""
Type definitions and state models for the Learning Agent System.

This module contains all TypedDict definitions and data models used
throughout the learning agent workflow.
"""

from typing import List, Dict, Any, TypedDict

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

class LearningAgentState(TypedDict):
    """Complete state for the learning agent workflow."""
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
    
    # Workflow management
    workflow_step: str
    workflow_history: List[str]
    errors: List[str]