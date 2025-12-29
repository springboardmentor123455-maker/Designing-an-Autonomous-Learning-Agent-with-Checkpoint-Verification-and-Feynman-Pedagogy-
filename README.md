# Autonomous Learning Agent with Feynman Pedagogy


## 📖 Project Overview
This project implements an **Autonomous AI Tutor** designed to guide users through structured learning pathways using **Checkpoint Verification** and **Adaptive Simplification**.

Built on the **LangGraph** framework[cite: 5, 49], the agent operates as a directed cyclic graph that:
1.  **Ingests Knowledge:** Retrieves context from User Notes or Wikipedia via RAG[cite: 11, 18].
2.  **Generates Assessments:** Dynamically creates questions based on specific learning checkpoints[cite: 12, 22].
3.  **Verifies Understanding:** Grades learner answers using vector similarity and LLM-based logic[cite: 12, 23].
4.  **Adapts (Milestone 3 Focus):** If a learner scores **< 70%**, the agent triggers the **Feynman Pedagogy Module** to re-explain concepts using simple analogies before re-assessing[cite: 13, 25, 105].

---

## 🎯 Milestone 3: Feynman Teaching & Adaptive Loop
**Current Phase: Weeks 5-6** 

In this milestone, we transitioned from a linear assessment pipeline to a **closed-loop adaptive system**. The agent now possesses "Cognitive Recovery"—it detects failure and intervenes to teach rather than just grade.

### Key Features Implemented:
* [cite_start]✅ **Conditional Logic & Routing:** implemented the LangGraph router to direct users to the *Pass* state (End) or *Remediation* state based on the strict **70% threshold**[cite: 1, 94].
* [cite_start]✅ **Feynman Simplification Node:** A dedicated module that identifies knowledge gaps and generates simplified explanations (e.g., using cooking or traffic analogies) for difficult concepts[cite: 105, 109].
* [cite_start]✅ **Loop-Back Mechanism:** Successfully implemented the feedback loop where the workflow returns to *Question Generation* after remediation to verify the learner's new understanding[cite: 111].
* [cite_start]✅ **Hybrid Grading Engine:** Enhanced the scoring logic to use a combination of Vector Cosine Similarity, Keyword Matching, and LLM Judgment.

---

## ⚙️ System Architecture
[cite_start]The system logic is defined in `agent_phase_3.py` using **LangGraph** nodes and edges.

### Workflow Nodes:
1.  [cite_start]**`gather_context`**: Checks user notes first; falls back to Wikipedia API if empty.
2.  [cite_start]**`generate_questions`**: Synthesizes 5 focused questions based on the retrieved context.
3.  [cite_start]**`audit_questions`**: Self-correction layer that ensures questions are relevant before showing them.
4.  [cite_start]**`evaluate_learner`**: Interacts with the user, collects answers, and calculates a pass/fail score.
5.  [cite_start]**`feynman_simplification`**: (Triggered on Fail) Generates a simplified summary using `google/flan-t5-base`.

### State Graph:
```mermaid
graph TD
    A[Start] --> B(Gather Context)
    B --> C(Generate Questions)
    C --> D(Audit Questions)
    D --> E(Evaluate Learner)
    E -->|Score >= 70%| F[End / Next Checkpoint]
    E -->|Score < 70%| G(Feynman Simplification)

🛠️ Tech StackLanguage: Python 3.9+ 3Orchestration: langgraph, langchain 4LLM (Local): google/flan-t5-base (via HuggingFace Pipeline) 5Embeddings: sentence-transformers/all-MiniLM-L6-v2 6Vector Store: faiss-cpu 7External Data: wikipedia (API Wrapper) 8🚀 Installation & Usage1. PrerequisitesEnsure you have Python installed.2. Setup EnvironmentBash# Clone the repository
git clone <repository-url>
cd <repository-folder>

# Install dependencies
pip install -r requirements.txt
3. Run the Agent 
