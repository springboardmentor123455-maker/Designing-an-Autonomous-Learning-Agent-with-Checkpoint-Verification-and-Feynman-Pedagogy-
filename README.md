# Designing-an-Autonomous-Learning-Agent-with-Checkpoint-Verification-and-Feynman-Pedagogy-

# 🧠 Adaptive AI Tutor (LangGraph + Groq + Tavily + Streamlit)

An **Adaptive AI Tutor** that teaches concepts step-by-step, generates short test questions, evaluates answers, and if the learner fails, it automatically switches to **Feynman Technique** teaching mode and re-tests again.

This project uses:

- **LangGraph** for agent workflow + state handling
- **Groq LLM (LangChain Groq)** for tutoring + question generation + grading
- **Tavily Search** for web-based learning content
- **SentenceTransformers embeddings** for semantic chunk retrieval (temporary vector store)
- **Streamlit UI** for interactive learning and testing

---

## 🚀 Features

- ✅ Select a checkpoint topic (or enter a custom topic)
- ✅ Automatically fetches learning content from the web (Tavily)
- ✅ Merges user notes + generated context into one clean explanation
- ✅ Splits context into chunks + builds a temporary vector store
- ✅ Generates **3 short beginner questions** (max 18 words)
- ✅ Grades answers using a strict scoring bucket: **0 / 40 / 70 / 100**
- ✅ If score is low → enters **Feynman Teaching Mode** and retries
- ✅ Attempts limit included (default: 3)
- ✅ Optional raw LLM logging + PDF export support

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

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 📦 requirements.txt

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

This project requires API keys for Groq + Tavily (and optional LangSmith).

### Option A (Recommended): Export in Terminal

**Windows (PowerShell)**

```powershell
$env:GROQ_API_KEY="YOUR_TOKEN"
$env:TAVILY_API_KEY="YOUR_TOKEN"
$env:LANGSMITH_TRACING="true"
$env:LANGSMITH_API_KEY="YOUR_TOKEN"
```

**Mac/Linux**

```bash
export GROQ_API_KEY="YOUR_TOKEN"
export TAVILY_API_KEY="YOUR_TOKEN"
export LANGSMITH_TRACING="true"
export LANGSMITH_API_KEY="YOUR_TOKEN"
```

### Option B: Put inside `backend.py` (Not recommended for GitHub)

⚠️ Do not upload tokens to GitHub.

---

## ▶️ Run the App (Streamlit)

```bash
streamlit run app.py
```

Then open the URL shown in terminal (usually):

```text
http://localhost:8501
```

---

## 🧪 Run Backend in Interactive Mode (CLI)

You can also run the backend in terminal mode:

```bash
python backend.py
```

It will ask:

- `1` → interactive learning run (generate questions & answer interactively)
- `2` → evaluation suite (automated test)

---

## 📌 Learning Flow (How it Works)

1. **Checkpoint selected**
2. **Context gathered**
   - user notes (optional)
   - PDFs (optional)
   - web search (always)
3. **Context validated**
   - semantic relevance filter using embeddings
4. **Chunking + vector store**
   - chunks are embedded using SentenceTransformer
5. **Question generation**
   - 3 questions (18 words max)
6. **Answer verification**
   - overlap check + LLM grading
7. **Feynman remediation**
   - if score < threshold → simplified teaching
8. **Retry loop**
   - repeats until passed or attempts exhausted

---

## 🧠 How the Tutor Scores Answers

Each answer is graded into one of these buckets:

- **0** → wrong or unrelated
- **40** → partial understanding
- **70** → correct with minor gaps
- **100** → fully correct

Passing condition:

- All questions must score **>= 70**

---

## 🧩 Checkpoints Included

Currently included checkpoints:

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

You can also select **➕ Custom Topic** in the sidebar and enter any topic name.

---

## 🛡️ Notes & Security

- Never commit API keys to GitHub.
- Use environment variables or Streamlit secrets.
- Web search is performed using Tavily, so results depend on internet + query.

---

## 🌟 Future Improvements

- Add PDF upload inside Streamlit UI
- Save learner progress per checkpoint
- Add more checkpoints and difficulty levels
- Add voice-based learning mode
- Add database support for user sessions

---

## 📜 License

This project is open-source and free to use for learning and educational purposes.
