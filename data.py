from models import Checkpoint

CHECKPOINTS = { 
    "cp1": {
        "id": "cp1",
        "topic": "Introduction to AI Agents",
        "objectives": [
            "Define what an AI Agent is",
            "Explain how AI agents perceive and act in an environment",
            "List real-world examples of AI agents"
        ],
        "success_criteria": "Learner can clearly define an AI agent and describe its components with examples.",
    },
 
    "cp2": {
        "id": "cp2",
        "topic": "Types of AI Agents",
        "objectives": [
            "Explain different types of agents (simple reflex, model-based, goal-based, utility-based)",
            "Compare different agent types"
        ],
        "success_criteria": "Learner can name and explain the main types of AI agents.",
    },

    "cp3": {
        "id": "cp3",
        "topic": "Architecture of AI Agents",
        "objectives": [
            "Explain agent architecture",
            "Describe sensors and actuators",
            "Understand agent–environment interaction"
        ],
        "success_criteria": "Learner can explain how an AI agent is structured and interacts with its environment.",
    }, 


    "cp4": {
        "id": "cp4",
        "topic": "AI Agent Environments",
        "objectives": [
            "Explain different types of environments (deterministic, stochastic, episodic, sequential)",
            "Understand observable vs partially observable environments",
            "Relate environments to agent behavior"
        ],
        "success_criteria": "Learner can classify environments and explain how environment type affects agent design.",
    },
}
