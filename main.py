# src/main.py

from dotenv import load_dotenv
load_dotenv()

from src.graph import build_graph
from src.checkpoints import CHECKPOINTS

PASS_THRESHOLD = 70


def run_single_checkpoint(checkpoint, user_answers=None, quiz_round=1):
    graph = build_graph()

    state = {
        "checkpoint": checkpoint,
        "user_answers": user_answers,   # MUST be dict {question: answer}
        "quiz_round": quiz_round
    }

    final_state = graph.invoke(state)

    return {
        "questions": final_state.get("questions", []),
        "score": final_state.get("score", 0),
        "passed": final_state.get("score", 0) >= PASS_THRESHOLD,
        "feynman_explanations": final_state.get("feynman_explanations", []),
        "per_question_scores": final_state.get("per_question_scores", []),
        "feedback": final_state.get("feedback", [])
    }

def run_learning_path():
    """
    Autonomous mode: runs all checkpoints until failure.
    """
    summary = []

    for cp in CHECKPOINTS:
        # ✅ Always pass empty dict in autonomous mode
        result = run_single_checkpoint(cp, user_answers={})

        summary.append({
            "checkpoint": cp.get("topic", "Unknown"),
            "score": result["score"],
            "passed": result["passed"]
        })

        if not result["passed"]:
            break

    return {
        "summary": summary,
        "completed": all(x["passed"] for x in summary)
    }
