from typing import List, Literal

from pydantic import BaseModel, Field


class ValidatorStructure(BaseModel):
    evaluation: Literal['approved', 'needs_improvement'] = Field(..., description="Evaluation based on topic and objective.")
    score : int = Field(description='Score out of 10', ge=0, le=10)

class QuestionGeneratorStruc(BaseModel):
    question_1 :str = Field(description='Generator  question_1 based on context')
    question_2 :str = Field(description='Generator question_2 based on context')
    question_3 :str = Field(description='Generator question_3 based on context')
    # question_4 :str = Field(description='Generator question_4 based on context')
    # question_5 :str = Field(description='Generator question_5 based on context')

class PerQuestionScore(BaseModel):
    scores: List[int] = Field(
        description="Score (0-100) for each question, in the same order as the questions"
    )

class LearningGap(BaseModel):
    question_number: int = Field(
        description="Question number (1-based) where misunderstanding occurred"
    )
    gap: str = Field(
        description="Brief description of the missing or incorrect concept"
    )
class GapDetectionOutput(BaseModel):
    gaps: List[LearningGap] = Field(
        description="Detected learning gaps; empty list if no gaps"
    )

class FeynmanTeachingStruc(BaseModel):
    explanation: str = Field(
        description="Simple explanation addressing the learning gaps using the Feynman technique"
    )