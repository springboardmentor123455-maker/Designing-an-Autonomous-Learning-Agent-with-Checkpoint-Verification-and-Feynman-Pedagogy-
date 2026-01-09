# Milestone 1: Autonomous Learning Agent (RAG + LangGraph)

This Jupyter Notebook (`Milestone1.ipynb`) implements a robust, self-correcting AI Tutor Agent. The agent is designed to generate concise technical summaries on specific Deep Learning topics by leveraging Retrieval-Augmented Generation (RAG) and autonomous web search.

## 🧠 Core Architecture

The agent is built using **LangGraph** and follows a cyclical workflow:

1.  **Document Check:** Checks a local PDF (`notes.pdf`) for relevant content using vector search (FAISS) and semantic grading.
2.  **Web Search:** If the local document is insufficient, the agent performs a live DuckDuckGo web search.
3.  **Generation:** Synthesizes a technical essay using the **Qwen/Qwen2.5-72B-Instruct** LLM.
4.  **Validation:** An LLM-based grader evaluates the essay on a 1-5 scale (checking for relevance, citations, and clarity).
5.  **Self-Correction:**
    * If the score is low (< 4/5), the agent retries the generation.
    * If the score is high (4 or 5), the submission is finalized.

## 🛠️ Dependencies

The notebook requires the following Python libraries:
* `langgraph`
* `langchain`, `langchain-huggingface`, `langchain-community`
* `duckduckgo-search`
* `pypdf` (for PDF processing)
* `faiss-cpu` (for vector storage)
* `sentence-transformers` (for embeddings)

## ⚙️ Configuration

Before running the notebook, ensure you have the following API keys ready. The notebook will prompt you to enter them securely:

* **Hugging Face API Token:** Access to the Qwen 2.5 model via Hugging Face Inference Endpoints.
* **LangChain API Key:** For LangSmith tracing (Project: `Llama-Tutor-Agent`).

## 🚀 Usage Guide

1.  **Install Requirements:** Run the first cell to install all necessary packages.
2.  **Authenticate:** Run the second cell and enter your API keys when prompted.
3.  **Initialize:** Run the model configuration cells to set up the Qwen model and embeddings.
4.  **Select a Topic:** The agent provides 5 preset learning checkpoints:
    * 1. Transformer Architecture
    * 2. Backpropagation
    * 3. RAG Systems
    * 4. Generative Adversarial Networks
    * 5. Convolutional Neural Networks
5.  **Provide Context:**
    * Place a file named `notes.pdf` in the same directory for local RAG support.
    * If no file is found, the agent will rely entirely on Web Search.
6.  **Run the Agent:** Execute the final cells to start the LangGraph workflow. The agent will print its thought process (Searching -> Generating -> Validating) in real-time.

## 📂 File Structure

* `Milestone1.ipynb`: The main application logic.
* `notes.pdf`: (Optional) User-provided context file for RAG.
