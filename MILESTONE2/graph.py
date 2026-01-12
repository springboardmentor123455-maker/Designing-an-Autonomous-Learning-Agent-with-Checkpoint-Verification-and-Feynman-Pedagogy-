# =====================================================
# Environment setup
# =====================================================
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"

from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from langsmith import traceable
from langchain_groq import ChatGroq

from semantic_analysis import compute_similarity, expand_objectives

# =====================================================
# LLMS
# =====================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# =====================================================
# State
# =====================================================
class LearningState(TypedDict, total=False):
    checkpoint: object
    questions: List[str]
    answers: Dict[int, str]
    results: List[dict]
    feedback: str

    # Milestone 3
    weak_concepts: List[str]
    feynman_explanations: Dict[str, str]
    average_score: int

# =====================================================
# Nodes
# =====================================================
def generate_questions(state: LearningState):
    cp = state["checkpoint"]

    questions = [
        f"Explain {cp.objectives[0]}.",
        f"Describe {cp.objectives[1]} in detail.",
        f"Why is {cp.objectives[2]} important?",
        f"Give a real-world application of {cp.topic}."
    ]

    return {"questions": questions}

def evaluate_questions(state: LearningState):
    cp = state["checkpoint"]
    reference = expand_objectives(cp.topic, cp.objectives)

    results = []

    for idx, question in enumerate(state["questions"]):
        answer = state["answers"].get(idx, "")

        similarity = compute_similarity(reference, answer)
        score = int(similarity * 100)
        status = "PASSED" if score >= 60 else "FAILED"

        results.append({
            "question": question,
            "answer": answer,
            "semantic_score": round(similarity, 3),
            "final_score": score,
            "status": status
        })

    return {"results": results}

def identify_knowledge_gaps(state: LearningState):
    weak = [r["question"] for r in state["results"] if r["final_score"] < 60]
    avg = sum(r["final_score"] for r in state["results"]) // len(state["results"])

    return {
        "weak_concepts": weak,
        "average_score": avg
    }

@traceable(name="Feynman Teaching Module")
def feynman_teaching(state: LearningState):
    explanations = {}

    for concept in state["weak_concepts"]:
        prompt = f"""
Explain the following concept using the Feynman Technique.

Concept:
{concept}

Rules:
- Use very simple words
- Use real-life analogies
- Avoid technical jargon
- Assume the learner is a beginner
"""

        response = llm.invoke(prompt)
        explanations[concept] = response.content.strip()

    return {"feynman_explanations": explanations}

@traceable(name="Overall Feedback")
def generate_feedback(state: LearningState):
    summary = "\n".join(
        [f"Q{i+1}: {r['status']} ({r['final_score']})"
         for i, r in enumerate(state["results"])]
    )

    prompt = f"""
Checkpoint: {state["checkpoint"].topic}

Results:
{summary}

Give short overall feedback.
"""

    response = llm.invoke(prompt)
    return {"feedback": response.content}

# =====================================================
# Routing Logic
# =====================================================
def route_after_gap_check(state: LearningState):
    if state["average_score"] < 60:
        return "feynman_teaching"
    return "generate_feedback"

# =====================================================
# Graph Builders
# =====================================================
def build_question_graph():
    graph = StateGraph(LearningState)
    graph.add_node("generate_questions", generate_questions)
    graph.set_entry_point("generate_questions")
    graph.add_edge("generate_questions", END)
    return graph.compile()

def build_evaluation_graph():
    graph = StateGraph(LearningState)

    graph.add_node("evaluate_questions", evaluate_questions)
    graph.add_node("identify_gaps", identify_knowledge_gaps)
    graph.add_node("feynman_teaching", feynman_teaching)
    graph.add_node("generate_feedback", generate_feedback)

    graph.set_entry_point("evaluate_questions")

    graph.add_edge("evaluate_questions", "identify_gaps")

    graph.add_conditional_edges(
        "identify_gaps",
        route_after_gap_check,
        {
            "feynman_teaching": "feynman_teaching",
            "generate_feedback": "generate_feedback"
        }
    )

    graph.add_edge("feynman_teaching", "generate_feedback")
    graph.add_edge("generate_feedback", END)

    return graph.compile()
