from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

class TutorStep(str, Enum):
    SETUP = "setup"
    PLAN = "plan"
    GENERATING = "generating"
    STUDY = "study"
    QUIZ = "quiz"
    GRADING = "grading"
    SUCCESS = "success"
    FAIL = "fail"

@dataclass
class StudyPlanItem:
    id: int
    topic: str
    objective: str
    completed: bool = False
    score: int = 0
    icon: str = "📚"
    color: str = "#4f46e5"

@dataclass
class QuizItem:
    question: str
    answer: str = ""
    score: int = 0
    feedback: str = ""
    concept: str = ""
    max_score: int = 20

@dataclass
class LearningMetrics:
    modules_completed: int = 0
    total_score: int = 0
    average_score: float = 0.0
    time_spent: int = 0  # in minutes
    streak_days: int = 0

@dataclass
class TutorSession:
    current_step: TutorStep = TutorStep.SETUP
    main_topic: str = ""
    study_plan: List[StudyPlanItem] = field(default_factory=list)
    current_module: Optional[StudyPlanItem] = None
    lesson_content: str = ""
    quiz_questions: List[QuizItem] = field(default_factory=list)
    attempt_count: int = 1
    max_attempts: int = 2
    failed_concepts: List[str] = field(default_factory=list)
    metrics: LearningMetrics = field(default_factory=LearningMetrics)