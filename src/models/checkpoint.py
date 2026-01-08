"""Data models for learning checkpoints and gathered context."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Checkpoint:
    """
    Represents a learning checkpoint - a specific topic with learning objectives.
    
    This is the fundamental unit of learning in the agent. Each checkpoint
    defines what the learner needs to understand.
    """
    topic: str
    objectives: List[str]
    difficulty_level: str = "beginner"  # beginner, intermediate, advanced
    estimated_time_minutes: int = 30
    prerequisites: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        return f"Checkpoint: {self.topic} ({len(self.objectives)} objectives)"


@dataclass
class GatheredContext:
    """
    Represents context/information gathered for a checkpoint.
    
    This could be from user notes, web search, documentation, etc.
    """
    source: str  # e.g., "user_notes", "web_search", "documentation"
    content: str
    gathered_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    relevance_score: Optional[float] = None  # 0.0 to 1.0, set during validation
    
    def __str__(self) -> str:
        preview = self.content[:100] + "..." if len(self.content) > 100 else self.content
        return f"Context from {self.source}: {preview}"
