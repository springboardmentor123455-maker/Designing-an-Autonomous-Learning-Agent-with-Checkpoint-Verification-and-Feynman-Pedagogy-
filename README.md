# Designing an Autonomous Learning Agent with Checkpoint Verification and Feynman Pedagogy

# 🧠 Adaptive AI Tutor (LangGraph + Groq + Tavily + Streamlit)

An **Adaptive AI Tutor** that teaches concepts step-by-step, generates short test questions, evaluates learner answers, and if the learner struggles, it automatically switches to **Feynman Technique** teaching mode and re-tests until mastery (or attempts run out).

This project is designed as a complete learning pipeline that includes:

- 📚 **Content generation + enrichment**
- 🧩 **Chunking + semantic retrieval**
- 📝 **Adaptive questioning**
- ✅ **Checkpoint verification**
- 🧠 **Feynman remediation**
- 🎛️ **Streamlit UI**

---

## ✨ Key Technologies Used

- **LangGraph** → workflow orchestration + state-based agent execution  
- **Groq LLM (LangChain Groq)** → explanation writing, question generation, answer scoring  
- **Tavily Search** → fetches web content as learning context  
- **SentenceTransformers + NumPy** → embeddings + semantic retrieval for better grading  
- **PyPDF2** → optional PDF reading support  
- **ReportLab** → optional PDF export for raw LLM logs  
- **Streamlit** → frontend UI for interactive learning  

---

## 🚀 Features

### 🎯 Learning & Teaching
- ✅ Select a checkpoint topic (or choose **Custom Topic**)
- ✅ Generates structured learning content based on objectives
- ✅ Supports optional learner notes (used to enrich final context)
- ✅ Fetches trusted web content automatically using Tavily
- ✅ Summarizes large content to keep it clean and relevant

### 🧩 Context Processing
- ✅ Splits content into overlapping chunks (chunking strategy)
- ✅ Builds a temporary in-memory vector store using embeddings
- ✅ Retrieves the top-k most relevant chunks for question generation & grading

### 📝 Adaptive Testing
- ✅ Generates **exactly 3 short questions**
- ✅ Questions follow strict rules:
  - 1 sentence only
  - Max 18 words
  - Beginner-friendly
  - Must end with `?`
- ✅ Uses different question styles across attempts (role / process / why / application)

### ✅ Answer Evaluation
- ✅ Rejects answers that are too short (less than 30 characters)
- ✅ Rejects unrelated answers using keyword overlap guard
- ✅ Scores answers strictly using buckets:
 
### 🧠 Feynman Teaching Mode
- ✅ Automatically activates if the learner fails
- ✅ Generates simplified teaching focused only on weak concepts
- ✅ Re-tests learner with new questions
- ✅ Attempts are limited (default: 3)

---

## 🗂️ Project Structure

```text
adaptive-ai-tutor/
│
├── backend.py          # LangGraph workflow + tutoring logic
├── app.py              # Streamlit UI
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```

---

## ⚙️ Setup Instructions (Windows Only)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/adaptive-ai-tutor.git
cd adaptive-ai-tutor
```

---

### 2️⃣ Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

If activation works, you will see something like:

```text
(venv)
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 📦 requirements.txt (Example)

Create a `requirements.txt` like this:

```txt
streamlit
langgraph
langchain-groq
tavily-python
sentence-transformers
numpy
PyPDF2
reportlab
langsmith
ipython
```

---

## 🔑 Environment Variables (IMPORTANT)

This project requires API keys for:

- **Groq** → LLM inference  
- **Tavily** → web search context  
- **LangSmith** (optional) → tracing & debugging  

### ✅ Recommended: Set Keys in Windows PowerShell

Open PowerShell and run:

```powershell
$env:GROQ_API_KEY="YOUR_TOKEN"
$env:TAVILY_API_KEY="YOUR_TOKEN"
$env:LANGSMITH_TRACING="true"
$env:LANGSMITH_API_KEY="YOUR_TOKEN"
```

⚠️ These keys apply only to the current terminal session.

---


## ▶️ Run the Streamlit App

Start the UI:

```bash
streamlit run app.py
```

Then open the URL shown in terminal (usually):

```text
http://localhost:8501
```

---

## 🧪 Run Backend in Terminal Mode (Optional)

You can run the backend without Streamlit:

```bash
python backend.py
```

It will ask you to choose:

- `1` → interactive learning run (answer questions manually)
- `2` → evaluation suite (automated testing)

---

## 📌 How the Tutor Works (Pipeline Overview)

### Step 1: Checkpoint Selection
User selects a checkpoint like:

- CP1 — Basics of Neural Networks
- CP2 — Loss Functions
- ...
- CP10 — Regularization Techniques

Or selects **Custom Topic**.

---

### Step 2: Context Gathering
The tutor gathers learning content from:

- **User notes** (optional)
- **PDFs** (optional, supported in backend)
- **Web search** (always enabled via Tavily)

Then it merges everything into one clean explanation.

---

### Step 3: Context Validation
The system checks relevance using embeddings:

- If content is unrelated → it refetches from the web
- It also scores coverage of objectives (1–5)

---

### Step 4: Chunking + Temporary Vector Store
The context is split into chunks:

- Chunk size: **1200**
- Overlap: **250**
- Minimum chunk length: **300**

Embeddings are generated using:

- `all-MiniLM-L6-v2`

This allows top-k retrieval for grading.

---

### Step 5: Question Generation
The tutor generates 3 questions per attempt:

- Short and simple
- Different style per attempt
- Focused on weak concepts

---

### Step 6: Answer Verification
Each answer is checked using:

1. **Short answer filter**
2. **Keyword overlap guard**
3. **LLM-based scoring bucket**

Final pass condition:

- All answers must score **>= 70**

---

### Step 7: Feynman Remediation (If Failed)
If learner fails:

- Tutor explains only the weak concepts
- Uses simple step-by-step teaching
- Generates new questions again
- Repeats until pass or attempts finish

---

## 🧠 Scoring System

Each answer gets one of:

- **0** → wrong/unrelated
- **40** → partial understanding
- **70** → correct with minor gaps
- **100** → fully correct

Overall score is average of the 3 answers.

Passing rule:

- Must score **>= 70 on all questions**

---

## 🧩 Checkpoints Included

The current learning path includes:

- CP1 — Basics of Neural Networks  
- CP2 — Loss Functions  
- CP3 — Gradient Descent  
- CP4 — Learning Rate  
- CP5 — Activation Functions  
- CP6 — Backpropagation  
- CP7 — Overfitting and Generalization  
- CP8 — Train Validation and Test Data  
- CP9 — Weight Initialization  
- CP10 — Regularization Techniques  

---

## 🛡️ Notes & Security

- Never commit API keys to GitHub
- Always use environment variables
- Web results depend on Tavily + internet
- Scoring is strict by design to encourage real understanding

---

## 🌟 Future Improvements

- Add PDF upload option inside Streamlit UI
- Add progress tracking per checkpoint
- Add difficulty levels (Beginner / Intermediate / Advanced)
- Add database support for multi-user learning sessions
- Add better UI analytics (weak topics chart)

---

## 📜 License

This project is open-source and free to use for learning and educational purposes.
