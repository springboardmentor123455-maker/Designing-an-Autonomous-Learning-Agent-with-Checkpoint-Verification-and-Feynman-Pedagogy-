# =====================================================
# Environment setup
# =====================================================
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in .env")

if not TAVILY_API_KEY:
    raise ValueError("❌ TAVILY_API_KEY not found in .env")

# =====================================================
# Imports
# =====================================================
from typing import TypedDict
from checkpoints import CHECKPOINTS, Checkpoint
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from tavily import TavilyClient

# =====================================================
# Clients
# =====================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)

tavily = TavilyClient(api_key=TAVILY_API_KEY)

# =====================================================
# State definition
# =====================================================
class LearningState(TypedDict, total=False):
    checkpoint_index: int
    checkpoint: Checkpoint
    context: str
    questions: str
    hints: str
    answers: str
    score: int
    feedback: str
    followup_question: str
    status: str
    data_source: str

# =====================================================
# Graph Nodes
# =====================================================

def define_checkpoint(state: LearningState):
    idx = state["checkpoint_index"]
    state["checkpoint"] = CHECKPOINTS[idx]
    return state


def gather_context(state: LearningState):
    cp = state["checkpoint"]
    query = f"{cp.topic} computer vision explanation for beginners"

    results = tavily.search(query=query, max_results=3)

    docs = []
    for r in results.get("results", []):
        docs.append(r.get("content", ""))

    state["context"] = "\n".join(docs)
    state["data_source"] = "Tavily Web Search"
    return state


def generate_questions(state: LearningState):
    cp = state["checkpoint"]

    prompt = f"""
You are a Computer Vision tutor.

Topic: {cp.topic}
Objectives:
{cp.objectives}

Generate:
1. One short-answer question
2. One MCQ with 4 options
3. One conceptual "why" question

Format clearly.
"""

    response = llm.invoke(prompt)
    state["questions"] = response.content
    return state


def generate_hints(state: LearningState):
    cp = state["checkpoint"]

    prompt = f"""
The learner is struggling with the topic: {cp.topic}

Provide:
Hint 1: Very small clue
Hint 2: Moderate explanation
Hint 3: Almost full answer
"""

    response = llm.invoke(prompt)
    state["hints"] = response.content
    return state


def evaluate_answers(state: LearningState):
    prompt = f"""
Evaluate the learner answers using the context.

Context:
{state.get("context", "")}

Questions:
{state.get("questions", "")}

Learner Answers:
{state.get("answers", "")}

Return:
Score (0-100)
Strengths
Weaknesses
What to revise next
"""

    response = llm.invoke(prompt)
    text = response.content

    digits = "".join(filter(str.isdigit, text))
    score = int(digits[:3]) if digits else 60

    state["score"] = score
    state["feedback"] = text
    state["status"] = "PASSED" if score >= 70 else "RETRY"
    return state


def generate_followup(state: LearningState):
    cp = state["checkpoint"]
    score = state.get("score", 0)

    level = "advanced application-based" if score >= 85 else "simple conceptual"

    prompt = f"""
Generate ONE {level} follow-up question
for the topic: {cp.topic}
"""

    response = llm.invoke(prompt)
    state["followup_question"] = response.content
    return state

# =====================================================
# Graph Builder
# =====================================================
def build_graph():
    graph = StateGraph(LearningState)

    graph.add_node("define_checkpoint", define_checkpoint)
    graph.add_node("gather_context", gather_context)
    graph.add_node("generate_questions", generate_questions)
    graph.add_node("generate_hints", generate_hints)
    graph.add_node("evaluate_answers", evaluate_answers)
    graph.add_node("generate_followup", generate_followup)

    graph.set_entry_point("define_checkpoint")

    graph.add_edge("define_checkpoint", "gather_context")
    graph.add_edge("gather_context", "generate_questions")
    graph.add_edge("generate_questions", "evaluate_answers")
    graph.add_edge("evaluate_answers", "generate_followup")

    graph.add_conditional_edges(
        "evaluate_answers",
        lambda state: "end" if state["status"] == "PASSED" else "retry",
        {
            "end": END,
            "retry": "generate_hints"
        }
    )

    graph.add_edge("generate_hints", "gather_context")

    return graph.compile()
