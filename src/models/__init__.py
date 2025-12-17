"""
Data models for the autonomous learning agent system.
Defines the core structures for checkpoints, learning objectives, and progress tracking.
"""

from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid


class DifficultyLevel(str, Enum):
    """Difficulty levels for learning checkpoints."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"


class QuestionType(str, Enum):
    """Types of questions that can be generated."""
    MULTIPLE_CHOICE = "multiple_choice"
    OPEN_ENDED = "open_ended"
    MIXED = "mixed"


class CheckpointStatus(str, Enum):
    """Status of a learning checkpoint."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class LearningObjective(BaseModel):
    """Individual learning objective within a checkpoint."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Brief title of the objective")
    description: str = Field(..., description="Detailed description of what should be learned")
    keywords: List[str] = Field(default_factory=list, description="Key terms related to this objective")
    importance_weight: float = Field(default=1.0, ge=0.1, le=2.0, description="Weight for assessment (0.1-2.0)")


class SuccessCriteria(BaseModel):
    """Defines what constitutes successful completion of a checkpoint."""
    minimum_score: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum score to pass (0.0-1.0)")
    required_objectives: List[str] = Field(default_factory=list, description="IDs of objectives that must be mastered")
    max_attempts: int = Field(default=3, ge=1, description="Maximum number of attempts before requiring intervention")
    time_limit_minutes: Optional[int] = Field(default=None, ge=5, description="Optional time limit for assessment")


class Checkpoint(BaseModel):
    """Main checkpoint data structure defining a learning milestone."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Clear, descriptive title of the checkpoint")
    description: str = Field(..., description="Detailed description of the checkpoint content")
    
    # Learning structure
    objectives: List[LearningObjective] = Field(..., min_items=1, description="Learning objectives for this checkpoint")
    prerequisites: List[str] = Field(default_factory=list, description="IDs of prerequisite checkpoints")
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    
    # Assessment configuration
    success_criteria: SuccessCriteria = Field(default_factory=SuccessCriteria)
    question_type: QuestionType = Field(default=QuestionType.MIXED)
    estimated_duration_minutes: int = Field(default=30, ge=5, description="Expected time to complete")
    
    # Content guidance
    topic_keywords: List[str] = Field(default_factory=list, description="Keywords for content search")
    context_requirements: str = Field(default="", description="Specific requirements for context gathering")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    
    @validator('objectives')
    def validate_objectives(cls, v):
        if len(v) == 0:
            raise ValueError("At least one learning objective is required")
        return v


class ContextSource(BaseModel):
    """Represents a source of learning context."""
    source_type: Literal["user_notes", "web_search", "document"] = Field(...)
    content: str = Field(..., description="The actual content text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the source")
    relevance_score: Optional[float] = Field(default=None, ge=0.0, le=5.0, description="Relevance score (0-5)")
    timestamp: datetime = Field(default_factory=datetime.now)


class GatheredContext(BaseModel):
    """Container for all context gathered for a checkpoint."""
    checkpoint_id: str = Field(...)
    sources: List[ContextSource] = Field(default_factory=list)
    total_length: int = Field(default=0, description="Total character count of all context")
    average_relevance: Optional[float] = Field(default=None, description="Average relevance score across sources")
    gathered_at: datetime = Field(default_factory=datetime.now)
    
    def add_source(self, source: ContextSource) -> None:
        """Add a context source and update metrics."""
        self.sources.append(source)
        self.total_length += len(source.content)
        self._update_average_relevance()
    
    def _update_average_relevance(self) -> None:
        """Update the average relevance score."""
        scores = [s.relevance_score for s in self.sources if s.relevance_score is not None]
        if scores:
            self.average_relevance = sum(scores) / len(scores)


class CheckpointProgress(BaseModel):
    """Tracks progress and performance for a specific checkpoint."""
    checkpoint_id: str = Field(...)
    learner_id: str = Field(default="default", description="Identifier for the learner")
    
    # Status tracking
    status: CheckpointStatus = Field(default=CheckpointStatus.NOT_STARTED)
    attempts: int = Field(default=0, ge=0)
    current_attempt_start: Optional[datetime] = Field(default=None)
    
    # Performance tracking
    scores: List[float] = Field(default_factory=list, description="Scores from each attempt")
    best_score: float = Field(default=0.0, ge=0.0, le=1.0)
    completion_time_minutes: Optional[int] = Field(default=None, ge=0)
    
    # Context and assessment history
    context_used: Optional[GatheredContext] = Field(default=None)
    questions_generated: int = Field(default=0, ge=0)
    feynman_explanations_used: int = Field(default=0, ge=0)
    
    # Timestamps
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    def start_attempt(self) -> None:
        """Start a new attempt at the checkpoint."""
        self.attempts += 1
        self.current_attempt_start = datetime.now()
        if self.status == CheckpointStatus.NOT_STARTED:
            self.status = CheckpointStatus.IN_PROGRESS
            self.started_at = datetime.now()
        self.last_updated = datetime.now()
    
    def complete_attempt(self, score: float) -> None:
        """Complete the current attempt with a score."""
        self.scores.append(score)
        self.best_score = max(self.best_score, score)
        
        if self.current_attempt_start:
            duration = (datetime.now() - self.current_attempt_start).total_seconds() / 60
            self.completion_time_minutes = int(duration)
        
        self.last_updated = datetime.now()
    
    def mark_completed(self) -> None:
        """Mark the checkpoint as successfully completed."""
        self.status = CheckpointStatus.COMPLETED
        self.completed_at = datetime.now()
        self.last_updated = datetime.now()
    
    def mark_failed(self) -> None:
        """Mark the checkpoint as failed."""
        self.status = CheckpointStatus.FAILED
        self.last_updated = datetime.now()


class LearningPath(BaseModel):
    """Represents a complete learning path with multiple checkpoints."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Title of the learning path")
    description: str = Field(..., description="Description of what this path covers")
    
    # Structure
    checkpoint_ids: List[str] = Field(..., min_items=1, description="Ordered list of checkpoint IDs")
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    estimated_total_hours: float = Field(default=1.0, ge=0.1, description="Estimated total completion time")
    
    # Metadata
    subject_area: str = Field(default="", description="Subject or domain area")
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('checkpoint_ids')
    def validate_checkpoint_ids(cls, v):
        if len(v) == 0:
            raise ValueError("At least one checkpoint is required")
        return v


class LearningSession(BaseModel):
    """Represents an active learning session."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    learner_id: str = Field(default="default")
    learning_path_id: str = Field(...)
    
    # Session state
    current_checkpoint_id: Optional[str] = Field(default=None)
    current_checkpoint_index: int = Field(default=0, ge=0)
    session_active: bool = Field(default=True)
    
    # Progress tracking
    checkpoints_completed: List[str] = Field(default_factory=list)
    total_score: float = Field(default=0.0, ge=0.0)
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(default=None)
    
    def advance_to_next_checkpoint(self, checkpoint_ids: List[str]) -> bool:
        """Advance to the next checkpoint in the path. Returns True if successful."""
        if self.current_checkpoint_id:
            self.checkpoints_completed.append(self.current_checkpoint_id)
        
        self.current_checkpoint_index += 1
        
        if self.current_checkpoint_index >= len(checkpoint_ids):
            # Learning path completed
            self.current_checkpoint_id = None
            self.session_active = False
            self.completed_at = datetime.now()
            return False
        
        self.current_checkpoint_id = checkpoint_ids[self.current_checkpoint_index]
        self.last_activity = datetime.now()
        return True