Autonomous AI Tutor (Milestone 2)
An intelligent, autonomous study assistant built with LangGraph and Hugging Face. This agent creates personalized study guides, generates conceptual quizzes, and rigorously grades student answers using a "Strict Examiner" persona.

Key Features
Smart RAG (Retrieval-Augmented Generation):

First checks your uploaded PDF Notes for relevant content.

If notes are insufficient or missing, it automatically falls back to Web Search (DuckDuckGo) to ensure comprehensive lessons.

Automated Lesson Generation:

Writes detailed 750-1000 word technical guides.

"No Math" Mode: Explains complex formulas using only plain English narratives (Zero LaTeX/Equations).

Adaptive Quizzing:

Generates 3-5 conceptual questions based specifically on the generated lesson.

Ensures questions focus on "Why" and "How" rather than rote calculation.

Rigorous Grading System:

Strict Examiner Persona: Penalizes vague answers and lack of technical keywords.

Detailed Feedback: Provides line-by-line critique and specific reasoning for every score.

Score Tracking: Auto-calculates final scores (Pass/Fail threshold: 80%).

Observability: Integrated with LangSmith for real-time tracing of agent thoughts and latency.

Tech Stack
Orchestration: LangChain, LangGraph

LLM: Qwen 2.5-72B-Instruct (via Hugging Face API)

Embeddings: Sentence-Transformers (all-MiniLM-L6-v2)

Vector Store: FAISS

Search: DuckDuckGo Search Tool

Frontend: Streamlit (or Python Notebook Interface)

Project Structure
Bash

├── app.py               # Main application logic (Streamlit/Python)
├── notes.pdf            # (Optional) User uploadable study notes
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
⚙️ Setup & Installation
1. Clone the Repository
Bash

git clone https://github.com/YOUR_USERNAME/ai-tutor-milestone-2.git
cd ai-tutor-milestone-2
2. Install Dependencies
Bash

pip install -r requirements.txt
(Ensure you have langchain, langgraph, streamlit, faiss-cpu, huggingface_hub installed)

3. Configure API Keys
You need a Hugging Face Token to run the LLM.

Create a .env file or export it in your terminal:

Bash

export HUGGINGFACEHUB_API_TOKEN="hf_your_token_here"
(Optional) For LangSmith tracing:

Bash

export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_API_KEY="ls_your_key_here"
How to Run
Option A: Streamlit UI (Recommended)
Bash

streamlit run app.py
Open the local URL provided (usually http://localhost:8501).

Enter your Hugging Face Token in the sidebar.

Select a topic (e.g., "CNNs", "GANs") or upload a PDF.

Click "Generate Study Material".

Option B: Jupyter Notebook
If using the .ipynb version, simply Run All Cells in order. The interaction will happen inside the output cells.

System Workflow (The "Graph")
The agent follows a strict logic flow managed by LangGraph:

Start: User selects a topic (e.g., "Backpropagation").

Check PDF: The agent searches notes.pdf.

Decision: Is the content relevant?

YES: Use PDF content.

NO: Trigger Web Search to find external info.

Generate: The LLM writes a 1000-word lesson (Plain English only).

Quiz: The LLM generates 5 conceptual questions.

User Input: Student types answers.

Grade: The "Strict Examiner" compares answers against the generated lesson and assigns a score (0-100).
