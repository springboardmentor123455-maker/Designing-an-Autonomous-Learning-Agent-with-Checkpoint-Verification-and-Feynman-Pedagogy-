# Autonomous Learning Agent - Phase 1 (RAG-Enabled)

## 1. Project Overview
This repository contains the **Checkpoint Verification & Context Retrieval** module for an Autonomous AI Learning Agent. The system is engineered as a **Local Hybrid Intelligence** unit that orchestrates a structured learning workflow using **LangGraph**. It eliminates dependency on unstable cloud APIs by running a full **RAG (Retrieval-Augmented Generation)** pipeline directly in the execution environment.

## 2. Technical Architecture
The system implements a "Glass Box" AI architecture with three core layers:

### A. Context Ingestion Layer (Priority Queue)
Adhering to the "Flexible Content" requirement, the agent utilizes a strict priority logic:
1.  **User Document Analysis:** Ingests PDF notes via `pypdf`, chunks text using `RecursiveCharacterTextSplitter`, and performs Semantic Search using **FAISS** (Facebook AI Similarity Search).
2.  **Intelligence Grader:** An LLM-based node evaluates retrieved chunks. If the content is "Thin" (<200 chars) or graded "Irrelevant" by the model, it triggers a fallback.
3.  **Autonomous Web Search:** Uses `DuckDuckGoSearchRun` to dynamically fill knowledge gaps only when user data is insufficient.

### B. Cognitive Processing Layer (LangGraph)
The core logic is a **Stateful Graph** (`StateGraph`) that manages:
* **Context State:** Tracks source provenance (User Doc vs. Web).
* **Retry State:** Maintains a counter for self-correction loops.
* **Best Effort Memory:** Persists the highest-scoring output across failed attempts.

### C. Self-Correction & Validation Layer
Unlike standard chatbots, this agent "grades itself" before showing output:
* **Validation Node:** An LLM acts as a strict examiner, scoring the generated essay (0-5) based on a rubric (Relevance, Citations, Conciseness).
* **Feedback Loop:** If the score is < 4/5, the agent rejects the answer and retries (up to 5 times).

## 3. Features (Milestone 1)
* **Hybrid RAG Strategy:** Prioritizes local documents but seamlessly fetches web data when needed.
* **Strict Citation Enforcement:** All outputs leverage a "No-Hallucination" prompt policy, requiring tags like `[Source: User Doc]` or `[Source: Web Search]`.
* **Resilience Engineering:** Implements a "Best Effort" fallback to return the highest-scoring draft if the API limits are hit.
* **Formula-Free Mode:** Optimized for text-only explanations to avoid LaTeX rendering issues in standard console outputs.

## 4. Tech Stack
* **Orchestration:** LangGraph, LangChain
* **LLM Provider:** Hugging Face Inference API (Microsoft Phi-3.5 / Qwen 2.5)
* **Vector Database:** FAISS (CPU)
* **Search Tool:** DuckDuckGo Search
* **Document Handling:** `pypdf`, `fpdf` (for test generation)
* **Observability:** LangSmith Tracing

## 5. Usage Guide

### Prerequisites
* Python 3.10+
* Hugging Face API Token
* LangSmith API Key (Optional but recommended)

### Installation
```bash
pip install langgraph langchain langchain-huggingface langchain-community duckduckgo-search python-dotenv pypdf faiss-cpu sentence-transformers fpdf
