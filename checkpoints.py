from typing import TypedDict, List, Dict


class Checkpoint(TypedDict):
    id: str
    topic: str
    objectives: List[str]
    success_criteria: str


CHECKPOINTS: Dict[str, Checkpoint] = {
    "1": {
        "id": "1",
        "topic": "Introduction to Machine Learning",
        "objectives": [
            "define machine learning",
            "explain the difference between AI and ML",
            "describe how ML learns from data",
        ],
        "success_criteria": (
            "Learner can define ML, differentiate AI vs ML, "
            "and explain data-driven learning."
        ),
    },
    "2": {
        "id": "2",
        "topic": "Types of Machine Learning",
        "objectives": [
            "define supervised, unsupervised, and reinforcement learning",
            "give simple real-world examples for each type",
        ],
        "success_criteria": (
            "Learner can list ML types and give correct examples."
        ),
    },
    "3": {
        "id": "3",
        "topic": "Supervised Learning Basics",
        "objectives": [
            "explain the concept of labeled data",
            "differentiate regression and classification",
            "give examples of regression and classification problems",
        ],
        "success_criteria": (
            "Learner distinguishes regression vs classification with examples."
        ),
    },
    "4": {
        "id": "4",
        "topic": "Regression Algorithms",
        "objectives": [
            "explain linear regression in simple terms",
            "describe the idea of fitting a line to data",
            "understand what prediction means in regression",
        ],
        "success_criteria": (
            "Learner can describe linear regression and interpret simple predictions."
        ),
    },
    "5": {
        "id": "5",
        "topic": "Classification Algorithms",
        "objectives": [
            "explain how classification assigns labels",
            "give examples of binary and multi-class classification",
            "describe simple algorithms like KNN or Logistic Regression",
        ],
        "success_criteria": (
            "Learner can describe classification and give real-world examples."
        ),
    },
}
