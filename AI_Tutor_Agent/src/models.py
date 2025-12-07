from pydantic import BaseModel, Field
from typing import List

class LearningCheckpoint(BaseModel):
    """
    Formal definition of a Learning Checkpoint as required by Milestone 1.
    """
    topic: str = Field(..., description="The main subject of this checkpoint")
    objectives: List[str] = Field(..., description="Specific concepts the user must learn")
    # This field is required by the project spec
    success_criteria: str = Field(
        default="User must demonstrate understanding of key concepts.", 
        description="Criteria for passing this checkpoint"
    )