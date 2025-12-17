from typing import TypedDict, List
from langgraph.graph import StateGraph, END
import json
from pathlib import Path

from gemini_client import gemini_evaluate, gemini_feynman
import json


EVALUATION_RULES = {
    "Newton's Second Law": [
        "force",
        "mass",
        "acceleration",
        "f=ma"
    ],
    "Ohm's Law": [
        "voltage",
        "current",
        "resistance",
        "v=ir"
    ],
    "IoT Fundamentals & Architecture": [
        "device",
        "sensor",
        "cloud",
        "gateway",
        "data"
    ],
    "Sensor & Actuator Specifications": [
        "accuracy",
        "range",
        "resolution",
        "sampling"
    ],
    "IoT Communication Protocols": [
        "mqtt",
        "http",
        "protocol",
        "publish",
        "subscribe"
    ]
}
FEYNMAN_EXPLANATIONS = {
    "IoT Fundamentals & Architecture": (
        "Think of IoT like a human body. Sensors are the senses (eyes, ears), "
        "the gateway is the nervous system, and the cloud is the brain where "
        "decisions are made using the collected data."
    ),

    "Sensor & Actuator Specifications": (
        "A sensor is like a thermometer that measures temperature, while an "
        "actuator is like a fan that turns on when it gets hot. Specifications "
        "tell us how accurate and reliable these devices are."
    ),

    "IoT Communication Protocols": (
        "Communication protocols are rules for how devices talk to each other. "
        "MQTT works like a message delivery service where devices publish and "
        "subscribe to messages instead of talking directly."
    ),

    "IoT Security & Data Privacy": (
        "IoT security is like locking your house. Authentication checks who can "
        "enter, and encryption hides information so attackers cannot read it."
    ),

    "Edge Computing & Cloud Integration in IoT": (
        "Edge computing is like making quick decisions locally, while the cloud "
        "is used for deeper analysis later. This helps reduce delay and save bandwidth."
    )
}


class AgentState(TypedDict):
    current_checkpoint: int
    checkpoints: list
    user_input: str
    score: float
    passed: bool
    explanation_level: str  # "normal" or "feynman"



def load_checkpoints():
    path = Path(__file__).parent / "checkpoints" / "ckpts_sample.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def teach_checkpoint(state: AgentState) -> AgentState:
    cp = state["checkpoints"][state["current_checkpoint"]]
    print(f"\n CHECKPOINT {state['current_checkpoint'] + 1}")
    print("Topic:", cp["topic"])
    print("Objectives:")
    for obj in cp["objectives"]:
        print("-", obj)
    return state

def ask_question(state: AgentState) -> AgentState:
    print("\n Explain this topic in your own words:")
    state["user_input"] = input("Your answer: ")
    return state

def evaluate_answer(state: AgentState) -> AgentState:
    cp = state["checkpoints"][state["current_checkpoint"]]

    raw = gemini_evaluate(
        cp["topic"],
        cp["objectives"],
        state["user_input"]
    )

    try:
        data = json.loads(raw)
        state["score"] = float(data.get("score", 0))
        state["passed"] = state["score"] >= 0.7
        print(f" Gemini score: {state['score']}")
    except Exception:
        print(" Gemini evaluation failed, defaulting to fail.")
        state["score"] = 0.0
        state["passed"] = False

    return state


def decide_next(state: AgentState) -> AgentState:
    if state["passed"]:
        print("Passed. Moving to next checkpoint.")
        state["current_checkpoint"] += 1
        state["explanation_level"] = "normal"
    else:
        print(" Not sufficient. Switching to Feynman explanation.")
    return state


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("teach", teach_checkpoint)
    graph.add_node("ask", ask_question)
    graph.add_node("evaluate", evaluate_answer)
    graph.add_node("decide", decide_next)
    graph.add_node("feynman", feynman_explain)

    graph.set_entry_point("teach")

    graph.add_edge("teach", "ask")
    graph.add_edge("ask", "evaluate")
    graph.add_edge("evaluate", "decide")
    graph.add_edge("feynman", "ask")

    graph.add_conditional_edges(
        "decide",
        lambda s: (
            "end"
            if s["current_checkpoint"] >= len(s["checkpoints"])
            else ("teach" if s["passed"] else "feynman")
        ),
        {
            "teach": "teach",
            "feynman": "feynman",
            "end": END
        }
    )
    return graph.compile()

def feynman_explain(state: AgentState) -> AgentState:
    cp = state["checkpoints"][state["current_checkpoint"]]
    print("\n Feynman Explanation (Gemini):")
    explanation = gemini_feynman(cp["topic"], cp["objectives"])
    print(explanation)

    state["explanation_level"] = "feynman"
    return state

