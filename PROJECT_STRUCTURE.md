# 📂 Project Structure Guide

**Autonomous Learning Agent - Complete Directory Structure**

---

## 📋 Table of Contents

1. [Directory Tree](#-directory-tree)
2. [File-by-File Breakdown](#-file-by-file-breakdown)
3. [Module Dependencies](#-module-dependencies)
4. [Data Flow Diagram](#-data-flow-diagram)
5. [Code Organization](#-code-organization)

---

## 🌳 Directory Tree

```
Tutor/
│
├── 📄 app.py                                    [986 lines] - Streamlit Web Interface
├── 📄 main.py                                   [218 lines] - CLI Demo Script
├── 📄 requirements.txt                          [24 lines]  - Python Dependencies
├── 📄 README.md                                 [860 lines] - User Documentation
├── 📄 DOCUMENTATION.md                          [NEW]       - Technical Documentation
├── 📄 PROJECT_STRUCTURE.md                      [NEW]       - This File
├── 📄 LICENSE                                               - MIT License
├── 📄 .env.example                                          - Environment Template
├── 📄 .env                                                  - API Keys (DO NOT COMMIT)
├── 📄 .gitignore                                            - Git Ignore Rules
│
├── 📁 src/                                                  - Source Code (Main Application)
│   │
│   ├── 📄 __init__.py                                       - Package Initializer
│   │
│   ├── 📁 models/                                           - Data Models & State
│   │   ├── 📄 __init__.py
│   │   ├── 📄 checkpoint.py                    [48 lines]  - Checkpoint & Context Models
│   │   │   │
│   │   │   ├── class Checkpoint                            - Learning checkpoint definition
│   │   │   │   ├── topic: str
│   │   │   │   ├── objectives: List[str]
│   │   │   │   ├── difficulty_level: str
│   │   │   │   └── estimated_time_minutes: int
│   │   │   │
│   │   │   └── class GatheredContext                       - Gathered learning content
│   │   │       ├── source: str
│   │   │       ├── content: str
│   │   │       ├── gathered_at: datetime
│   │   │       └── relevance_score: float
│   │   │
│   │   └── 📄 state.py                         [133 lines] - LangGraph State Definition
│   │       │
│   │       ├── class LearningState(TypedDict)              - Workflow state container
│   │       │   ├── all_checkpoints: List[Checkpoint]
│   │       │   ├── current_checkpoint_index: int
│   │       │   ├── checkpoint: Optional[Checkpoint]
│   │       │   ├── completed_checkpoints: List[int]
│   │       │   ├── user_notes: Optional[str]
│   │       │   ├── gathered_contexts: List[GatheredContext]
│   │       │   ├── context_valid: bool
│   │       │   ├── context_chunks: List[str]
│   │       │   ├── vector_store: Optional[FAISS]
│   │       │   ├── questions: List[Dict]
│   │       │   ├── answers: List[Dict]
│   │       │   ├── understanding_score: Optional[float]
│   │       │   ├── passed_checkpoint: bool
│   │       │   ├── weak_concepts: List[str]
│   │       │   ├── feynman_explanations: List[Dict]
│   │       │   ├── feynman_attempts: int
│   │       │   ├── current_stage: str
│   │       │   ├── messages: List[str]
│   │       │   └── error: Optional[str]
│   │       │
│   │       └── def create_initial_state()                  - State factory function
│   │
│   ├── 📁 graph/                                            - LangGraph Workflow
│   │   ├── 📄 __init__.py
│   │   └── 📄 learning_graph.py                [756 lines] - Workflow Orchestration
│   │       │
│   │       ├── class LearningGraph                         - Main workflow engine
│   │       │   │
│   │       │   ├── __init__()                              - Initialize components
│   │       │   │   ├── ContextManager
│   │       │   │   ├── VectorStoreManager
│   │       │   │   ├── QuestionGenerator
│   │       │   │   ├── UnderstandingVerifier
│   │       │   │   └── FeynmanTeacher
│   │       │   │
│   │       │   ├── build_graph()                           - Build StateGraph
│   │       │   │
│   │       │   ├── Workflow Nodes:
│   │       │   │   ├── define_checkpoint_node()            - Initialize checkpoint
│   │       │   │   ├── gather_context_node()               - Gather learning content
│   │       │   │   ├── validate_context_node()             - Validate relevance
│   │       │   │   ├── process_context_node()              - Create embeddings
│   │       │   │   ├── generate_questions_node()           - Generate questions
│   │       │   │   ├── evaluate_answers_node()             - Score answers
│   │       │   │   ├── feynman_teaching_node()             - Generate explanations
│   │       │   │   └── move_to_next_checkpoint_node()      - Advance checkpoint
│   │       │   │
│   │       │   └── Conditional Logic:
│   │       │       ├── should_retry_context()              - Context retry logic
│   │       │       ├── should_apply_feynman()              - Feynman trigger (< 70%)
│   │       │       ├── should_regenerate_questions()       - Question regen logic
│   │       │       └── has_more_checkpoints()              - Next checkpoint check
│   │       │
│   │       └── def create_learning_graph()                 - Factory function
│   │
│   ├── 📁 modules/                                          - Core Business Logic
│   │   ├── 📄 __init__.py
│   │   │
│   │   ├── 📄 context_manager.py               [336 lines] - Context Gathering & Validation
│   │   │   │
│   │   │   └── class ContextManager
│   │   │       ├── __init__()                              - Initialize LLMs & text splitter
│   │   │       ├── gather_context()                        - Gather from notes + web
│   │   │       │   ├── Process user notes
│   │   │       │   └── Web search with deduplication
│   │   │       ├── validate_context()                      - LLM-based validation
│   │   │       │   ├── Score relevance (0-1)
│   │   │       │   └── Return is_valid, message
│   │   │       ├── chunk_context()                         - Split into chunks
│   │   │       └── _calculate_relevance_score()            - LLM scoring
│   │   │
│   │   ├── 📄 vector_store_manager.py          [106 lines] - FAISS Vector Operations
│   │   │   │
│   │   │   └── class VectorStoreManager
│   │   │       ├── __init__()                              - Initialize embeddings
│   │   │       │   └── HuggingFace: all-MiniLM-L6-v2
│   │   │       ├── create_vector_store()                   - Create FAISS from chunks
│   │   │       ├── similarity_search()                     - Semantic search
│   │   │       └── get_relevant_context()                  - Multi-objective context
│   │   │
│   │   ├── 📄 question_generator.py            [179 lines] - LLM Question Generation
│   │   │   │
│   │   │   └── class QuestionGenerator
│   │   │       ├── __init__()                              - Initialize LLM
│   │   │       ├── generate_questions()                    - Generate 3-5 questions
│   │   │       │   ├── LLM prompt with objectives
│   │   │       │   └── Parse structured response
│   │   │       ├── _parse_questions()                      - Extract from LLM output
│   │   │       └── _get_default_questions()                - Fallback questions
│   │   │
│   │   ├── 📄 understanding_verifier.py        [222 lines] - Answer Evaluation & Scoring
│   │   │   │
│   │   │   └── class UnderstandingVerifier
│   │   │       ├── __init__()                              - Initialize LLM & threshold
│   │   │       ├── evaluate_answers()                      - Score all answers
│   │   │       │   ├── Score each answer (0-1)
│   │   │       │   ├── Calculate average
│   │   │       │   ├── Check 70% threshold
│   │   │       │   └── Identify weak concepts
│   │   │       ├── _score_answer()                         - LLM-based scoring
│   │   │       └── _parse_score()                          - Extract score from LLM
│   │   │
│   │   └── 📄 feynman_teacher.py               [240 lines] - Adaptive Feynman Teaching
│   │       │
│   │       └── class FeynmanTeacher
│   │           ├── __init__()                              - Initialize LLM
│   │           ├── generate_explanations()                 - Generate for weak concepts
│   │           │   ├── Identify unique weak concepts
│   │           │   ├── Get related Q&A
│   │           │   └── Generate simplified explanation
│   │           ├── _get_related_qa()                       - Find related questions
│   │           └── _generate_simplified_explanation()      - Feynman prompt
│   │               ├── Simple language
│   │               ├── Analogies
│   │               ├── Step-by-step breakdown
│   │               └── Code examples
│   │
│   └── 📁 utils/                                            - Utility Functions
│       ├── 📄 __init__.py
│       │
│       ├── 📄 llm_provider.py                  [255 lines] - LLM Initialization
│       │   │
│       │   ├── def get_llm()                               - Get primary LLM
│       │   │   ├── Support for Google Gemini
│       │   │   ├── Support for OpenAI
│       │   │   └── Environment-based config
│       │   ├── def get_reasoning_llm()                     - Get powerful LLM
│       │   └── def get_validation_llm()                    - Get fast LLM
│       │
│       ├── 📄 search_tools.py                  [152 lines] - Web Search Integration
│       │   │
│       │   └── def search_for_learning_content()           - Multi-provider search
│       │       ├── Tavily Search (preferred)
│       │       ├── DuckDuckGo Search (fallback)
│       │       └── Google Search (optional)
│       │
│       ├── 📄 pdf_generator.py                 [369 lines] - PDF Report Generation
│       │   │
│       │   └── class LearningReportGenerator
│       │       ├── __init__()                              - Setup ReportLab styles
│       │       ├── generate_report()                       - Main report generator
│       │       │   ├── Title page
│       │       │   ├── Executive summary
│       │       │   ├── Checkpoint details
│       │       │   ├── Performance analytics
│       │       │   ├── Feynman explanations
│       │       │   └── Recommendations
│       │       ├── _build_title_page()
│       │       ├── _build_summary()
│       │       ├── _build_checkpoint_details()
│       │       ├── _build_analytics()
│       │       ├── _build_feynman_section()
│       │       └── _build_recommendations()
│       │
│       └── 📄 database_manager.py              [296 lines] - SQLite Operations
│           │
│           └── class SessionDatabase
│               ├── __init__()                              - Initialize DB connection
│               ├── _init_database()                        - Create tables
│               │   ├── sessions table
│               │   ├── checkpoints table
│               │   ├── questions table
│               │   └── performance_metrics table
│               ├── save_session()                          - Save complete session
│               ├── get_session_history()                   - Retrieve sessions
│               ├── get_performance_stats()                 - Calculate stats
│               └── delete_session()                        - Delete session
│
├── 📁 notebooks/                                            - Development Artifacts (Optional)
│   ├── 📄 Milestone2.ipynb                                  - Milestone 2 testing
│   ├── 📄 Milestone3.ipynb                                  - Milestone 3 testing
│   ├── 📄 Milestone3_Presentation.ipynb                     - Presentation notebook
│   ├── 📄 Complete_Testing_Tutorial.ipynb                   - Testing guide
│   ├── 📄 interactive_analysis.ipynb                        - Interactive testing
│   └── 📄 ter_agent_autonomous_test_checkpoint.ipynb        - Early checkpoint tests
│
├── 📁 tests/                                                - Unit Tests (Placeholder)
│   └── 📄 __init__.py
│
├── 📁 venv/                                                 - Virtual Environment (Generated)
│   ├── Scripts/                                             - Windows executables
│   ├── Lib/                                                 - Python packages
│   └── ...
│
└── 📄 learning_sessions.db                                  - SQLite Database (Generated)
```

---

## 📄 File-by-File Breakdown

### Root Level Files

#### `app.py` (986 lines) - Streamlit Web Application

**Purpose:** Complete web interface for the learning agent

**Key Components:**
```python
# Session State Management
def init_session_state()                    # Initialize all session variables

# Page Functions
def setup_page()                            # Setup checkpoints & notes
def learning_page()                         # Display learning progress
def questions_page()                        # Question answering interface
def results_page()                          # Show scores & feedback
def feynman_page()                          # Feynman explanations display
def complete_page()                         # Session completion & PDF download

# Helper Functions
def run_learning_workflow()                 # Execute LangGraph workflow
def generate_pdf_report()                   # Create PDF report
def save_to_database()                      # Save session to DB

# UI Components
- Sidebar with navigation
- Progress tracking
- Real-time analytics dashboard
- PDF download button
- Historical performance charts
```

**Features:**
- ✅ Multi-page navigation
- ✅ Real-time progress tracking
- ✅ Interactive Q&A interface
- ✅ Auto-submit functionality
- ✅ Auto-Feynman trigger
- ✅ PDF report generation
- ✅ Historical analytics
- ✅ Plotly charts

---

#### `main.py` (218 lines) - CLI Demo Script

**Purpose:** Command-line demonstration script

**Structure:**
```python
def main():
    # 1. Create checkpoints
    checkpoints = [checkpoint1, checkpoint2]
    
    # 2. Provide user notes
    user_notes = "..."
    
    # 3. Initialize state
    state = create_initial_state(checkpoints, user_notes)
    
    # 4. Create graph
    graph = create_learning_graph()
    
    # 5. Execute workflow
    result = graph.invoke(state)
    
    # 6. Display results
    print_results(result)
```

**Use Cases:**
- Testing workflow without UI
- Debugging graph execution
- Automated testing
- Demo presentations

---

#### `requirements.txt` (24 lines) - Dependencies

**Categories:**

1. **Core Framework:**
   - streamlit>=1.28.0
   - langgraph>=0.2.0
   - langchain>=0.3.0

2. **LLM Integration:**
   - langchain-openai>=0.2.0
   - langchain-google-genai
   - langchain-groq>=0.2.0

3. **ML/AI:**
   - faiss-cpu>=1.7.4
   - sentence-transformers>=2.2.0
   - langchain-huggingface>=0.0.1

4. **Search:**
   - tavily-python
   - duckduckgo-search>=6.0.0
   - google-search-results>=2.4.2

5. **Reports & Analytics:**
   - reportlab>=4.0.0
   - plotly>=5.17.0
   - pandas>=2.1.0
   - sqlalchemy>=2.0.0

6. **Utilities:**
   - python-dotenv>=1.0.0
   - tiktoken>=0.5.0

---

### Source Code (`src/`)

#### Models Directory (`src/models/`)

##### `checkpoint.py` (48 lines)

**Classes:**

```python
@dataclass
class Checkpoint:
    """Learning checkpoint definition"""
    topic: str                          # Main topic
    objectives: List[str]               # Learning objectives
    difficulty_level: str               # beginner/intermediate/advanced
    estimated_time_minutes: int         # Time estimate
    prerequisites: List[str]            # Prerequisites
    created_at: datetime                # Creation time

@dataclass
class GatheredContext:
    """Context gathered from various sources"""
    source: str                         # user_notes/web_search/etc
    content: str                        # Actual content
    gathered_at: datetime               # Gathering time
    metadata: Dict[str, Any]            # Additional info
    relevance_score: Optional[float]    # 0-1 relevance score
```

---

##### `state.py` (133 lines)

**Classes & Functions:**

```python
class LearningState(TypedDict):
    """Complete workflow state - 25+ fields"""
    # See DOCUMENTATION.md for full structure

def create_initial_state(checkpoints, user_notes) -> LearningState:
    """Factory function to create initial state"""
    # Returns fully initialized LearningState
```

---

#### Graph Directory (`src/graph/`)

##### `learning_graph.py` (756 lines)

**Main Class:**

```python
class LearningGraph:
    """Orchestrates the complete learning workflow"""
    
    # Initialization
    __init__(force_poor_answers=False)
    build_graph() -> StateGraph
    
    # Workflow Nodes (8 nodes)
    define_checkpoint_node(state) -> LearningState
    gather_context_node(state) -> LearningState
    validate_context_node(state) -> LearningState
    process_context_node(state) -> LearningState
    generate_questions_node(state) -> LearningState
    evaluate_answers_node(state) -> LearningState
    feynman_teaching_node(state) -> LearningState
    move_to_next_checkpoint_node(state) -> LearningState
    
    # Conditional Logic (4 functions)
    should_retry_context(state) -> str
    should_apply_feynman(state) -> str
    should_regenerate_questions(state) -> str
    has_more_checkpoints(state) -> str
```

**Graph Structure:**

```
START → define_checkpoint
        ↓
    gather_context
        ↓
    validate_context ←──┐ (retry if invalid)
        ↓               │
    process_context     │
        ↓               │
    generate_questions  │
        ↓               │
    [WAIT FOR ANSWERS]  │
        ↓               │
    evaluate_answers    │
        ↓               │
    [score >= 70%?]     │
        ↓         ↓     │
       YES       NO     │
        ↓         ↓     │
    next_checkpoint     │
        ↓        feynman_teaching
        ↓         ↓     │
    [more checkpoints?] │
        ↓         ↓     │
       YES   regenerate_questions
        ↓         ↓
    define_checkpoint
        ↓
       END
```

---

#### Modules Directory (`src/modules/`)

##### `context_manager.py` (336 lines)

**Responsibilities:**
1. Gather context from multiple sources
2. Validate context relevance
3. Chunk text for embedding
4. Deduplicate URLs across retries

**Key Methods:**

```python
gather_context(checkpoint, user_notes, max_web_results=6)
    # 1. Process user notes (if provided)
    # 2. Search web with Tavily/DuckDuckGo
    # 3. Deduplicate by URL
    # Returns: List[GatheredContext]

validate_context(checkpoint, contexts)
    # 1. Score each context with LLM (0-1)
    # 2. Check average score >= 0.6
    # 3. Return (is_valid, message, scored_contexts)

chunk_context(contexts, chunk_size=1000)
    # 1. Combine all contexts
    # 2. Split with RecursiveCharacterTextSplitter
    # Returns: List[str] chunks
```

---

##### `vector_store_manager.py` (106 lines)

**Responsibilities:**
1. Create FAISS vector stores
2. Perform similarity search
3. Retrieve relevant context

**Key Methods:**

```python
create_vector_store(text_chunks)
    # 1. Create Document objects
    # 2. Generate embeddings
    # 3. Build FAISS index
    # Returns: FAISS vector store

similarity_search(vector_store, query, k=3)
    # 1. Query vector store
    # 2. Return top-k results
    # Returns: List[Document]

get_relevant_context(vector_store, objectives, k_per_objective=2)
    # 1. Search for each objective
    # 2. Deduplicate results
    # 3. Combine into string
    # Returns: str (combined context)
```

---

##### `question_generator.py` (179 lines)

**Responsibilities:**
1. Generate 3-5 assessment questions
2. Align with learning objectives
3. Parse LLM responses

**Key Methods:**

```python
generate_questions(checkpoint, context, num_questions=4)
    # 1. Create LLM prompt with objectives + context
    # 2. Generate questions with LLM
    # 3. Parse into structured format
    # Returns: List[Dict] with questions

_parse_questions(response, checkpoint)
    # Extract questions from LLM response
    # Returns: List[Dict]

_get_default_questions(checkpoint)
    # Fallback questions if LLM fails
    # Returns: List[Dict]
```

**Question Structure:**
```python
{
    'id': 1,
    'question': "What is the purpose of...?",
    'objective': "Understand XYZ",
    'difficulty': 'medium'
}
```

---

##### `understanding_verifier.py` (222 lines)

**Responsibilities:**
1. Score individual answers
2. Calculate average score
3. Apply 70% threshold
4. Identify weak concepts

**Key Methods:**

```python
evaluate_answers(questions, answers, context)
    # 1. Score each answer with LLM
    # 2. Calculate average
    # 3. Check >= 70% threshold
    # 4. Identify weak concepts (< 70%)
    # Returns: (avg_score, passed, weak_concepts)

_score_answer(question, answer, context)
    # 1. Create scoring prompt
    # 2. Get LLM score (0-100)
    # 3. Normalize to 0-1
    # Returns: float (0-1)
```

---

##### `feynman_teacher.py` (240 lines)

**Responsibilities:**
1. Generate simplified explanations
2. Use Feynman Technique principles
3. Create analogies and examples

**Key Methods:**

```python
generate_explanations(questions, answers, context, weak_concepts)
    # 1. Get unique weak concepts
    # 2. Find related Q&A pairs
    # 3. Generate simplified explanation for each
    # Returns: List[Dict] with explanations

_generate_simplified_explanation(concept, related_qa, context)
    # 1. Create Feynman-style prompt
    # 2. Generate explanation with LLM
    # 3. Include analogies + examples
    # Returns: str (explanation)
```

**Feynman Principles:**
- Simple language (12-year-old level)
- Analogies and metaphors
- Step-by-step breakdowns
- Concrete examples
- Address common mistakes

---

#### Utils Directory (`src/utils/`)

##### `llm_provider.py` (255 lines)

**Functions:**

```python
get_llm(model_name=None, temperature=0.7, max_tokens=None, provider=None)
    # Primary LLM for most tasks
    # Default: gemini-1.5-flash
    # Returns: ChatOpenAI instance

get_reasoning_llm()
    # Powerful LLM for complex reasoning
    # Default: gemini-1.5-pro
    # Returns: ChatOpenAI instance

get_validation_llm()
    # Fast LLM for validation tasks
    # Default: gemini-1.5-flash
    # Returns: ChatOpenAI instance
```

**Supported Providers:**
- Google Gemini (via langchain-google-genai)
- OpenAI (via langchain-openai)
- Azure OpenAI (via langchain-openai)
- Groq (optional)

---

##### `search_tools.py` (152 lines)

**Functions:**

```python
search_for_learning_content(topic, objectives, max_results=5)
    # 1. Try Tavily Search (preferred)
    # 2. Fallback to DuckDuckGo
    # 3. Optional: Google Search
    # Returns: List[Dict] with search results
```

**Result Structure:**
```python
{
    'url': "https://...",
    'title': "...",
    'snippet': "...",
    'content': "..."
}
```

---

##### `pdf_generator.py` (369 lines)

**Class:**

```python
class LearningReportGenerator:
    """Generate professional PDF reports"""
    
    generate_report(session_data)
        # Creates multi-page PDF with:
        # - Title page
        # - Executive summary
        # - Checkpoint details with scores
        # - Performance analytics
        # - Feynman explanations (if used)
        # - Personalized recommendations
        # Returns: BytesIO buffer
```

**Report Sections:**
1. **Title Page:** Session info, date, overall score
2. **Summary:** Key metrics, pass/fail status
3. **Checkpoints:** Detailed breakdown per checkpoint
4. **Analytics:** Charts and visualizations
5. **Feynman:** Explanations (if applicable)
6. **Recommendations:** Next steps based on performance

---

##### `database_manager.py` (296 lines)

**Class:**

```python
class SessionDatabase:
    """Manage SQLite database for history"""
    
    _init_database()
        # Create 4 tables:
        # - sessions
        # - checkpoints
        # - questions
        # - performance_metrics
    
    save_session(session_data)
        # Save complete session with all data
        # Returns: session_id
    
    get_session_history(limit=10)
        # Retrieve recent sessions
        # Returns: List[Dict]
    
    get_performance_stats()
        # Calculate statistics:
        # - Total sessions
        # - Average score
        # - Pass rate
        # - Total time
        # Returns: Dict
```

---

## 🔗 Module Dependencies

### Dependency Graph

```
app.py / main.py
    │
    ├──> src.models.checkpoint
    │    └── Checkpoint, GatheredContext
    │
    ├──> src.models.state
    │    └── LearningState, create_initial_state()
    │
    └──> src.graph.learning_graph
         └── LearningGraph
              │
              ├──> src.modules.context_manager
              │    └── ContextManager
              │         └──> src.utils.llm_provider
              │         └──> src.utils.search_tools
              │
              ├──> src.modules.vector_store_manager
              │    └── VectorStoreManager
              │         └──> HuggingFace Embeddings
              │
              ├──> src.modules.question_generator
              │    └── QuestionGenerator
              │         └──> src.utils.llm_provider
              │
              ├──> src.modules.understanding_verifier
              │    └── UnderstandingVerifier
              │         └──> src.utils.llm_provider
              │
              └──> src.modules.feynman_teacher
                   └── FeynmanTeacher
                        └──> src.utils.llm_provider

app.py only:
    ├──> src.utils.pdf_generator
    │    └── LearningReportGenerator
    │
    └──> src.utils.database_manager
         └── SessionDatabase
```

### Import Chain

```python
# Level 1: Models (no dependencies)
src.models.checkpoint
src.models.state

# Level 2: Utils (depend on external libs only)
src.utils.llm_provider
src.utils.search_tools

# Level 3: Modules (depend on utils + models)
src.modules.context_manager
src.modules.vector_store_manager
src.modules.question_generator
src.modules.understanding_verifier
src.modules.feynman_teacher

# Level 4: Graph (depends on everything)
src.graph.learning_graph

# Level 5: Applications (depend on graph)
app.py
main.py

# Level 5: Additional Utils (standalone)
src.utils.pdf_generator
src.utils.database_manager
```

---

## 📊 Data Flow Diagram

### Complete Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                    USER INPUT                            │
│  ┌──────────────────┐     ┌──────────────────────┐     │
│  │  Checkpoints     │     │   User Notes         │     │
│  │  (Topic +        │     │   (Learning          │     │
│  │   Objectives)    │     │    Materials)        │     │
│  └────────┬─────────┘     └─────────┬────────────┘     │
└───────────┼────────────────────────┼──────────────────┘
            │                        │
            └────────────┬───────────┘
                         │
            ┌────────────▼────────────┐
            │  create_initial_state() │
            │  (LearningState)        │
            └────────────┬────────────┘
                         │
┌────────────────────────▼───────────────────────────────┐
│              LANGGRAPH WORKFLOW                         │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 1. Define Checkpoint                            │   │
│  │    Input:  all_checkpoints, current_index       │   │
│  │    Output: checkpoint                           │   │
│  └────────────┬────────────────────────────────────┘   │
│               │                                         │
│  ┌────────────▼────────────────────────────────────┐   │
│  │ 2. Gather Context                               │   │
│  │    Input:  checkpoint, user_notes               │   │
│  │    Process: Web search + text extraction        │   │
│  │    Output: gathered_contexts []                 │   │
│  └────────────┬────────────────────────────────────┘   │
│               │                                         │
│  ┌────────────▼────────────────────────────────────┐   │
│  │ 3. Validate Context                             │   │
│  │    Input:  gathered_contexts                    │   │
│  │    Process: LLM relevance scoring               │   │
│  │    Output: context_valid, scored_contexts       │   │
│  └────────────┬────────────────────────────────────┘   │
│               │                                         │
│  ┌────────────▼────────────────────────────────────┐   │
│  │ 4. Process Context                              │   │
│  │    Input:  gathered_contexts                    │   │
│  │    Process: Chunking + FAISS embeddings         │   │
│  │    Output: context_chunks, vector_store         │   │
│  └────────────┬────────────────────────────────────┘   │
│               │                                         │
│  ┌────────────▼────────────────────────────────────┐   │
│  │ 5. Generate Questions                           │   │
│  │    Input:  checkpoint, vector_store             │   │
│  │    Process: LLM question generation             │   │
│  │    Output: questions []                         │   │
│  └────────────┬────────────────────────────────────┘   │
│               │                                         │
│               ▼                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │        [WAIT FOR USER ANSWERS]                 │    │
│  │     (Streamlit UI / CLI input)                 │    │
│  └────────────┬──────────────────────────────────┘    │
│               │                                         │
│  ┌────────────▼────────────────────────────────────┐   │
│  │ 6. Evaluate Answers                             │   │
│  │    Input:  questions, answers, vector_store     │   │
│  │    Process: LLM answer scoring                  │   │
│  │    Output: understanding_score, passed,         │   │
│  │            weak_concepts                        │   │
│  └────────────┬────────────────────────────────────┘   │
│               │                                         │
│          [Score >= 70%?]                                │
│               │                                         │
│        ┌──────┴──────┐                                 │
│       YES            NO                                 │
│        │              │                                 │
│        │    ┌─────────▼──────────────────────────┐    │
│        │    │ 7. Feynman Teaching                 │    │
│        │    │    Input:  weak_concepts, Q&A       │    │
│        │    │    Process: Generate explanations   │    │
│        │    │    Output: feynman_explanations     │    │
│        │    └─────────┬──────────────────────────┘    │
│        │              │                                 │
│        │         [Attempts < 3?]                       │
│        │              │                                 │
│        │             YES                                │
│        │              │                                 │
│        │              └──► Regenerate Questions        │
│        │                                                │
│        │                                                │
│  ┌─────▼─────────────────────────────────────────┐    │
│  │ 8. Move to Next Checkpoint                     │    │
│  │    Input:  current_checkpoint_index            │    │
│  │    Process: Increment index                    │    │
│  │    Output: completed_checkpoints []            │    │
│  └────────────┬───────────────────────────────────┘    │
│               │                                         │
│       [More Checkpoints?]                              │
│               │                                         │
│        ┌──────┴──────┐                                 │
│       YES            NO                                 │
│        │              │                                 │
│        └──► Define    │                                 │
│          Checkpoint   │                                 │
│                       ▼                                 │
│                    ┌──────────────────┐                │
│                    │    COMPLETE      │                │
│                    └────────┬─────────┘                │
└─────────────────────────────┼──────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────┐
│                    FINAL OUTPUT                         │
│  ┌──────────────────┐  ┌──────────────────────┐       │
│  │  LearningState   │  │  Session Data        │       │
│  │  (Complete)      │  │  (For Reporting)     │       │
│  └────────┬─────────┘  └─────────┬────────────┘       │
└───────────┼─────────────────────┼────────────────────┘
            │                     │
            ├──────────┬──────────┤
            │          │          │
       ┌────▼──┐  ┌───▼────┐  ┌──▼─────┐
       │  UI   │  │  PDF   │  │Database│
       │Display│  │ Report │  │ Save   │
       └───────┘  └────────┘  └────────┘
```

---

## 🗂 Code Organization

### Design Patterns Used

1. **Factory Pattern**
   - `create_initial_state()` - Creates LearningState
   - `create_learning_graph()` - Creates LearningGraph
   - `get_llm()` - Creates LLM instances

2. **Builder Pattern**
   - `LearningGraph.build_graph()` - Builds StateGraph
   - `LearningReportGenerator` - Builds PDF report

3. **Strategy Pattern**
   - `search_tools.py` - Multiple search strategies (Tavily/DuckDuckGo/Google)
   - `llm_provider.py` - Multiple LLM providers (Google/OpenAI/Groq)

4. **State Pattern**
   - `LearningState` - Maintains workflow state
   - State transitions managed by LangGraph

5. **Singleton Pattern**
   - Database connection in `SessionDatabase`
   - Vector store manager instances

### Code Style & Conventions

1. **Naming Conventions:**
   - Classes: `PascalCase` (e.g., `ContextManager`)
   - Functions: `snake_case` (e.g., `gather_context()`)
   - Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
   - Private methods: `_leading_underscore` (e.g., `_score_answer()`)

2. **Documentation:**
   - All classes have docstrings
   - All public methods have docstrings
   - Type hints on function signatures
   - Inline comments for complex logic

3. **Error Handling:**
   - Try-except blocks in all nodes
   - Error state in LearningState
   - Graceful degradation (fallback questions, default values)

---

## 📝 Summary

This project is organized into clear, modular components:

- **Models** define data structures
- **Graph** orchestrates the workflow
- **Modules** implement business logic
- **Utils** provide supporting functions
- **Applications** (app.py/main.py) provide user interfaces

Each component has a single responsibility and clear interfaces, making the codebase maintainable and extensible.

---

**End of Project Structure Guide**
