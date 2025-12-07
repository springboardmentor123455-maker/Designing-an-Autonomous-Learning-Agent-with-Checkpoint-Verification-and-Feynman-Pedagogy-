# AI Autonomous Learning Agent

**Project Lead:** Vivek Chaudhary  
**Current Status:**  Milestone 1 Complete (Context Gathering & Verification)

## Project Overview
This project is an **Autonomous AI Learning Agent** designed to provide a personalized, structured tutoring experience. Built using **LangGraph**, it acts as an intelligent tutor that creates a "Learning Map" for any topic, gathers high-quality study materials, and rigorously verifies them before teaching.

Unlike standard chatbots, this agent possesses a **Self-Correction Loop**: it evaluates its own search results against specific learning objectives. If the content is irrelevant, it critiques itself and refines its search query to try again.

## Key Features (Milestone 1)
- **Topic Agnostic:** Can generate study materials for any subject (e.g., "Quantum Physics", "History of Rome", "Java Stream API").
- **Smart Context Gathering:** - Prioritizes **User-Uploaded Notes** (if available).
  - Falls back to **Live Web Search** (Tavily API) if notes are missing or insufficient.
- **Strict Relevance Verification:** An **Azure OpenAI** powered "Judge" evaluates gathered content against specific learning objectives, assigning a relevance score (1-5).
- **Self-Correction Loop:** If the Relevance Score is `< 4/5`, the agent automatically:
  - Generates feedback on *why* the content failed.
  - Refines the search query.
  - Retries (up to 5 times) to find better material.
- **Full Observability:** Integrated with **LangSmith** to trace search queries, LLM decisions, and latency in real-time.
- **Verbose UI:** A Streamlit interface that displays the agent's internal "thought process," logs, and validation scores live.

## Tech Stack
- **Core Logic:** Python 3.10+, LangGraph
- **LLM Provider:** Azure OpenAI (Native Client with `gpt-5-nano` / `gpt-4o`)
- **Web Search:** Tavily Search API
- **Frontend:** Streamlit
- **Observability:** LangSmith (LangChain Tracing)
- **Data Validation:** Pydantic

## Project Structure
```text
AI_Tutor_Agent/
├── src/
│   ├── graph.py       # Core Logic: The LangGraph workflow (Nodes & Edges)
│   ├── state.py       # Memory: Shared state definition
│   ├── models.py      # Data Structure: Strict Pydantic models for Checkpoints
│   └── __init__.py
├── app.py             # UI: Streamlit Frontend
├── requirements.txt   # Dependencies
├── .env               # API Keys (Secrets)
└── README.md          # Documentation