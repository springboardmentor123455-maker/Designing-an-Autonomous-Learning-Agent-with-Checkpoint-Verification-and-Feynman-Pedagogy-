# 🎓 Autonomous Learning Agent

An interactive **AI-powered learning system** built with **Streamlit**, **LangGraph**, and **LangChain**, designed to guide learners through structured checkpoints, assess understanding, identify gaps, and apply the **Feynman Technique** for remediation.

---

## 📌 Table of Contents

1. Project Overview
2. Key Features
3. System Architecture
4. Folder Structure
5. Installation & Setup
6. Running the Application
7. Learning Flow (User Journey)
8. State Management (LearningState)
9. Checkpoint Logic
10. Pass / Fail Behavior
11. LangGraph Workflow
12. LangSmith Tracing
13. Known Constraints
14. Future Enhancements

---

## 1️⃣ Project Overview

The **Autonomous Learning Agent** helps learners progress through topics step-by-step using:

- Context gathering (web or user notes)
- Automated assessment questions
- AI-based evaluation
- Gap detection
- Simplified explanations using the Feynman Technique

The system adapts dynamically based on learner performance.

---

## 2️⃣ Key Features

- 📚 Topic-wise learning checkpoints
- 📄 PDF notes upload
- 🤖 AI-generated questions
- 🧪 Automated evaluation
- 🧠 Gap detection & Feynman explanations
- 🔁 Retry same checkpoint on failure
- ➡️ Move to next checkpoint on success
- 📊 Progress persistence (JSON-based)
- 🔍 Full LangSmith tracing

---

## 3️⃣ System Architecture

High-level flow:

```
Streamlit UI
   ↓
LearningState (shared state)
   ↓
LangGraph Workflow
   ↓
Nodes (Context → Questions → Evaluation → Routing)
   ↓
Result (Pass / Feynman Retry)
```

---

## 4️⃣ Folder Structure

```
Learning_Agent_Ai/
│
├── app.py                   # Streamlit frontend
├── graph_workflow.py        # LangGraph definition
├── nodes.py                 # All graph nodes
├── routing.py               # Conditional routing logic
├── state.py                 # LearningState TypedDict
│
├── checkpoint_1.py          # Checkpoint definitions
├── checkpoint_class_1.py    # Checkpoint schema
│
├── ui_upload_view.py        # PDF upload UI
├── ui_pdf_loader.py         # PDF text extraction
├── ui_progress_store.py     # Progress persistence
│
├── contextProcessor.py      # Chunking & vector prep
├── gathercontext.py         # Web context gathering
│
├── llm_model.py             # NVIDIA LLM configs
├── promts.py                # Prompt templates & parsers
├── structureOut.py          # Pydantic output schemas
│
├── progress.json            # Saved learner progress
└── README.md                # Project documentation
```

---

## 5️⃣ Installation & Setup

### Prerequisites

- Python 3.10+
- Virtual environment (recommended)

### Install Dependencies

```bash
pip install streamlit langgraph langchain langsmith langchain-nvidia-ai-endpoints faiss-cpu pydantic python-dotenv PyPDF2
```

### Environment Variables

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=Autonomous-Learning-Agent
NVIDIA_API_KEY=your_nvidia_api_key
```

---

## 6️⃣ Running the Application

From the **parent directory**:

```bash
streamlit run Learning_Agent_Ai/app_ex.py
```

---

## 7️⃣ Learning Flow (User Journey)

1. Select checkpoint automatically (resume supported)
2. Upload notes (optional PDF)
3. Start learning
4. Review generated context
5. Answer assessment questions
6. Submit answers
7. View result
   - ✅ Pass → Next checkpoint button
   - ❌ Fail → Feynman explanation + retry

---

## 8️⃣ State Management (LearningState)

`LearningState` is the **single source of truth** shared across nodes.

Important keys:

- `checkpoint`
- `user_Notes`
- `answers`
- `questions`
- `score_percentage`
- `passed`
- `gaps`, `feynman_explanation`

⚠️ All keys accessed by nodes **must be initialized** before workflow invocation.

---

## 9️⃣ Checkpoint Logic

Each checkpoint includes:

- Topic
- Learning objectives
- Success criteria

Defined in `checkpoint_1.py`.

Progress is stored as:

```json
{
  "user_id": "default_user",
  "checkpoint": 2
}
```

---

## 🔟 Pass / Fail Behavior

### PASS

- Score ≥ 70%
- User sees result
- Must click **Next Checkpoint** to continue

### FAIL

- Score < 70%
- Feynman explanation shown
- User retries **same checkpoint**

No automatic progression.

---

## 1️⃣1️⃣ LangGraph Workflow

Nodes:

- start_checkpoint
- gather_context
- evalution_context
- process_context
- question_generation
- evaluate_answer
- detect_gap
- feynman_teaching

Routing is handled in `routing.py` using conditional edges.

---

## 1️⃣2️⃣ LangSmith Tracing

Enabled via environment variables.

Traces include:

- Each LangGraph node
- Routing decisions
- LLM prompts & outputs
- Latency and errors

Project name: **Autonomous-Learning-Agent**

---

## 1️⃣3️⃣ Known Constraints

- Some nodes assume pre-initialized state keys
- Monkey-patching used in Streamlit to avoid refactors
- Single-user progress store (JSON)

---

## 1️⃣4️⃣ Future Enhancements

- Multi-user authentication
- Database-backed progress
- Per-question feedback
- Learning analytics dashboard
- Export learning reports (PDF)
- Adaptive difficulty levels

---

## ✅ Conclusion

This project demonstrates a **production-style AI learning system** combining:

- LangGraph for control flow
- LangChain + NVIDIA LLMs for reasoning
- Streamlit for UX
- LangSmith for observability

It is extensible, debuggable, and learner-centric.

Happy Learning 🚀
