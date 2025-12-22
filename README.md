# Milestone 2: Autonomous Assessment & Grading Engine

## 📌 Project Overview
This module implements the **Evaluation Layer** of the Autonomous Learning Agent. It is designed to autonomously generate unique assessment questions based on dynamic knowledge bases (Wikipedia/User Notes) and strictly evaluate learner responses using a **Triple-Layer Semantic Grading System**.

## 🚀 Key Features

### 1. Dynamic Context Retrieval (RAG)
- **Hybrid Source Selection:** Automatically prioritizes "User Notes" if available; falls back to live "Wikipedia API" search if notes are missing.
- **Vector Database:** Uses **FAISS** (Facebook AI Similarity Search) to index and retrieve only the most relevant text chunks.

### 2. Intelligent Question Generation
- **Anti-Hallucination Constraints:** Strictly enforces open-ended questions.
- **MCQ Firewall:** Contains logic filters to reject "Which of the following" style outputs, ensuring deep-learning assessment.
- **Relevance Auditing:** Every generated question is scored (0-5) against the source text before being shown to the user.

### 3. Triple-Layer "Strong" Grading System
To ensure human-like accuracy, the agent uses three concurrent evaluation metrics:
1.  **Vector Similarity (Cosine):** Measures the semantic closeness of the answer to the ground truth.
2.  **Keyword Forensics (TF-IDF):** Scans for critical technical terminology extracted from the context.
3.  **LLM Judgment:** A local LLM (Flan-T5) acts as a final judge to catch logically correct answers that might miss specific keywords.

## 🛠️ Tech Stack
- **Orchestration:** LangGraph (State Management)
- **LLM:** Google Flan-T5 (Local Inference)
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2`
- **Math:** Scikit-Learn (Cosine Similarity)
- **Search:** Wikipedia API Wrapper

## 📊 Logic Flow
1.  **Ingest:** Checkpoint Title -> Fetch Data -> Chunking.
2.  **Generate:** Create 5 unique questions -> Audit for Relevance.
3.  **Interact:** User answers questions via console.
4.  **Evaluate:** Apply Triple-Layer Grading -> Calculate Score.
5.  **Decision:**
    - Score > 70%: **PASS** (Proceed to next module).
    - Score < 70%: **FAIL** (Trigger Remediation - *Milestone 3*).
