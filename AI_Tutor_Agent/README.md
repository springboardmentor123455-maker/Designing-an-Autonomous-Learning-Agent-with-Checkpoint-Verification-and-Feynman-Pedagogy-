# AI Autonomous Learning Agent

**Project Lead:** Vivek Chaudhary  
**Current Status:** Milestone 4 Complete (Full Integration with Feynman Pedagogy)

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
    formatted_content: str                 # AI-cleaned, structured study material
    processed_context: List[str]           # Chunked text for questions
    quiz_questions: List[Dict]             # Generated MCQ pairs
    subjective_questions: List[str]        # Generated open-ended questions
    knowledge_gaps: List[str]              # Identified weak concepts (Milestone 3)
    feynman_explanation: str               # Simplified explanation (Milestone 3)
    feynman_attempt_count: int             # Retry tracking (Milestone 3)
    retry_count: int                       # Recursion limiter
```

### 2. The Graph Workflow
```
┌─────────────────────────────────────────────────────────────────────────┐
│                         START NEW TOPIC                                 │
│                    (User Defines Learning Path)                         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 ↓
                    ┌────────────────────────┐
                    │ CHECKPOINT N (1,2,3...)│
                    └────────────┬───────────┘
                                 ↓
                         Gather Context
                                 ↓
                      Validate Context → [Retry if Score < 4]
                                 ↓
                         Format Content
                                 ↓
                        Process Context
                                 ↓
                   [User Chooses Assessment Type]
                          ↙              ↘
              Generate MCQs          Generate Subjective
              (5 Questions)          (3 Questions)
                          ↘              ↙
                        Evaluate Answers
                    (Auto Grade / AI Evaluate)
                                 ↓
                    ┌────────────────────────┐
                    │  Score Check: ≥70%?    │
                    └─────┬──────────────┬───┘
                          │              │
                         PASS           FAIL (<70%)
                          │              │
                          │              ↓
                          │      ┌──────────────────┐
                          │      │ Feynman Teaching │
                          │      └────────┬─────────┘
                          │               ↓
                          │    Identify Knowledge Gaps
                          │               ↓
                          │    Generate Simplified Explanation
                          │    (Analogies + Simple Language)
                          │               ↓
                          │        Display to Learner
                          │               ↓
                          │    ┌──────────────────────┐
                          │    │  Learner Choice:     │
                          │    │  1. Retry with new   │
                          │    │     questions        │
                          │    │  2. Switch assessment│
                          │    │     mode             │
                          │    └──────┬───────────────┘
                          │           │
                          │           └──────┐
                          │                  ↓
                          │        [Generate Questions] ←─┘
                          │                  │
                          │                  └─→ Loop Back to Assessment
                          │
                          ↓
                ┌─────────────────────┐
                │ More Checkpoints?   │
                └──────┬──────────┬───┘
                       │          │
                    YES│          │NO
                       │          │
                       ↓          ↓
            ┌──────────────┐  ┌──────────────────┐
            │ NEXT         │  │     COURSE       │
            │ CHECKPOINT   │  │   COMPLETE!      │
            │ (N+1)        │  └────────┬─────────┘
            └──────┬───────┘           │
                   │                   ↓
                   │         ┌──────────────────┐
                   │         │ Start New Topic  │
                   │         │ (Clear State)    │
                   │         └────────┬─────────┘
                   │                  │
                   └──────────────────┴──→ Loop Back to START
