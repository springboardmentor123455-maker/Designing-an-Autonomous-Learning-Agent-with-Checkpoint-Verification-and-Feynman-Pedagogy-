# 🎓 Autonomous Learning Agent - Technical Documentation

**Project:** Autonomous Learning Agent

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Architecture](#-architecture)
3. [Project Structure](#-project-structure)
4. [Core Components](#-core-components)
5. [Workflow & State Management](#-workflow--state-management)
6. [API Reference](#-api-reference)
7. [Database Schema](#-database-schema)
8. [Configuration](#-configuration)
9. [Development Milestones](#-development-milestones)
10. [Dependencies](#-dependencies)

---

## 🌟 Project Overview

The **Autonomous Learning Agent** is an advanced AI-powered educational platform that implements adaptive teaching methodologies through an agentic architecture. Built with **LangGraph** and **LangChain**, it provides personalized learning experiences through multi-checkpoint progression, intelligent assessment, and Feynman teaching techniques.

### Key Features

- **🤖 Agentic Architecture**: LangGraph-based autonomous workflow orchestration
- **🎯 Adaptive Learning**: Automatic Feynman teaching when learners struggle (< 70% score)
- **📊 Multi-Checkpoint Progression**: Sequential topic-based learning (2-5 checkpoints per session)
- **🔍 Intelligent Context Gathering**: Web search + vector embeddings for relevant content
- **📝 Automated Assessment**: LLM-powered question generation and answer evaluation
- **📄 Professional Reports**: Comprehensive PDF session summaries
- **📈 Historical Tracking**: SQLite database with performance analytics
- **⚡ Real-time Dashboard**: Interactive Plotly visualizations

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Python 3.8+ |
| **Web Interface** | Streamlit 1.28+ |
| **Workflow Engine** | LangGraph 0.2+ |
| **LLM Framework** | LangChain 0.3+ |
| **LLM Provider** | Google Gemini (via langchain-google-genai) |
| **Vector Store** | FAISS (Facebook AI Similarity Search) |
| **Embeddings** | HuggingFace sentence-transformers/all-MiniLM-L6-v2 |
| **Web Search** | Serp API |
| **Database** | SQLite with SQLAlchemy |
| **PDF Generation** | ReportLab 4.0+ |
| **Analytics** | Plotly 5.17+ & Pandas 2.1+ |

---

## 🏗 Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  ┌─────────────────────┐         ┌─────────────────────┐        │
│  │   Streamlit App     │         │   CLI Interface     │        │
│  │    (app.py)         │         │    (main.py)        │        │
│  └──────────┬──────────┘         └──────────┬──────────┘        │
└─────────────┼────────────────────────────────┼──────────────────┘
              │                                │
              └────────────────┬───────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│                      LANGGRAPH WORKFLOW                          │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              Learning Graph (StateGraph)                   │  │
│  │                                                            │  │
│  │  Define → Gather → Validate → Process → Generate →         │  │
│  │  Evaluate → [Pass? → Next] [Fail? → Feynman → Retry]       │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│                       CORE MODULES                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │ Context Manager  │  │ Vector Store Mgr │  │ Question Gen   │  │
│  │ (Web Search +    │  │ (FAISS +         │  │ (LLM-powered)  │  │
│  │  Chunking)       │  │  Embeddings)     │  │                │  │
│  └──────────────────┘  └──────────────────┘  └────────────────┘  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │Understanding     │  │ Feynman Teacher  │  │ PDF Generator  │  │
│  │Verifier          │  │ (Adaptive        │  │ (Reports)      │  │
│  │(Scoring)         │  │  Teaching)       │  │                │  │
│  └──────────────────┘  └──────────────────┘  └────────────────┘  │
└──────────────────────────────┬───────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────── ┐
│                    EXTERNAL SERVICES                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐   │
│  │ Google Gemini    │  │ Serp API         │  │ HuggingFace    │   │
│  │ (LLM)            │  │ (Web Search)     │  │ (Embeddings)   │   │
│  └──────────────────┘  └──────────────────┘  └────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│                      DATA PERSISTENCE                            │
│  ┌──────────────────┐  ┌──────────────────┐                      │
│  │ SQLite Database  │  │ Session Files    │                      │
│  │ (History)        │  │ (Temp Storage)   │                      │
│  └──────────────────┘  └──────────────────┘                      │
└───────────────────────────────────────────────────────────────────┘
```

### Workflow State Machine

```
                    START
                      │
                      ▼
            ┌─────────────────┐
            │ Define          │
            │ Checkpoint      │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Gather          │
            │ Context         │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Validate        │◄──────┐
            │ Context         │       │
            └────────┬────────┘       │
                     │                │
                 Valid?               │
                 │   │                │
                Yes  No               │
                 │   │                │
                 │   └─Retry──────────┘
                 │    (Max 3)
                 ▼
            ┌─────────────────┐
            │ Process Context │
            │ (Embeddings)    │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Generate        │
            │ Questions       │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Collect User    │
            │ Answers         │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Evaluate        │
            │ Answers         │
            └────────┬────────┘
                     │
                Score >= 70%?
                 │       │
                Yes      No
                 │       │
                 │       ▼
                 │  ┌─────────────────┐
                 │  │ Feynman         │
                 │  │ Teaching        │
                 │  └────────┬────────┘
                 │           │
                 │    Attempts < 3?
                 │           │
                 │          Yes
                 │           │
                 │           └─Regenerate Questions
                 │
                 ▼
        More Checkpoints?
                 │
                Yes ────► Next Checkpoint
                 │
                No
                 │
                 ▼
               COMPLETE
```

---

## 📁 Project Structure

```
Tutor/
│
├── 📄 app.py                          # Streamlit web interface (986 lines)
├── 📄 main.py                         # CLI demo script (218 lines)
├── 📄 requirements.txt                # Python dependencies
├── 📄 README.md                       # User documentation
├── 📄 LICENSE                         # MIT License
├── 📄 .env.example                    # Environment variables template
├── 📄 .env                            # Environment variables (API keys)
├── 📄 .gitignore                      # Git ignore rules
│
├── 📁 src/                            # Source code
│   ├── 📄 __init__.py
│   │
│   ├── 📁 models/                     # Data models
│   │   ├── 📄 __init__.py
│   │   ├── 📄 checkpoint.py           # Checkpoint & GatheredContext models
│   │   └── 📄 state.py                # LangGraph state definition
│   │
│   ├── 📁 graph/                      # LangGraph workflow
│   │   ├── 📄 __init__.py
│   │   └── 📄 learning_graph.py       # Main workflow orchestration (756 lines)
│   │
│   ├── 📁 modules/                    # Core business logic
│   │   ├── 📄 __init__.py
│   │   ├── 📄 context_manager.py      # Context gathering & validation (336 lines)
│   │   ├── 📄 vector_store_manager.py # FAISS vector operations (106 lines)
│   │   ├── 📄 question_generator.py   # Question generation (179 lines)
│   │   ├── 📄 understanding_verifier.py # Answer evaluation (222 lines)
│   │   └── 📄 feynman_teacher.py      # Feynman explanations (240 lines)
│   │
│   └── 📁 utils/                      # Utility functions
│       ├── 📄 __init__.py
│       ├── 📄 llm_provider.py         # LLM initialization (255 lines)
│       ├── 📄 search_tools.py         # Web search integration (152 lines)
│       ├── 📄 pdf_generator.py        # PDF report generation (369 lines)
│       └── 📄 database_manager.py     # SQLite operations (296 lines)
│
├── 📁 venv/                           # Virtual environment (generated)
│
└── 📄 learning_sessions.db            # SQLite database (generated)
```

### File Descriptions

#### **Root Files**

| File | Purpose | Lines |
|------|---------|-------|
| `app.py` | Main Streamlit web application with full UI | 986 |
| `main.py` | Command-line demo script for testing | 218 |
| `requirements.txt` | Python package dependencies | 24 |
| `README.md` | User-facing documentation and setup guide | 860 |

#### **Source Code (`src/`)**

##### **Models (`src/models/`)**

| File | Purpose | Key Classes |
|------|---------|-------------|
| `checkpoint.py` | Data models for learning checkpoints | `Checkpoint`, `GatheredContext` |
| `state.py` | LangGraph state definition | `LearningState`, `create_initial_state()` |

##### **Graph (`src/graph/`)**

| File | Purpose | Key Components |
|------|---------|----------------|
| `learning_graph.py` | LangGraph workflow orchestration | `LearningGraph`, 15+ workflow nodes |

##### **Modules (`src/modules/`)**

| File | Purpose | Key Methods |
|------|---------|------------|
| `context_manager.py` | Web search, chunking, validation | `gather_context()`, `validate_context()` |
| `vector_store_manager.py` | FAISS vector operations | `create_vector_store()`, `similarity_search()` |
| `question_generator.py` | LLM-based question generation | `generate_questions()` |
| `understanding_verifier.py` | Answer scoring and evaluation | `evaluate_answers()` |
| `feynman_teacher.py` | Adaptive Feynman teaching | `generate_explanations()` |

##### **Utils (`src/utils/`)**

| File | Purpose | Key Functions |
|------|---------|---------------|
| `llm_provider.py` | LLM initialization (Google Gemini) | `get_llm()`, `get_reasoning_llm()` |
| `search_tools.py` | Web search (Tavily/DuckDuckGo/Google) | `search_for_learning_content()` |
| `pdf_generator.py` | PDF report generation | `LearningReportGenerator.generate_report()` |
| `database_manager.py` | SQLite CRUD operations | `SessionDatabase.save_session()` |

---

## 🔧 Core Components

### 1. Checkpoint Model

**File:** `src/models/checkpoint.py`

```python
@dataclass
class Checkpoint:
    """Represents a learning checkpoint with objectives."""
    topic: str                          # Main topic
    objectives: List[str]               # Learning objectives
    difficulty_level: str = "beginner" # beginner/intermediate/advanced
    estimated_time_minutes: int = 30   # Estimated completion time
    prerequisites: List[str] = []      # Required prior knowledge
    created_at: datetime               # Creation timestamp
```

**Purpose:** Defines a single learning unit with clear objectives.

### 2. Learning State

**File:** `src/models/state.py`

The `LearningState` is a TypedDict that maintains workflow state across all nodes:

```python
class LearningState(TypedDict):
    # Checkpoint management (Milestone 4)
    all_checkpoints: List[Checkpoint]       # All checkpoints in session
    current_checkpoint_index: int           # Current checkpoint index
    checkpoint: Optional[Checkpoint]        # Current checkpoint
    completed_checkpoints: List[int]        # Completed indices
    
    # Context gathering (Milestone 1)
    user_notes: Optional[str]               # User-provided notes
    gathered_contexts: List[GatheredContext] # Gathered content
    context_valid: bool                     # Validation status
    retry_count: int                        # Retry counter
    
    # Vector processing (Milestone 2)
    context_chunks: List[str]               # Text chunks
    vector_store: Optional[FAISS]           # Vector store instance
    questions: List[Dict]                   # Generated questions
    answers: List[Dict]                     # User answers
    understanding_score: Optional[float]    # Score (0-1)
    passed_checkpoint: bool                 # Pass status
    
    # Feynman teaching (Milestone 3)
    weak_concepts: List[str]                # Concepts < 70%
    feynman_explanations: List[Dict]        # Explanations
    feynman_attempts: int                   # Attempt counter
    max_feynman_attempts: int               # Max attempts (3)
    
    # Workflow metadata
    current_stage: str                      # Current workflow stage
    messages: List[str]                     # Log messages
    error: Optional[str]                    # Error message
```

### 3. Learning Graph

**File:** `src/graph/learning_graph.py`

The `LearningGraph` class orchestrates the entire workflow using LangGraph's StateGraph:

#### **Workflow Nodes:**

1. **`define_checkpoint_node`** - Initialize current checkpoint
2. **`gather_context_node`** - Gather learning materials
3. **`validate_context_node`** - Validate context relevance
4. **`process_context_node`** - Create embeddings
5. **`generate_questions_node`** - Generate assessment questions
6. **`evaluate_answers_node`** - Score user answers
7. **`feynman_teaching_node`** - Generate simplified explanations
8. **`move_to_next_checkpoint_node`** - Advance to next checkpoint

#### **Conditional Edges:**

- **Context Valid?** - If no → retry gathering (max 3 times)
- **Score >= 70%?** - If yes → next checkpoint, if no → Feynman teaching
- **Feynman Attempts < 3?** - If yes → regenerate questions, if no → move on
- **More Checkpoints?** - If yes → next checkpoint, if no → complete

### 4. Context Manager

**File:** `src/modules/context_manager.py`

Handles gathering and validating learning content.

**Key Methods:**

```python
gather_context(checkpoint, user_notes, max_web_results=6)
    # Gathers context from user notes + web search
    # Returns: List[GatheredContext]

validate_context(checkpoint, contexts)
    # Validates context relevance with LLM scoring
    # Returns: (is_valid, message, scored_contexts)

chunk_context(contexts, chunk_size=1000)
    # Splits text into chunks for embedding
    # Returns: List[str]
```

**Features:**
- URL deduplication across retries
- Relevance scoring (0.0-1.0)
- Automatic text chunking
- Multi-source aggregation

### 5. Vector Store Manager

**File:** `src/modules/vector_store_manager.py`

Manages FAISS vector operations for semantic search.

**Key Methods:**

```python
create_vector_store(text_chunks: List[str]) -> FAISS
    # Creates FAISS vector store from chunks
    # Uses HuggingFace sentence-transformers

similarity_search(vector_store, query, k=3)
    # Performs similarity search
    # Returns: List[Document]

get_relevant_context(vector_store, objectives, k_per_objective=2)
    # Gets context for multiple objectives
    # Returns: Combined context string
```

**Technology:**
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **Vector Store:** FAISS (Facebook AI Similarity Search)
- **Device:** CPU (for compatibility)

### 6. Question Generator

**File:** `src/modules/question_generator.py`

Generates assessment questions using LLM.

**Key Methods:**

```python
generate_questions(checkpoint, context, num_questions=4)
    # Generates 3-5 questions based on objectives
    # Returns: List[Dict] with question structure
```

**Question Structure:**
```python
{
    'id': 1,
    'question': "What is the purpose of...?",
    'objective': "Understand function definition syntax",
    'difficulty': 'medium'
}
```

### 7. Understanding Verifier

**File:** `src/modules/understanding_verifier.py`

Evaluates learner answers and calculates scores.

**Key Methods:**

```python
evaluate_answers(questions, answers, context)
    # Scores all answers with LLM
    # Returns: (avg_score, passed, weak_concepts)
```

**Scoring Logic:**
- Individual question scoring (0.0-1.0)
- Average score calculation
- 70% passing threshold
- Weak concept identification

### 8. Feynman Teacher

**File:** `src/modules/feynman_teacher.py`

Implements Feynman Technique for adaptive teaching.

**Key Methods:**

```python
generate_explanations(questions, answers, context, weak_concepts)
    # Generates simplified explanations
    # Returns: List[Dict] with explanations
```

**Feynman Principles:**
1. **Simple Language** - Explain like teaching a 12-year-old
2. **Analogies** - Relatable comparisons
3. **Break Down** - Step-by-step explanations
4. **Examples** - Concrete code examples
5. **Common Mistakes** - Address misconceptions

### 9. PDF Generator

**File:** `src/utils/pdf_generator.py`

Generates professional PDF reports.

**Key Methods:**

```python
generate_report(session_data)
    # Creates comprehensive PDF
    # Returns: BytesIO buffer
```

**Report Sections:**
1. Title page with session summary
2. Executive summary with key metrics
3. Checkpoint details with scores
4. Performance analytics with charts
5. Feynman explanations (if used)
6. Personalized recommendations

### 10. Database Manager

**File:** `src/utils/database_manager.py`

Manages SQLite database for historical tracking.

**Key Methods:**

```python
save_session(session_data)
    # Saves complete session to database
    # Returns: session_id

get_session_history(limit=10)
    # Retrieves recent sessions
    # Returns: List[Dict]

get_performance_stats()
    # Calculates performance metrics
    # Returns: Dict with statistics
```

---

## 🔄 Workflow & State Management

### Complete Workflow Execution

```python
# 1. Initialize State
state = create_initial_state(
    checkpoints=[checkpoint1, checkpoint2],
    user_notes="My learning notes..."
)

# 2. Create Graph
graph = LearningGraph().build_graph()

# 3. Execute Workflow
result = graph.invoke(state)

# 4. Access Results
print(f"Score: {result['understanding_score']:.1%}")
print(f"Passed: {result['passed_checkpoint']}")
print(f"Completed: {len(result['completed_checkpoints'])}")
```

### State Transitions

| Stage | Next Stage (Success) | Next Stage (Failure) |
|-------|---------------------|---------------------|
| `initialized` | `checkpoint_defined` | `error` |
| `checkpoint_defined` | `context_gathered` | `error` |
| `context_gathered` | `context_validated` | `error` |
| `context_validated` | `context_processed` | `context_gathered` (retry) |
| `context_processed` | `questions_generated` | `error` |
| `questions_generated` | `understanding_verified` | `error` |
| `understanding_verified` | `next_checkpoint` | `feynman_teaching` |
| `feynman_teaching` | `feynman_completed` | `error` |
| `feynman_completed` | `questions_generated` | `next_checkpoint` (max attempts) |
| `next_checkpoint` | `checkpoint_defined` | `all_checkpoints_completed` |

---

## 📚 API Reference

### LearningGraph

```python
class LearningGraph:
    def __init__(self, force_poor_answers: bool = False)
    def build_graph(self) -> StateGraph
    def define_checkpoint_node(self, state: LearningState) -> LearningState
    def gather_context_node(self, state: LearningState) -> LearningState
    def validate_context_node(self, state: LearningState) -> LearningState
    def process_context_node(self, state: LearningState) -> LearningState
    def generate_questions_node(self, state: LearningState) -> LearningState
    def evaluate_answers_node(self, state: LearningState) -> LearningState
    def feynman_teaching_node(self, state: LearningState) -> LearningState
    def move_to_next_checkpoint_node(self, state: LearningState) -> LearningState
```

### Helper Functions

```python
# LLM Provider
get_llm(model_name=None, temperature=0.7, max_tokens=None, provider=None) -> ChatOpenAI
get_reasoning_llm() -> ChatOpenAI  # For complex reasoning
get_validation_llm() -> ChatOpenAI  # Fast model for validation

# Search Tools
search_for_learning_content(topic: str, objectives: List[str], max_results: int = 5) -> List[Dict]

# State Creation
create_initial_state(checkpoints: List[Checkpoint], user_notes: Optional[str] = None) -> LearningState
```

---

## 💾 Database Schema

**File:** `learning_sessions.db` (SQLite)

### Tables

#### 1. `sessions`

| Column | Type | Description |
|--------|------|-------------|
| `session_id` | INTEGER PRIMARY KEY | Auto-increment ID |
| `start_time` | TIMESTAMP | Session start |
| `end_time` | TIMESTAMP | Session end |
| `total_time_seconds` | INTEGER | Total duration |
| `overall_score` | REAL | Average score (0-1) |
| `checkpoints_count` | INTEGER | Total checkpoints |
| `passed_count` | INTEGER | Passed checkpoints |
| `feynman_used_count` | INTEGER | Feynman uses |
| `user_notes` | TEXT | Initial notes |
| `created_at` | TIMESTAMP | Record creation |

#### 2. `checkpoints`

| Column | Type | Description |
|--------|------|-------------|
| `checkpoint_id` | INTEGER PRIMARY KEY | Auto-increment ID |
| `session_id` | INTEGER FOREIGN KEY | Links to sessions |
| `checkpoint_index` | INTEGER | Order in session |
| `topic` | TEXT | Checkpoint topic |
| `subtopic` | TEXT | Subtopic (if any) |
| `score` | REAL | Score (0-1) |
| `passed` | BOOLEAN | Pass status |
| `feynman_used` | BOOLEAN | Feynman used flag |
| `attempt_count` | INTEGER | Number of attempts |
| `time_spent_seconds` | INTEGER | Time spent |
| `questions_count` | INTEGER | Number of questions |
| `created_at` | TIMESTAMP | Record creation |

#### 3. `questions`

| Column | Type | Description |
|--------|------|-------------|
| `question_id` | INTEGER PRIMARY KEY | Auto-increment ID |
| `checkpoint_id` | INTEGER FOREIGN KEY | Links to checkpoints |
| `question_text` | TEXT | Question content |
| `answer_text` | TEXT | User answer |
| `objective` | TEXT | Learning objective |
| `created_at` | TIMESTAMP | Record creation |

#### 4. `performance_metrics`

| Column | Type | Description |
|--------|------|-------------|
| `metric_id` | INTEGER PRIMARY KEY | Auto-increment ID |
| `session_id` | INTEGER FOREIGN KEY | Links to sessions |
| `metric_name` | TEXT | Metric name |
| `metric_value` | REAL | Numeric value |
| `metric_data` | TEXT | JSON data |
| `created_at` | TIMESTAMP | Record creation |

---

## ⚙ Configuration

### Environment Variables (`.env`)

```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional (for web search)
SERP_API_KEY=your_tavily_api_key

# Configuration
UNDERSTANDING_THRESHOLD=0.70    # 70% passing score
MAX_RETRIES=3                   # Max context retries
CHUNK_SIZE=1000                 # Text chunk size
CHUNK_OVERLAP=200               # Chunk overlap
```

### Model Configuration

```python
# Default Models
PRIMARY_LLM = "gemini-1.5-flash"         # Main LLM
REASONING_LLM = "gemini-1.5-pro"         # Complex reasoning
VALIDATION_LLM = "gemini-1.5-flash"      # Fast validation

# Embedding Model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

---

## 🎯 Development Milestones

### Milestone 1: Foundation ✅
- Basic checkpoint system
- Question generation
- Answer verification
- Simple workflow

### Milestone 2: Vector Storage ✅
- Web search integration
- FAISS vector embeddings
- Context validation
- Semantic search

### Milestone 3: Feynman Teaching ✅
- Adaptive teaching
- Simplified explanations
- Multi-attempt retry
- Weak concept identification

### Milestone 4: Multi-Checkpoint ✅
- Sequential progression
- State management
- Completion tracking
- Streamlit UI

### Phase 1-3: Enhancements ✅
- Auto-Feynman trigger
- PDF reports
- Auto-submit
- Historical tracking
- Analytics dashboard

---

## 📦 Dependencies

### Core Dependencies

```
streamlit>=1.28.0              # Web interface
langgraph>=0.2.0               # Workflow engine
langchain>=0.3.0               # LLM framework
langchain-google-genai         # Google Gemini
langchain-huggingface>=0.0.1   # HuggingFace integration
```

### ML/AI Libraries

```
faiss-cpu>=1.7.4               # Vector similarity
sentence-transformers>=2.2.0   # Text embeddings
tiktoken>=0.5.0                # Token counting
```

### Web & Search

```
tavily-python                  # Web search (optional)
duckduckgo-search>=6.0.0       # Alternative search
google-search-results>=2.4.2   # Google search (optional)
```

### Reports & Analytics

```
reportlab>=4.0.0               # PDF generation
pillow>=10.0.0                 # Image processing
plotly>=5.17.0                 # Interactive charts
pandas>=2.1.0                  # Data analysis
sqlalchemy>=2.0.0              # Database ORM
```

### Utilities

```
python-dotenv>=1.0.0           # Environment variables
python-dateutil>=2.8.2         # Date utilities
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repository-url>
cd Tutor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Create .env file
cp .env.example .env

# Add your OpenAI API key
OPENAI_API_KEY=your_key_here
```

### 3. Run Application

```bash
# Web interface (recommended)
streamlit run app.py

# CLI demo
python main.py
```

---

## 📖 Usage Examples

### Example 1: Creating Checkpoints

```python
from src.models.checkpoint import Checkpoint

checkpoint = Checkpoint(
    topic="Python Functions",
    objectives=[
        "Understand function syntax",
        "Learn about parameters",
        "Master return values"
    ],
    difficulty_level="beginner",
    estimated_time_minutes=20
)
```

### Example 2: Running Workflow

```python
from src.models.state import create_initial_state
from src.graph.learning_graph import LearningGraph

# Create checkpoints
checkpoints = [checkpoint1, checkpoint2]

# Initialize state
state = create_initial_state(
    checkpoints=checkpoints,
    user_notes="Functions are defined with 'def'..."
)

# Create and run graph
graph = LearningGraph().build_graph()
result = graph.invoke(state)

# Check results
print(f"Score: {result['understanding_score']:.1%}")
```

### Example 3: Generating PDF Report

```python
from src.utils.pdf_generator import LearningReportGenerator

generator = LearningReportGenerator()
pdf_buffer = generator.generate_report(session_data)

# Save to file
with open("report.pdf", "wb") as f:
    f.write(pdf_buffer.getvalue())
```

---

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure `GOOGLE_API_KEY` is set in `.env`
   - Get key from: https://makersuite.google.com/app/apikey

2. **Import Errors**
   - Reinstall dependencies: `pip install -r requirements.txt --upgrade`
   - Check Python version: `python --version` (requires 3.8+)

3. **Vector Store Errors**
   - Install FAISS: `pip install faiss-cpu`
   - Check embeddings model download

4. **Streamlit Issues**
   - Clear cache: `streamlit cache clear`
   - Update Streamlit: `pip install streamlit --upgrade`

---

## 📝 License

MIT License - See `LICENSE` file for details.

---

## 👤 Author

**Saket Kumar**  
Project: Autonomous Learning Agent  
Date: January 2026

---

**End of Technical Documentation**
