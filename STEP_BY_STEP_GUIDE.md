# 👣 Complete User Manual: Autonomous Learning Agent

**A Comprehensive "Zero-to-Hero" Guide for Installation and Execution**

---

## 📚 Table of Contents
1.  [Phase 1: Environment Setup](#phase1)
2.  [Phase 2: Configuration](#phase2)
3.  [Phase 3: Running the Simulation](#phase3)
4.  [Phase 4: Understanding the Output](#phase4)
5.  [Troubleshooting & FAQ](#faq)

---

## <a name="phase1"></a>Phase 1: Environment Setup ✅
*Before we run the AI, we must prepare the computer.*

### Step 1.1: Verify Python Installation
This project requires Python language support.
1.  Open your **Command Prompt** (Windows) or **Terminal** (Mac/Linux).
2.  Type the following command and press Enter:
    ```bash
    python --version
    ```
3.  **Check Output**:
    *   ✅ `Python 3.10.x` (or 3.11, 3.12) -> **Good**. Proceed.
    *   ❌ `Python not found` -> **Stop**. Download it from [python.org](https://www.python.org/downloads/).

### Step 1.2: Navigate to Project Directory
We need to be inside the folder where the code lives.
1.  Locate the folder on your Desktop.
2.  In your terminal, command the computer to go there:
    ```bash
    cd path/to/autonomous_learning_agent
    ```

### Step 1.3: Install Dependencies
The agent relies on specialized brain-power libraries.
1.  Run the installer command:
    ```bash
    pip install -r requirements.txt
    ```
2.  **What to watch for**: You will see many lines of text saying `Downloading...` and `Installing...`.
3.  **Completion**: Ensure the last line says `Successfully installed...`.

---

## <a name="phase2"></a>Phase 2: Configuration ⚙️
*We need to give the Agent its "Keys" to access the internet and the LLM.*

### Step 2.1: Locate the Environment File
1.  Look for a file named `.env` in your project folder.
2.  *(Note: If you only see `.env.example`, make a copy of it and rename it to just `.env`)*.

### Step 2.2: Add your API Keys
1.  Open `.env` with a text editor (Notepad or VS Code).
2.  Paste your keys carefully. It should look exactly like this:
    ```env
    GROQ_API_KEY="gsk_YourActualKeyHere12345"
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_API_KEY="lsv2_YourLangChainKeyHere12345"
    ```
3.  **Save** the file (Ctrl+S).

---

## <a name="phase3"></a>Phase 3: Running the Simulation 🚀
*Now the magic happens. We will start the AI agent.*

### Step 3.1: Launch Command
In your terminal, inside the project folder, type:
```bash
python main.py
```

### Step 3.2: Select a Module
The agent will wake up and ask you where to begin.
*   **Screen Output**: `Which checkpoint do you want to start with? (Default: cp1)`
*   **Action**: Type `cp1` and press **Enter**.
*   *Why?*: Checkpoint 1 is the "Introduction". It is the best place to start.

---

## <a name="phase4"></a>Phase 4: Understanding the Output 👁️
*Here is a guide to what you will see on the screen.*

### 🔍 Stage 1: The Research (Gathering Context)
> **You will see:** `[gather_context] Web search query: Introduction to AI Agents`
>
> **What is happening?**
> The Agent works like a frantic student in a library. It is continuously searching DuckDuckGo for definitions, articles, and papers about the topic. It reads them in milliseconds.

### 📚 Stage 2: The Lesson (Study Guide)
> **You will see:** `=== STUDY GUIDE: CP1 ===` followed by bullet points.
>
> **What is happening?**
> The Agent has synthesized all the web search results into a clean, easy-to-read summary. **READ THIS!** The answers to the quiz are hidden in this text.

### 📝 Stage 3: The Exam (Quiz)
> **You will see:** `Question 1: What is an agent?`
>
> **Action**: Type `A`, `B`, `C`, or `D`.
> *   The quiz always has **4 Questions**.
> *   You need 3 correct to pass.

### 🔄 Stage 4: The Adaptation (Pass or Fail)

#### Scenario A: The Happy Path (PASS)
*   **Output**: `Score: 100.0% (PASSED)`
*   **Menu**: `Choose action: [N]ext`
*   **Meaning**: You demonstrated mastery. You are allowed to proceed to CP2.

#### Scenario B: The Learning Path (FAIL)
*   **Output**: `Score: 50.0% (FAILED)`
*   **Intervention**: `=== FEYNMAN EXPLANATION ===`
*   **What is happening?**
    The Agent identifies *why* you failed. It generates a custom explanation using a metaphor (e.g., "Think of an Agent like a Thermostat...").
*   **Next Step**: It loops you back to the Quiz to try again instantly.

---

## <a name="faq"></a>Troubleshooting & FAQ 🔧

### Q: I get an error `ModuleNotFoundError: No module named 'langgraph'`?
**A:** You didn't install the libraries correctly.
**Fix:** Run `pip install langgraph langchain-groq` again.

### Q: It says `api_key not found`?
**A:** Your `.env` file is empty or named wrong.
**Fix:** Make sure the file is named exactly `.env` (no `.txt` at the end) and has your `gsk_...` key inside.

### Q: The Quiz only gave me 3 questions?
**A:** This is a rare randomness issue with AI.
**Fix:** Simply restart the program (`Ctrl+C` then `python main.py`). The code is designed to force 4, so it should correct itself.

### Q: Can I go back to the previous topic?
**A:** Yes! If you are on CP2 or higher, the menu will show `[P]revious`. Select it to review earlier material.

---
**Enjoy your learning journey!** 🎓
