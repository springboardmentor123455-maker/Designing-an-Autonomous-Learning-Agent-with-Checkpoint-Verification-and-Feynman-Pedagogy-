# app/core/graph.py
from __future__ import annotations

from typing import Callable
from langgraph.graph import StateGraph, END

from app.core.state import LearningState
from app.core.context_gatherer import gather_context_for_checkpoint
from app.core.context_validator import validate_context
from app.config import CONTEXT_RELEVANCE_THRESHOLD, MAX_CONTEXT_ATTEMPTS

from app.core.question_generator import generate_questions
from app.core.answer_evaluator import evaluate_answer

from langgraph.graph import StateGraph, END

from app.core.state import LearningState
from app.core.context_gatherer import collect_learning_context
from app.core.context_processor import build_vector_index
from app.core.question_generator import build_assessment_questions
from app.core.answer_evaluator import evaluate_user_responses
from app.core.feynman_explainer import simplify_with_feynman


# -------------------------------
# LangGraph Nodes
# -------------------------------

def define_checkpoint(state: LearningState):
    """Initialize selected checkpoint"""
    state.context = None
    state.vector_index = None
    state.questions = []
    state.responses = {}
    return state


def gather_context(state: LearningState):
    """Collect learning material"""
    material, _ = collect_learning_context(state.active_checkpoint)
    state.context = material
    state.vector_index = build_vector_index(material)
    return state


def generate_questions(state: LearningState):
    """Generate assessment questions"""
    state.questions = build_assessment_questions(state.active_checkpoint)
    return state


def evaluate_answers(state: LearningState):
    """Evaluate learner understanding"""
    answers = list(state.responses.values())
    score, weak = evaluate_user_responses(state.questions, answers)
    state.score = score
    state.weak_topics = weak
    return state


def feynman_teaching(state: LearningState):
    """Simplify weak concepts using Feynman technique"""
    explanations = []
    for topic in state.weak_topics:
        explanations.append(
            simplify_with_feynman(
                question=topic,
                wrong_answer="",
                context=state.context
            )
        )
    state.feynman_explanations = explanations
    return state


# -------------------------------
# Routing Logic
# -------------------------------

def route_after_evaluation(state: LearningState):
    if state.score >= state.active_checkpoint.pass_score:
        return "complete"
    return "feynman"


# -------------------------------
# Build LangGraph
# -------------------------------

def build_learning_graph():
    graph = StateGraph(LearningState)

    graph.add_node("define", define_checkpoint)
    graph.add_node("context", gather_context)
    graph.add_node("questions", generate_questions)
    graph.add_node("evaluate", evaluate_answers)
    graph.add_node("feynman", feynman_teaching)

    graph.set_entry_point("define")

    graph.add_edge("define", "context")
    graph.add_edge("context", "questions")
    graph.add_edge("questions", "evaluate")

    graph.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {
            "complete": END,
            "feynman": "feynman"
        }
    )

    graph.add_edge("feynman", END)

    return graph.compile()
