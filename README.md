# 🎓 Autonomous Learning Agent (ALA) 🤖📚

**An AI-powered Adaptive Tutor that PERCEIVES, ACTS, and ADAPTS using the Feynman Technique.**

> *"Education is not the learning of facts, but the training of the mind to think."* - Albert Einstein

---

## 🚀 Overview
The **Autonomous Learning Agent (ALA)** is not just a chatbot. It is a **Cognitive Architecture** designed to autonomously manage the educational lifecycle of a student.

Built on the cutting-edge **LangGraph** framework and powered by **Llama-3**, this agent acts as a personal professor. It doesn't rely on pre-written textbooks; instead, it:
1.  **🔍 Searches** the live web for the latest information on a topic.
2.  **🧠 Synthesizes** vast amounts of data into concise, structured Study Guides.
3.  **📝 Tests** your knowledge with dynamically generated Quizzes.
4.  **💡 Adapts** to your failures by explaining concepts simply (The Feynman Technique).

## 🌟 Why This Project?
Traditional learning tools are static. They don't know when you are confused.
*   **Static Quizzes** give you a score (e.g., "50%").
*   **ALA** gives you a **Strategy**. It identifies *exactly* why you failed and teaches you that specific concept before letting you try again.

---

## ✨ Key Features

### 1. 🌐 Autonomous Context Gathering
*   The agent uses **DuckDuckGo** to perform real-time research.
*   It reads multiple sources, filters out noise, and chunks relevant information for its memory.

### 2. 🧠 Cognitive State Machine (LangGraph)
*   The system is built as a **Directed Graph**.
*   It moves logically: `Gather` used `Process` -> `Study` -> `Quiz` -> `Evaluate`.
*   It maintains **State** (memory of your score, your gaps, and your attempts) across the entire session.

### 3. 🔥 The Feynman Remediation Loop
*   **The "Secret Sauce"**: If you fail a quiz (<70%), the agent enters a special "Remediation Mode".
*   It analyzes your wrong answers.
*   It uses the **Feynman Technique** to re-explain concepts using **Simple English** and **Analogies**.
*   It forces you to re-learn before you can re-test.

### 4. 📚 Dynamic Curriculum & Navigation
*   **Sequential Learning**: Progress through 4 Checkpoints (CP1: Intro -> CP2: Types -> CP3: Architecture -> CP4: Design).
*   **Full Control**: A professional CLI Menu lets you:
    *   `[N]ext`: Move forward if you passed.
    *   `[P]revious`: Go back to review.
    *   `[R]etry`: Attempt the quiz again.
    *   `[Q]uit`: Save and exit.

---

## 🛠️ Technical Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Orchestration** | 🦜🕸️ `LangGraph` | Manages the workflow and state transitions. |
| **Intelligence** | 🦙 `Llama-3-70b` | High-IQ reasoning for generation and grading. |
| **Infrastructure** | ☁️ `Groq API` | Lightning-fast inference engine. |
| **Memory** | 💾 `ChromaDB` | Vector storage for processing context. |
| **Search** | 🦆 `DuckDuckGo` | Privacy-focused tool for web research. |
| **Observability** | 🛠️ `LangSmith` | Tracing and debugging complex agent flows. |

---

## � Project Structure

```bash
autonomous-learning-agent/
├── 📄 main.py           # 🏁 Entry Point: Manages the CLI session & Navigation
├── 📄 graph.py          # 🕸️ The Brain: Defines Nodes, Edges, and Logic Flow
├── 📄 nodes.py          # ⚡ The Workers: Functions for Quiz, Study, Search
├── 📄 data.py           # 📚 The Books: Curriculum definitions (Topics, Objectives)
├── 📄 models.py         # 🧬 The DNA: Data types (AgentState, Checkpoint codes)
├── 📄 config.py         # ⚙️ Settings: API keys and Tool initialization
├── 📄 requirements.txt  # 📦 Dependencies: List of Python libraries
└── 📄 README.md         # 📖 Documentation: You are reading it!
```

---

## 📦 Installation & Setup

### 1️⃣ Clone the Repository
Get the code on your machine:
```bash
git clone https://github.com/your-username/autonomous-learning-agent.git
cd autonomous-learning-agent
```

### 2️⃣ Install Dependencies
We use `pip` to install the necessary libraries:
```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Secrets 🔑
Security is important! Create a `.env` file in the root folder and add your keys:
```env
# Get this from https://console.groq.com
GROQ_API_KEY="your_groq_api_key"

# Get these from https://smith.langchain.com (Optional but recommended)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY="your_langchain_api_key"
```

---

## 🎮 How to Run

1.  **Launch the Agent**:
    ```bash
    python main.py
    ```

2.  **Start Learning**:
    *   Select `cp1` when prompted.
    *   Read the **Study Guide** carefully.
    *   Answer the **4 Questions**.

3.  **Experience the Loop**:
    *   **Try Failing**: Intentionally pick wrong answers on CP2 to see the **Feynman Remediation** in action!
    *   **Try Passing**: Score 3/4 or 4/4 to unlock the `[N]ext` button.

---

## 🤝 Contributing
Contributions are welcome!
1.  Fork the Project.
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the Branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.

---

## 📸 Demo Output (Example Run)
Want to see it in action? Click below to expand a full session transcript where the user **Fails** a quiz and gets **Feynman Remediation**.

<details>
<summary><strong>CLICK TO VIEW TERMINAL OUTPUT 🔽</strong></summary>

```text
=== AUTONOMOUS LEARNING AGENT ===
Welcome to your adaptive learning session.
Available checkpoints: cp1, cp2, cp3, cp4

Which checkpoint do you want to start with? (Default: cp1)
> cp2

=== MODULE: CP2 ===
[define_checkpoint] Selected checkpoint: cp2 - Types of AI Agents
[gather_context] Web search query: Types of AI Agents...
[process_context] Chunking and embedding context...

=== STUDY GUIDE: CP2 ===
**Key Concepts**: Simple Reflex, Goal-Based, Utility-Based Agents...
========================================

[generate_quiz] Generating 4 MCQs...

=== CP2 QUIZ: Types of AI Agents ===
Question 1: Which agent uses a condition-action rule?
  Your answer: B (Incorrect)
...
[evaluate_quiz] Score: 50.0% (FAILED)

[feynman_remediation] Analyzing knowledge gaps...
=== FEYNMAN EXPLANATION ===
Imagine a **Simple Reflex Agent** is like a knee-jerk reaction: If you touch fire, move hand.
A **Goal Based Agent** is like playing Chess. It looks ahead to win the game.
You confused the two!
===========================

[generate_quiz] Generating MCQs...
(User retakes quiz and passes)
```
</details>

---

*Built with ❤️ for the Future of Education.*
