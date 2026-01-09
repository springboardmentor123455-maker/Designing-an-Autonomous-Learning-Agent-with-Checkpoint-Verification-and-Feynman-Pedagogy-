# Autonomous AI Tutor with Checkpoint Verification & Feynman Pedagogy

## 📌 Project Overview
[cite_start]This project implements an **Autonomous Learning Agent** designed to provide a personalized, structured tutoring experience[cite: 69, 70]. The agent utilizes **Retrieval-Augmented Generation (RAG)** to teach complex technical topics, strictly enforcing mastery before allowing the learner to progress.

[cite_start]The system combines **LangChain** for logic orchestration and **Streamlit** for the user interface, aiming to solve the problem of passive learning by implementing active recall and rigorous assessment[cite: 74, 76].

## 📂 Repository Structure: Understanding the Files

This repository contains two core components that demonstrate the project's evolution from logic design to user interface integration.

### 1. `Milestone 2.ipynb` (The Backend Logic Core)
**Role:** Development, Logic Testing, and Graph Architecture.
* [cite_start]**Technology:** Implements **LangGraph** (`StateGraph`) to orchestrate the learning workflow[cite: 111].
* **Functionality:**
    * Defines the agent's nodes: Document Processing, Web Search, Essay Generation, Validation, and Grading.
    * [cite_start]Contains the retry logic and state management for the "Learning Feedback Loop"[cite: 102].
    * Used for rigorously testing the "no-math" generation prompts and strict grading rubrics.
    * [cite_start]Demonstrates the "Context Gathering" and "Initial Verification" milestones[cite: 132, 149].

### 2. `app.py` (The Interactive User Interface)
**Role:** Frontend Application and End-to-End Integration.
* **Technology:** **Streamlit** (Python web framework).
* **Functionality:**
    * [cite_start]A port of the backend logic into a user-friendly web interface[cite: 120].
    * Allows users to upload PDF notes, select topics (e.g., CNNs, Transformers), and take interactive quizzes.
    * Visualizes the progression from "Study Mode" to "Quiz Mode" to "Result Grading."
    * [cite_start]Fulfills the project requirement for a "Learner Interface"[cite: 120].

---

## 🚀 Key Features

* [cite_start]**Dynamic Context Gathering:** Prioritizes user-uploaded PDFs (Lecture Notes) and falls back to autonomous Web Search (DuckDuckGo) if notes are insufficient[cite: 80].
* **Strict "No-Math" Explanations:** The agent is prompted to explain complex mathematical concepts (like Backpropagation) using purely narrative, conceptual English, ensuring accessibility.
* **Checkpoint Verification:**
    * [cite_start]Generates 3-5 conceptual questions based on the generated material[cite: 154].
    * Grades answers on a strict rubric (0-100 scale).
    * [cite_start]Requires a passing score (e.g., >70%) to consider the topic mastered[cite: 74, 116].
* **Grading & Feedback:** Provides specific, corrective feedback for every answer, explaining *why* an answer was right or wrong.

## 🛠️ Tech Stack

* [cite_start]**Language:** Python [cite: 122]
* [cite_start]**Orchestration:** LangChain & LangGraph [cite: 123, 124]
* [cite_start]**LLM Engine:** HuggingFace Endpoint (Qwen/Qwen2.5-72B-Instruct) [cite: 125]
* [cite_start]**Embeddings:** Sentence-Transformers (`all-MiniLM-L6-v2`) [cite: 127]
* [cite_start]**Vector Store:** FAISS (for document chunking and retrieval) [cite: 129]
* [cite_start]**Search Tool:** DuckDuckGo Search API [cite: 126]
* **Frontend:** Streamlit

## ⚙️ Setup & Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/yourusername/autonomous-ai-tutor.git](https://github.com/yourusername/autonomous-ai-tutor.git)
    cd autonomous-ai-tutor
    ```

2.  **Install Dependencies**
    ```bash
    pip install langchain langchain-huggingface langchain-community chromadb faiss-cpu duckduckgo-search streamlit
    ```

3.  **Environment Variables**
    You must provide a Hugging Face API Token.
    * *Option A:* Create a `.env` file.
    * *Option B:* Enter the token directly in the `app.py` sidebar when running.

## 🖥️ Usage Guide

### To Run the Interactive App:
Execute the Streamlit application to use the full UI.
```bash
streamlit run app.py
