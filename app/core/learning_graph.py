# app/core/learning_graph.py
from langgraph.graph import StateGraph, END
from app.core.graph import build_graph as milestone1_graph
from app.core.question_generator import generate_questions
from app.core.answer_evaluator import evaluate_answer

def build_learning_graph():
    graph = milestone1_graph()

    def node_generate_questions(state):
        context = "\n".join(d.page_content for d in state["gathered_context"])
        state["questions"] = generate_questions(context)
        return state

    def node_evaluate_answers(state):
        context = "\n".join(d.page_content for d in state["gathered_context"])
        scores = []
        for q in state["questions"]:
            ans = input(f"\nAnswer: {q}\n> ")
            score = evaluate_answer(q, ans, context)
            scores.append(score)

        state["average_score"] = sum(scores) / len(scores)
        return state

    graph.add_node("generate_questions", node_generate_questions)
    graph.add_node("evaluate_answers", node_evaluate_answers)

    graph.add_edge(END, "generate_questions")
    graph.add_edge("generate_questions", "evaluate_answers")

    return graph.compile()
