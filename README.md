# 🎓 Autonomous Learning Agent

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-latest-green.svg)](https://github.com/langchain-ai/langchain)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-orange.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An intelligent, adaptive tutoring system that guides learners through structured knowledge checkpoints with AI-powered assessment and Feynman Technique remediation.

## 🌟 Overview

This project implements an autonomous learning agent using LangGraph to create a personalized educational experience. The system:

- ✅ **Structures learning** through sequential checkpoints
- 🔍 **Gathers context** from user notes and web search
- 📝 **Generates quizzes** tailored to learning objectives
- 🎯 **Verifies understanding** with 70% mastery threshold
- 🧠 **Applies Feynman Technique** for adaptive remediation
- 📊 **Tracks progress** and enforces mastery-based advancement

### Key Features

| Feature | Description |
|---------|-------------|
| **Adaptive Context Gathering** | Combines user-provided notes with real-time web search |
| **Smart Content Validation** | LLM-powered relevance scoring ensures quality materials |
| **Vector-Based Processing** | Context chunking and embedding for efficient retrieval |
| **Dynamic Quiz Generation** | AI-created MCQs tailored to checkpoint objectives |
| **Feynman Remediation** | Simplified explanations with analogies for failed concepts |
| **Mastery-Based Progression** | Must achieve 70%+ to advance, with 3 retry attempts |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Learning Workflow                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
                 ┌──────────────────────┐
                 │ Define Checkpoint    │
                 │ (Topic + Objectives) │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │  Gather Context      │
                 │ (Notes + Web Search) │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │  Validate Context    │
                 │  (LLM Relevance)     │
                 └──────────┬───────────┘
                            ↓
                    ┌───────┴───────┐
                    │ Score < 4?    │
              Yes ──┤ Attempts < 3? ├── No
                    └───────┬───────┘
                            ↓ (Process)
                 ┌──────────────────────┐
                 │  Process Context     │
                 │ (Chunk + Embed)      │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │ Create Study Guide   │
                 │   (Key Concepts)     │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │   Generate Quiz      │
                 │   (4 MCQs)           │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │     Take Quiz        │
                 │  (User Input)        │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │   Evaluate Quiz      │
                 │   (Score %)          │
                 └──────────┬───────────┘
                            ↓
                    ┌───────┴────────┐
                    │ Score >= 70%?  │
             Yes ───┤                ├── No
                    └───────┬────────┘
                            │            ↓
                            │    ┌───────────────┐
                            │    │ Loops < 3?    │
                            │    └───────┬───────┘
                            │            ↓ Yes
                            │    ┌───────────────┐
                            │    │   Feynman     │
                            │    │  Remediation  │
                            │    └───────┬───────┘
                            │            │
                            │            └──────────┐
                            ↓                       ↓
                       ┌─────────┐         (Back to Quiz)
                       │   END   │
                       │(Success)│
                       └─────────┘
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Groq API key (free tier available at [console.groq.com](https://console.groq.com))
- LangSmith API key (optional, for tracing)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/autonomous-learning-agent.git
cd autonomous-learning-agent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```env
# Required: Groq API Key
GROQ_API_KEY=your_groq_api_key_here

# Optional: LangSmith Tracing (for debugging)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=AutonomousLearningAgent
```

> **Getting API Keys:**
> - **Groq**: Sign up at [console.groq.com](https://console.groq.com) → API Keys
> - **LangSmith** (optional): Visit [smith.langchain.com](https://smith.langchain.com)

### Quick Start

```bash
python main.py
```

**First-time workflow:**
1. Select a checkpoint (default: `cp1`)
2. Optionally paste study notes (or press Enter to skip)
3. Review generated study guide
4. Take the 4-question quiz
5. Review results and explanations
6. Progress to next checkpoint (if passed) or retry

## 📚 Project Structure

```
autonomous-learning-agent/
│
├── main.py                 # Entry point, user interface, navigation logic
├── graph.py                # LangGraph workflow definition
├── nodes.py                # Individual workflow nodes (functions)
├── models.py               # Type definitions (AgentState, Checkpoint)
├── data.py                 # Checkpoint definitions (cp1-cp4)
├── config.py               # LLM and tool initialization
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (API keys)
└── README.md               # This file
```

### Key Files Explained

| File | Purpose | Key Components |
|------|---------|----------------|
| **main.py** | User interaction loop | Checkpoint selection, quiz interface, navigation |
| **graph.py** | Workflow orchestration | StateGraph definition, conditional edges |
| **nodes.py** | Business logic | 11 node functions (context gathering, quiz generation, etc.) |
| **models.py** | Data structures | `AgentState` (12 fields), `Checkpoint` (4 fields) |
| **data.py** | Learning content | 4 checkpoints on AI Agents topic |
| **config.py** | External integrations | Groq LLM, DuckDuckGo search |

## 🎯 Learning Checkpoints

The system currently includes 4 checkpoints on **AI Agents**:

| ID | Topic | Objectives | Success Criteria |
|----|-------|------------|------------------|
| **cp1** | Introduction to AI Agents | Define AI agents, explain perception/action, list examples | Clear definition with component descriptions |
| **cp2** | Types of AI Agents | Explain agent types (reflex, model-based, goal-based, utility-based) | Name and explain main types |
| **cp3** | Architecture of AI Agents | Explain architecture, sensors/actuators, environment interaction | Describe structure and interactions |
| **cp4** | AI Agent Environments | Explain environment types, observable vs. partial, relate to behavior | Classify environments and their impact |

### Adding Custom Checkpoints

Edit `data.py`:

```python
CHECKPOINTS = {
    "cp5": {
        "id": "cp5",
        "topic": "Your Topic Here",
        "objectives": [
            "Learning objective 1",
            "Learning objective 2",
            # Add 2-4 objectives
        ],
        "success_criteria": "Learner can demonstrate X and Y.",
    }
}
```

## 🔧 Technical Stack

### Core Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Programming language | 3.8+ |
| **LangGraph** | Workflow orchestration | Latest |
| **LangChain** | LLM integration framework | Latest |
| **Groq** | LLM inference (Llama 3.3 70B) | API |
| **DuckDuckGo** | Web search (no API key) | `duckduckgo-search` |

### Data Processing

| Component | Library | Purpose |
|-----------|---------|---------|
| **Text Splitting** | `RecursiveCharacterTextSplitter` | 500-char chunks, 50-char overlap |
| **Embeddings** | `HuggingFaceEmbeddings` | all-MiniLM-L6-v2 model (384-dim) |
| **Vector Store** | `Chroma` | Ephemeral storage for context chunks |

### LLM Configuration

```python
ChatGroq(
    model="llama-3.3-70b-versatile",  # 70B parameter model
    temperature=0.2                    # Balanced creativity/consistency
)
```

**Model Choice Rationale:**
- **Llama 3.3 70B**: Strong reasoning for educational tasks
- **Temperature 0.2**: Deterministic enough for assessments, creative enough for explanations
- **Groq Inference**: Sub-second response times critical for real-time tutoring

## 📊 Workflow Details

### 1. Context Gathering & Validation

**Process:**
```python
1. Collect user notes (if provided)
2. Execute web search: f"{topic} - {objectives}"
3. Combine materials
4. LLM scores relevance (1-5)
5. If score < 4 and attempts < 3: retry
6. Otherwise: proceed to processing
```

**Validation Prompt Template:**
```
Judge how relevant the context is to the objectives.
Scale: 1 = useless, 5 = highly relevant.
Reply with a single number.
```

### 2. Quiz Generation

**Specifications:**
- Exactly 4 MCQs per checkpoint
- 4 options per question (A-D)
- Includes correct answer + explanation
- JSON format for parsing

**Generation Prompt Template:**
```
Generate EXACTLY 4 MCQs based on context.
Output Format: Pure JSON array (no markdown).
[
  {
    "question": "...",
    "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
    "correct_option": "B",
    "explanation": "..."
  }
]
```

### 3. Evaluation & Remediation

**Scoring:**
- Pass threshold: ≥70%
- Formula: `(correct_answers / total_questions) × 100`

**Feynman Remediation:**
- Triggered when score < 70%
- Maximum 3 remediation loops
- Simplification strategy:
  - Plain English (no jargon)
  - Analogies and metaphors
  - Maximum 200 words
  - Focus on failed concepts only

**Feynman Prompt Template:**
```
You are an expert tutor using the Feynman Technique.
The student failed these concepts: [gaps]
Task:
1. Explain in simple, plain English
2. Use an analogy if possible
3. Keep it concise (max 200 words)
```

## 🐛 Debugging & Monitoring

### LangSmith Tracing

Enable detailed execution tracing:

1. Set `LANGCHAIN_TRACING_V2=true` in `.env`
2. Run application
3. View traces at [smith.langchain.com](https://smith.langchain.com)

**What you'll see:**
- Node execution order
- LLM input/output for each call
- State transitions between nodes
- Conditional edge decisions
- Timing information

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **JSON parsing error in quiz** | LLM returns markdown-wrapped JSON | Handled automatically with `.replace("```json", "")` |
| **Low relevance scores** | Generic search queries | Refine objectives to be more specific |
| **Web search timeout** | DuckDuckGo rate limiting | Wait 1 minute, retry |
| **Empty context** | Search returned no results | Provide user notes as fallback |

## 🎯 Milestones & Progress

### ✅ Milestone 1: Checkpoint Structure (Weeks 1-2)
- [x] Project environment setup
- [x] Checkpoint data structure
- [x] Context gathering (notes + web search)
- [x] Context validation with LLM scoring

**Evaluation:** Context relevance >4/5 average ✓

### ✅ Milestone 2: Context Processing & Verification (Weeks 3-4)
- [x] Text chunking and embedding
- [x] Vector store integration (Chroma)
- [x] Quiz generation (4 MCQs)
- [x] Automated scoring against 70% threshold

**Evaluation:** 80%+ question relevance, 90%+ scoring accuracy ✓

### ✅ Milestone 3: Feynman Implementation (Weeks 5-6)
- [x] Knowledge gap identification
- [x] Simplified explanation generation
- [x] Remediation loop integration
- [x] Re-assessment after teaching

**Evaluation:** 80%+ explanations rated "simpler", 100% correct loop routing ✓

### ✅ Milestone 4: Integration & Testing (Weeks 7-8)
- [x] Multi-checkpoint progression
- [x] End-to-end testing (3+ checkpoint paths)
- [x] Navigation controls (Next/Retry/Previous/Quit)
- [x] Detailed quiz review display

**Evaluation:** 80%+ successful path completion ✓


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain Team** for the incredible framework ecosystem
- **Groq** for fast, affordable LLM inference
- **HuggingFace** for open-source embedding models
- **Feynman** for the timeless teaching technique

 
**Made with ❤️ by [ Chaitanya Sai ]**

*Empowering learners through adaptive AI tutoring*
