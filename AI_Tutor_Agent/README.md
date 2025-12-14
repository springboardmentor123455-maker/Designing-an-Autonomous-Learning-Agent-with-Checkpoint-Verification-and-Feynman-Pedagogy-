# AI Autonomous Learning Agent

**Project Lead:** Vivek Chaudhary  
**Current Status:** Milestone 2 Complete (Context Processing, Quiz Generation & Sequential Verification)

## Project Overview
This project is an **Autonomous AI Learning Agent** built with **LangGraph** and **Azure OpenAI**. It functions as an intelligent tutor that generates structured learning paths, aggregates high-quality study materials, and rigorously validates user mastery through dynamic assessments.

Unlike standard LLM wrappers, this agent implements a **Stateful Cognitive Architecture**. It does not simply retrieve information; it evaluates the relevance of that information, processes it into learnable chunks, and refuses to let the user progress until they demonstrate understanding (≥ 70% quiz score).

## Key Features

### Milestone 1: Context Gathering & Validation
- **Smart Context Retrieval:** - Prioritizes **User-Uploaded Notes** to personalize the learning experience.
  - Falls back to **Tavily Web Search** if notes are insufficient.
- **Self-Correcting Search Loop:**
  - An Azure OpenAI "Judge" node evaluates gathered content against learning objectives.
  - If the **Relevance Score is < 4/5**, the agent generates a critique, refines its search query, and retries (up to 5 times).
- **LangSmith Observability:** Full tracing of search queries, LLM latency, and validation scores.

### Milestone 2: Processing, Assessment & Sequencing (Current)
- **Vector-Based Processing:** - Validated text is split using `RecursiveCharacterTextSplitter`.
  - Chunks are embedded via **Azure OpenAI (`text-embedding-ada-002`)** and stored in a local **FAISS Vector Store**.
- **Self-Healing Quiz Generator:**
  - A specialized node generates JSON-formatted quizzes.
  - Includes an **Internal Retry Mechanism** to automatically recover if the LLM outputs malformed JSON.
- **Strict Mastery Gate:**
  - **70% Threshold:** Users must score ≥ 70% on the quiz to pass a checkpoint.
  - **Halt Mechanism:** Progress is strictly blocked if the user fails.
- **Sequential Learning Path:** - Users define a curriculum (e.g., "Objective A, Objective B, Objective C").
  - The agent locks future objectives, forcing step-by-step mastery.

## Core Logic & Architecture

The agent uses a **StateGraph** architecture to manage the lifecycle of a learning session.

### 1. The Agent State
Shared memory persisted across graph nodes:
```python
class AgentState(TypedDict):
    active_checkpoint: LearningCheckpoint  # Current Topic & Specific Objective
    gathered_context: str                  # Raw text from web/notes
    relevance_score: int                   # 1-5 Score from Validation Node
    processed_context: List[str]           # Chunked text for the Quiz
    quiz_questions: List[Dict]             # Generated Q&A pairs
    retry_count: int                       # Recursion limiter