```

**Key Decision Points:**
- **Context Validation:** Retry search if relevance < 4/5 (max 5 attempts)
- **Assessment Selection:** User manually chooses Objective (MCQ) or Subjective
- **Score Threshold:** 70% required to pass; <70% triggers Feynman Teaching
- **Feynman Loop:** Learner can retry with fresh questions after simplified explanation
- **Checkpoint Progression:** Sequential mastery - must pass current to unlock next
- **Course Completion:** After final checkpoint, option to start entirely new topic

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
├── app.py                          # Streamlit UI with full workflow integration
├── src/
│   ├── models.py                   # Pydantic schemas (LearningCheckpoint)
│   ├── state.py                    # AgentState TypedDict with Feynman fields
│   ├── graph.py                    # LangGraph workflow + all nodes
│   ├── subjective_evaluator.py     # AI evaluation engine for open-ended answers
│   ├── feyman_instructor.py        # Feynman Technique implementation (Milestone 3)
│   └── checkpoints.py              # Sample curriculum (deprecated)
├── .env                            # Azure/Tavily/Langsimth API keys (not tracked)
├── requirements.txt                # Python dependencies
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
8. **Adaptive Learning (if score < 70%):**
   - **Feynman Explanation Triggered:** System identifies knowledge gaps
   - **Simplified Teaching:** Receive easy-to-understand explanations with analogies
   - **Retry with Clarity:** Return to assessment with better understanding
9. **Progress:** Pass (≥70%) unlocks next checkpoint, fail triggers Feynman loop
10. **Repeat:** Continue through all checkpoints until mastery achieved

### Milestone 3: Feynman Teaching Implementation 
- **Knowledge Gap Identification:**
  - Automatically identifies specific concepts user struggled with based on incorrect/low-scoring answers.
  - Works for both objective (MCQ) and subjective assessments.
  - Analyzes up to top 3 knowledge gaps for focused remediation.

- **Simplified Explanation Generation:**
  - Uses Feynman Technique to break down complex concepts into simple terms.
  - Generates everyday analogies and metaphors from daily life.
  - Avoids technical jargon; explains like teaching a 12-year-old.
  - Immediately defines any unavoidable technical terms in simple words.

- **AI-Powered Simplification Engine:**
  - Azure OpenAI generates targeted explanations addressing identified gaps.
  - References original study material while creating simplified versions.
  - Uses concrete examples and step-by-step breakdowns.
  - Formats with clear headings and bullet points for readability.

- **Seamless UI Integration:**
  - Feynman explanations display in distinctive styled boxes (orange accent).
  - Shows attempt count to track learning iterations.
  - Encourages learner to explain concepts aloud before retaking.
  - Non-intrusive: only appears after failing assessment (<70%).

- **Adaptive Loop-Back Mechanism:**
  - After viewing Feynman explanation, learner can retry assessment.
  - Fresh questions generated on each retry.
  - Tracks attempt count across checkpoint session.
  - Supports switching between objective/subjective modes.

### Milestone 4: Integration & End-to-End Testing 
- **Complete Workflow Integration:**
  - Seamless state management across all LangGraph nodes.
  - Proper data flow from context gathering → assessment → Feynman → retry.
  - Session state persistence ensures data consistency throughout learning journey.

- **Multi-Checkpoint Sequential Learning:**
  - Strict sequential progression through defined learning path.
  - Visual progress tracker in sidebar with current/completed/locked indicators.
  - Cannot skip ahead; must master each checkpoint before unlocking next.
  - Checklist format provides clear overview of entire learning path.

- **Full-Featured User Interface:**
  - **Streamlit-based web interface** with professional styling.
  - **Configuration sidebar:** Model info, note upload, course map.
  - **Dynamic content display:** Study material → Assessment selection → Results.
  - **Dual assessment modes** seamlessly integrated with single codebase.
  - **Responsive design** with custom CSS for optimal readability.

- **State Management Excellence:**
  - Persistent session state across UI interactions.
  - Proper handling of assessment retries and mode switching.
  - Clean state transitions prevent data loss or inconsistency.
  - Efficient caching of generated content (study material, questions).

- **Comprehensive Testing & Validation:**
  - **End-to-End Testing:** Verified complete learning path (3+ checkpoints).
  - **Feynman Loop Testing:** Confirmed trigger on <70%, proper regeneration.
  - **Assessment Diversity:** Both MCQ and subjective modes tested thoroughly.
  - **Edge Cases:** Handled retries, mode switching, empty inputs.
  - **LangSmith Tracing:** Full observability of agent decisions and LLM calls.

- **Production-Ready Features:**
  - Rate limiting and error handling for API calls.
  - Clean separation of concerns (UI, logic, state management).
  - Modular architecture allows easy feature additions.
  - Environment-based configuration for API keys.
  - User-friendly error messages and progress indicators.

## License
MIT License - See LICENSE file for details

## Contact
**Vivek Chaudhary**  
GitHub: VivekChaudhary111 | Email: vivekchaudharyfor121@gmail.com

---

**Last Updated:** January 17, 2026  
**Version:** 3.0.0 (All Milestones Complete - Production Ready)