from pydantic import BaseModel
from typing import List

class LearningCheckpoint(BaseModel):
    id: int
    topic: str
    objectives: List[str]

# The Map
course_curriculum = [
    LearningCheckpoint(
        id=1,
        topic="Tree Terminology",
        objectives=["Define Root, Node, and Leaf", "Calculate Height and Depth"]
    ),
    LearningCheckpoint(
        id=2,
        topic="Binary Search Trees (BST)",
        objectives=["Explain BST properties", "Visualize node insertion"]
    )
]