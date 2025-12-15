# Autonomous Learning Agent (Milestone 2 Release)

## 1. System Overview
This repository utilizes a **Local Hybrid Intelligence** architecture to act as an autonomous tutor.
This release includes the integrated workflow for **Phase 1 (Context)** and **Phase 2 (Assessment)**.

## 2. Key Features
* **Local RAG Pipeline:** Uses **FAISS** and **RecursiveCharacterTextSplitter** to chunk and index learning materials.
* **Neural Verification:** Uses **Google Flan-T5** (Local) to valid context relevance.
* **Assessment Engine:** Automatically generates questions based on the retrieved vector chunks.
* **Mastery-Based Progression:** Enforces a strict 70% pass threshold before allowing the learner to advance.

## 3. Workflow Steps
1.  **Gather:** Scrape Wikipedia or read User Notes.
2.  **Vectorize:** Embed text into FAISS database.
3.  **Quiz:** Generate 3 questions based on the vector embeddings.
4.  **Grade:** Score the learner's answers (Pass/Fail).

## 4. How to Run
1.  **Install:** `pip install -r requirements.txt`
2.  **Run:** `python agent_phase_2.py`