# Designing-an-Autonomous-Learning-Agent-with-Checkpoint-Verification-and-Feynman-Pedagogy-

# 🎓 Autonomous Learning Agent  
### An AI-Powered Adaptive Learning System using LangGraph and Feynman Teaching

---

## 📌 Project Overview

The **Autonomous Learning Agent** is an intelligent, AI-driven tutoring system designed to help learners understand technical topics **step-by-step** through adaptive assessments and simplified explanations.

Instead of allowing learners to progress without mastery, the system **verifies understanding at every checkpoint**. If the learner struggles, it applies the **Feynman Teaching Technique** to re-explain concepts in simple language and encourages a retry.

This project demonstrates how **Large Language Models (LLMs)** can be used **responsibly for education**, focusing on conceptual understanding rather than passive content generation.

---

## 🎯 Key Objectives

- Guide learners through **structured learning checkpoints**
- Automatically generate questions from defined learning objectives
- Evaluate learner understanding using a **mastery threshold**
- Provide simplified explanations when understanding is weak
- Enforce **concept mastery before progression**

---

## 🧩 Milestone-wise Implementation

### 🟢 Milestone 1: Context Gathering & Validation

**Goal:** Collect relevant study material for the selected topic.

**How it works:**
- Uses **user-uploaded notes** if available
- Falls back to **web search (Tavily API)** when notes are insufficient
- Combines and validates content relevance using an LLM
- Retries content fetching if relevance is low

**Outcome:**  
Only **meaningful, topic-relevant content** is used for learning.

---

### 🟢 Milestone 2: Question Generation & Verification

**Goal:** Verify learner understanding through assessment.

**Key Features:**
- Generates **checkpoint-specific questions** based on objectives
- Each checkpoint has **3–5 dynamically generated questions**
- Questions differ across checkpoints (no repetition)
- Learner answers are evaluated automatically
- Score is calculated as a percentage

**Pass Criteria:**
- ✔️ **Score ≥ 70%** → Checkpoint passed  
- ❌ **Score < 70%** → Triggers Feynman Teaching

---

### 🟢 Milestone 3: Feynman Teaching Technique

**Goal:** Help learners understand concepts they failed.

**How it works:**
- Identifies weak areas from incorrect answers
- Generates simplified explanations using:
  - Everyday analogies
  - Plain language
  - Minimal jargon
- Explanation is displayed in a highlighted UI section
- Learner retries the assessment after explanation

This simulates **teaching a concept as if explaining to a beginner**, reinforcing deep understanding.

---

### 🟢 Milestone 4: Integration & Learning Path

**Goal:** Create a complete end-to-end learning journey.

**Features:**
- Sequential progression through checkpoints
- Learners **cannot skip checkpoints**
- Progress tracked using session state
- Supports:
  - Predefined topics
  - Dynamic topics 

The learning path completes **only after all checkpoints are passed**.

---

```markdown
## 🧠 System Architecture (High Level)

```text
Select Topic
      ↓
Gather Context (Notes / Web)
      ↓
Validate Context
      ↓
Generate Questions
      ↓
Answer Verification
      ↓
Score ≥ 70% ?
   ├── Yes → Next Checkpoint
   └── No  → Feynman Explanation → Retry
```

---

## 🛠️ Technology Stack

| Category | Technology |
|--------|------------|
| Language | Python 3.x |
| Frontend | Streamlit |
| Workflow Engine | LangGraph |
| LLM | Groq (Llama 3.3 70B) |
| Search | Tavily API |
| State Management | LangGraph State |
| Environment | python-dotenv |

---

## 📂 Project Structure

```text
Designing-an-Autonomous-Learning-Agent-with-Checkpoint-Verification-and-Feynman-Pedagogy-/
│
├── app.py                    # Streamlit UI (entry point)
├── main.py                   # App / agent runner
├── graph.py                  # LangGraph workflow definition
├── state.py                  # AgentState definition
├── checkpoints.py            # Predefined ML checkpoints
├── config.py                 # Configuration & constants
├── requirements.txt          # Dependencies
├── README.md                 # Project documentation
├── .gitignore                # Git ignore rules
│
├── nodes/                    # LangGraph nodes (core logic)
│   ├── __init__.py
│   ├── define_checkpoint.py
│   ├── gather_context.py
│   ├── validate_context.py
│   ├── question_generation.py
│   ├── question_relevance.py
│   ├── answer_verification.py
│   ├── answer_decision.py
│   ├── decision.py
│   └── feynman_teaching.py
│
├── rag/                      # Retrieval-Augmented Generation utilities
│   ├── __init__.py
│   ├── chunking.py
│   ├── embeddings.py
│   └── qa.py
│
└── utils/                    # Supporting utilities
    ├── dynamic_checkpoints.py
    └── output.py
```

---

## 🚀 How to Run the Project

### 1️⃣ Install dependencies
```bash
pip install -r requirements.txt
```
### 2️⃣ Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_api_key_here
TAVILY_API_KEY=your_api_key_here
```

### 3️⃣ Run the application
```bash
streamlit run app.py
```

## 📊 Evaluation Criteria

- Checkpoint-wise assessment
- 70% mastery threshold
- Adaptive retry using Feynman explanations
- Strict sequential progression enforcement

## 🙏 Conclusion

This project demonstrates how AI can function as a responsible educational assistant, prioritizing understanding over shortcuts.

By combining LLMs, structured workflows, and pedagogical principles, the Autonomous Learning Agent delivers a meaningful and mastery-driven learning experience.

## 👩‍💻 Author

**Nisha Murali**
