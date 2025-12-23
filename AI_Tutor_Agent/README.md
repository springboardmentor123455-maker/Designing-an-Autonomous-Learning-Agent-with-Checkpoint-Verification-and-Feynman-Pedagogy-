# AI Autonomous Learning Agent

**Project Lead:** Vivek Chaudhary  
**Current Status:** Milestone 2 Complete (Context Processing & Dual Assessment System)

## Project Overview
This project is an **Autonomous AI Learning Agent** built with **LangGraph** and **Azure OpenAI**. It functions as an intelligent tutor that generates structured learning paths, aggregates high-quality study materials, and rigorously validates user mastery through dynamic assessments.

Unlike standard LLM wrappers, this agent implements a **Stateful Cognitive Architecture**. It evaluates the relevance of information, **formats it into clean study material**, processes it into learnable chunks, and refuses to let the user progress until they demonstrate understanding (≥ 70% score).

## Key Features

### Milestone 1: Context Gathering & Validation 
- **Smart Context Retrieval:**
  - Prioritizes **User-Uploaded Notes** to personalize the learning experience.
  - Falls back to **Tavily Web Search** if notes are insufficient.
- **Self-Correcting Search Loop:**
  - An Azure OpenAI "Judge" node evaluates gathered content against learning objectives.
  - If the **Relevance Score is < 4/5**, the agent generates a critique, refines its search query, and retries (up to 5 times).
- **LangSmith Observability:** Full tracing of search queries, LLM latency, and validation scores.

### Milestone 2: Processing, Assessment & Sequencing 
- **AI-Powered Content Formatting (NEW):**
  - Raw text is transformed into **clean, structured study material**.
  - Features proper headings, bullet points, bold key terms, and paragraph breaks.
  - Removes duplicates and broken text for professional presentation.

- **Vector-Based Processing:**
  - Formatted content is split using `RecursiveCharacterTextSplitter`.
  - Chunks are embedded via **Azure OpenAI (`text-embedding-ada-002`)** and stored in a local **FAISS Vector Store**.

- **Dual Assessment System (NEW):**
  - Questions **generate on-demand** when user selects assessment type.
  - **Two Modes Available:**
    1. **Objective (MCQ):** 5 multiple-choice questions with instant auto-grading.
    2. **Subjective (Open-Ended):** 3 descriptive questions evaluated by AI agent.

- **AI-Powered Subjective Evaluation (NEW):**
  - Each answer receives an individual score (0-100).
  - Detailed constructive feedback on strengths and areas for improvement.
  - Average score calculated; must achieve ≥70 to pass.

- **Strict Mastery Gate:**
  - **70% Threshold:** Users must score ≥ 70% on chosen assessment to pass a checkpoint.
  - **Halt Mechanism:** Progress is strictly blocked if the user fails.
  - Can retry with fresh questions or switch assessment modes.

- **Sequential Learning Path:**
  - Users define a curriculum (e.g., "Objective A, Objective B, Objective C").
  - The agent locks future objectives, forcing step-by-step mastery.
  - Visual progress tracker in sidebar.

## Core Logic & Architecture

The agent uses a **StateGraph** architecture to manage the lifecycle of a learning session.

### 1. The Agent State
Shared memory persisted across graph nodes:
```python
class AgentState(TypedDict):
    active_checkpoint: LearningCheckpoint  # Current Topic & Specific Objective
    gathered_context: str                  # Raw text from web/notes
    relevance_score: int                   # 1-5 Score from Validation Node
    formatted_content: str                 # AI-cleaned, structured study material (NEW)
    processed_context: List[str]           # Chunked text for questions
    quiz_questions: List[Dict]             # Generated MCQ pairs
    subjective_questions: List[str]        # Generated open-ended questions (NEW)
    retry_count: int                       # Recursion limiter
```

### 2. The Graph Workflow
```
START → Gather Context → Validate Context → [Retry if Score < 4]
                                          ↓
                                  Format Content (NEW)
                                          ↓
                                  Process Context
                                          ↓
                            [User Chooses Assessment Type] (NEW)
                                      ↙         ↘
                          Generate MCQs       Generate Subjective
                                      ↘         ↙
                                    [Evaluate Answers]
                                            ↓
                              [Pass ≥70% → Next | Fail → Retry]
```

### 3. Key Nodes

#### **gather_context_node**
- Checks for user notes first.
- If unavailable, performs Tavily web search.
- Retry logic refines queries based on validation feedback.

#### **validate_context_node**
- Azure OpenAI evaluates context coverage.
- Returns score (1-5), reason, and search refinement hint.

#### **format_content_node (NEW)**
- Transforms raw text into clean, readable study material.
- Uses Azure OpenAI with markdown formatting.
- Ensures professional presentation before user sees content.

#### **process_context_node**
- Splits formatted content into chunks.
- Embeds and stores in FAISS vector database.

#### **generate_quiz_from_context**
- On-demand MCQ generation when user selects objective mode.
- JSON validation with automatic retry.

#### **generate_subjective_questions (NEW)**
- On-demand open-ended question generation.
- 3 questions testing deep understanding.

#### **evaluate_subjective_answers (NEW)**
- AI agent scores each answer (0-100).
- Provides detailed, constructive feedback.
- Considers accuracy, depth, clarity, completeness.

### 4. Decision Points
- **Validation Loop:** Retry search if relevance < 4 or retries < 5.
- **Assessment Choice:** User manually selects objective or subjective mode.
- **Progression Gate:** Block next checkpoint until ≥70% score achieved.

## Technology Stack
- **Framework:** LangGraph (state management), Streamlit (UI)
- **LLM:** Azure OpenAI (GPT-4 for reasoning, Ada-002 for embeddings)
- **Search:** Tavily API
- **Vector Store:** FAISS (local, ephemeral)
- **Monitoring:** LangSmith (trace logs, latency analysis)
- **Environment:** Python 3.10+, dotenv for secrets

## Project Structure
```
AI_Tutor_Agent/
├── app.py                          # Streamlit UI with dual assessment flow
├── src/
│   ├── models.py                   # Pydantic schemas (LearningCheckpoint)
│   ├── state.py                    # AgentState TypedDict definition
│   ├── graph.py                    # LangGraph workflow + nodes
│   ├── subjective_evaluator.py     # AI evaluation engine (NEW)
│   └── checkpoints.py              # Sample curriculum (deprecated)
├── .env                            # Azure/Tavily API keys (not tracked)
└── README.md                       # This file
```

## How It Works (User Journey)

1. **Define Learning Path:** Enter topic + comma-separated objectives
2. **Agent Gathers Context:** Searches/validates content automatically
3. **Content Formatting:** AI cleans and structures material with headings/bullets
4. **Study Phase:** User reads formatted content at their own pace
5. **Choose Assessment:** Click "Objective" or "Subjective" button
6. **Take Assessment:** Answer MCQs or open-ended questions
7. **Get Results:**
   - Objective: Instant score
   - Subjective: AI feedback + score per question
8. **Progress:** Pass (≥70%) unlocks next checkpoint, fail allows retry

## Next Steps: Milestone 3 (Feynman Teaching)
- [ ] Implement knowledge gap identification
- [ ] Generate simplified explanations with analogies
- [ ] Add Feynman node to graph (trigger on <70% score)
- [ ] Loop back to re-assessment after explanation

## License
MIT License - See LICENSE file for details

## Contact
**Vivek Chaudhary**  
GitHub: VivekChaudhary111 | Email: vivekchaudharyfor121@gmail.com

---

**Last Updated:** December 23, 2025  
**Version:** 2.1.0 (Milestone 2 Complete + Dual Assessment)