# 🎓 Autonomous Learning Agent

**An advanced AI-powered educational platform with adaptive teaching, multi-checkpoint learning, and intelligent assessment**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/langgraph-0.2+-green.svg)](https://langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **📚 For detailed technical documentation, see [DOCUMENTATION.md](DOCUMENTATION.md)**  
> **📂 For project structure details, see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**

---

## 🌟 Overview

The **Autonomous Learning Agent** is a cutting-edge agentic platform that revolutionizes personalized education through intelligent workflow orchestration, adaptive teaching, and comprehensive analytics.

### Core Capabilities

- **🤖 Agentic Architecture**: LangGraph-powered autonomous workflow with 8 specialized nodes
- **🎯 Adaptive Learning**: Automatic Feynman teaching triggered when score < 70%
- **🔍 Smart Context**: FAISS vector embeddings + semantic search for relevant content
- **📊 Real-Time Analytics**: Performance tracking with interactive Plotly visualizations
- **📄 Professional Reports**: Comprehensive PDF summaries with personalized recommendations
- **🔄 Intelligent Automation**: Auto-submit, auto-retry, and smart question regeneration
- **🏛️ Historical Tracking**: SQLite database with session history and trend analysis

### Technology Stack

- **Backend:** Python 3.8+, LangGraph 0.2+, LangChain 0.3+
- **LLM:** Google Gemini (gemini-1.5-flash/pro)
- **Vector Store:** FAISS with HuggingFace embeddings (all-MiniLM-L6-v2)
- **Web Search:** Tavily API (with DuckDuckGo fallback)
- **Interface:** Streamlit 1.28+ (986-line web app)
- **Database:** SQLite with SQLAlchemy ORM
- **Analytics:** Plotly 5.17+ & Pandas 2.1+

---

## 📖 Table of Contents

- [Features](#-key-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [API Examples](#-api-examples)
- [Troubleshooting](#-troubleshooting)
- [Documentation](#-documentation)
- [Contributing](#-contributing)

---

## ✨ Key Features

### Core Functionality (Milestones 1-4)
- ✅ **Multi-Checkpoint Learning** - Sequential topic progression (2-5+ checkpoints per session)
- ✅ **Intelligent Question Generation** - Context-aware assessment (3-5 questions per checkpoint)
- ✅ **Adaptive Evaluation** - LLM-powered answer scoring with 70% pass threshold
- ✅ **Feynman Teaching** - Automatic simplified explanations for weak concepts
- ✅ **Web Search Integration** - Dynamic content gathering via Tavily API
- ✅ **Vector Storage** - FAISS-based semantic search (384-dim embeddings)
- ✅ **Context Validation** - Relevance scoring with automatic retry (max 3 attempts)

### Advanced Features (Enhancements Phase 1-3)
- 🚀 **Auto-Feynman Trigger** - Zero-click help automatically activated when score < 70%
- 📄 **PDF Reports** - Professional multi-page session summaries with ReportLab
- ⏭️ **Auto-Submit** - Questions auto-submit when all fields completed
- 🔄 **Intelligent Retry** - Fresh questions generated after Feynman explanations
- 📊 **Real-Time Dashboard** - Interactive Plotly charts for live performance tracking
- 📈 **Historical Tracking** - SQLite database with complete session history
- ⏰ **Time Analytics** - Precise time tracking per checkpoint and overall session
- 📉 **Trend Analysis** - Performance trends and insights across multiple sessions

### Workflow Features
- 🔀 **State Management** - Complete LangGraph state machine (25+ variables)
- 🎯 **Objective Alignment** - Questions directly tied to learning objectives
- 🧩 **Modular Architecture** - 15+ independent, testable components
- 🔁 **Retry Logic** - Smart retry mechanisms at multiple workflow stages
- 💾 **Auto-Save** - Automatic progress saving to database

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
git clone <repository-url>
cd Tutor
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys
Create `.env` file:
```bash
GOOGLE_API_KEY=your_google_gemini_api_key
TAVILY_API_KEY=your_tavily_search_key  # Optional
```

Get keys:
- **Google Gemini**: https://makersuite.google.com/app/apikey
- **Tavily**: https://tavily.com/#api

### 3. Launch Application
```bash
streamlit run app.py
```

Access at: **http://localhost:8501**

### 4. Start Learning
1. Select "Python Basics" template (or create custom)
2. Answer questions as they appear
3. Experience automatic Feynman teaching if needed
4. Download PDF report at completion

---

## � Development Journey

### Project Evolution

| Milestone | Focus | Key Achievement | Status |
|-----------|-------|----------------|--------|
| **Milestone 1** | Foundation | Core workflow with checkpoint-based learning | ✅ Complete |
| **Milestone 2** | Intelligence | Vector embeddings & semantic search | ✅ Complete |
| **Milestone 3** | Adaptation | Feynman teaching for struggling learners | ✅ Complete |
| **Milestone 4** | Scale | Multi-checkpoint progression & web UI | ✅ Complete |
| **Phase 1-3** | Production | Auto-features, PDF reports, analytics | ✅ Complete |

### Current Statistics

- **Total Code Lines:** 4,500+ (excluding notebooks)
- **Main Components:** 15+ classes, 8 workflow nodes
- **Test Coverage:** 5 comprehensive test suites
- **Documentation:** 3 detailed markdown files
- **Dependencies:** 20+ Python packages

### Feynman Technique Implementation

> "If you can't explain it simply, you don't understand it well enough." - Richard Feynman

Our implementation automatically generates:
- ✅ Simple, everyday language explanations
- ✅ Relatable analogies and metaphors
- ✅ Step-by-step concept breakdowns
- ✅ Concrete code examples
- ✅ Common mistake identification

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Step-by-Step

#### 1. Clone Repository
```bash
git clone <repository-url>
cd Tutor
```

#### 2. Create Virtual Environment
```bash
# Create venv
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Core Dependencies**:
```
streamlit>=1.28.0           # Web interface
langgraph>=0.2.0            # Workflow orchestration
langchain>=0.3.0            # LLM framework
langchain-google-genai      # Google Gemini integration
langchain-huggingface       # HuggingFace embeddings
faiss-cpu>=1.7.4            # Vector similarity search
sentence-transformers       # Text embeddings
tavily-python               # Web search
reportlab>=4.0.0            # PDF generation
plotly>=5.17.0              # Interactive charts
pandas>=2.1.0               # Data manipulation
sqlalchemy>=2.0.0           # Database ORM
```

#### 4. Configure Environment
```bash
# Create .env file
cp .env.example .env

# Edit with your API keys
nano .env  # or use any text editor
```

**.env Template**:
```bash
# Required
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Optional
TAVILY_API_KEY=your_tavily_api_key_here

# Configuration (defaults shown)
UNDERSTANDING_THRESHOLD=0.70
MAX_RETRIES=3
CHUNK_SIZE=1000
```

#### 5. Verify Installation
```bash
# Test imports
python -c "import streamlit, langgraph, langchain; print('✅ All core dependencies installed')"

# Test embeddings
python -c "from sentence_transformers import SentenceTransformer; print('✅ Embeddings ready')"
```

---

## 🎮 Usage

### Method 1: Streamlit Web Interface ⭐ **Recommended**

```bash
streamlit run app.py
```

**Access**: http://localhost:8501

**Features**:
- ✅ Visual interface with progress tracking
- ✅ Interactive question answering
- ✅ Real-time analytics dashboard
- ✅ PDF report download
- ✅ Historical performance view
- ✅ Checkpoint progress sidebar

**User Flow**:
1. **Setup** → Choose template or create custom checkpoints
2. **Learning** → System processes checkpoint (30-60 seconds)
3. **Questions** → Answer in text areas (auto-submit enabled)
4. **Results** → View score, automatic Feynman if needed
5. **Feynman** → Read simplified explanations, retry option
6. **Complete** → Download PDF, view analytics

---

### Method 2: Interactive CLI

```bash
python interactive_milestone4.py
```

**Features**:
- Terminal-based interaction
- Manual answer input
- Complete workflow
- Good for testing/debugging

---

### Method 3: Automated Testing

```bash
python test_milestone4.py
```

**Features**:
- Predefined answers
- Tests 3-checkpoint workflow
- Performance validation
- Useful for CI/CD

---

### Method 4: Standard Script

```bash
python main.py
```

**Features**:
- Quick testing
- 2-checkpoint demo
- Minimal configuration

---

## 🏛️ Architecture

### System Overview

```
┌─────────────────────────────────────────┐
│         Streamlit Web Interface         │
│    (User Interaction & Visualization)   │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│        LangGraph Workflow Engine        │
│     (State Machine & Orchestration)     │
└─┬────────┬────────┬────────┬─────────── ┘
  │        │        │        │
  ▼        ▼        ▼        ▼
┌────┐  ┌────┐  ┌────┐  ┌────┐
│Ctx │  │Vec │  │Qst │  │Vrf │
│Mgr │  │Str │  │Gen │  │yer │
└─┬──┘  └─┬──┘  └─┬──┘  └─┬──┘
  │       │       │       │
  └───────┴───────┴───────┘
              │
    ┌─────────┴─────────┐
    ▼                   ▼
┌────────┐        ┌──────────┐
│Google  │        │ Tavily   │
│Gemini  │        │ Search   │
└────────┘        └──────────┘
```

### Component Descriptions

#### 1. **LangGraph Workflow**
- State machine orchestration
- Node execution management
- Conditional edge routing
- State persistence

#### 2. **Context Manager**
- Web search integration
- Content aggregation
- Text chunking
- Relevance validation

#### 3. **Vector Store Manager**
- FAISS index creation
- Text embeddings (384-dim)
- Similarity search (k-NN)
- Document retrieval

#### 4. **Question Generator**
- LLM-powered question creation
- Objective-aligned questions
- Difficulty level control
- JSON output parsing

#### 5. **Understanding Verifier**
- Answer evaluation
- Context-based scoring
- Pass/fail determination
- Feedback generation

#### 6. **Feynman Teacher**
- Concept simplification
- Analogy generation
- Step-by-step explanations
- Example provision

---

### Data Flow

```mermaid
graph TD
    A[User Input] --> B[Define Checkpoint]
    B --> C[Gather Context]
    C --> D[Web Search]
    D --> E[Chunk Text]
    E --> F[Create Embeddings]
    F --> G[Generate Questions]
    G --> H[User Answers]
    H --> I[Evaluate Answers]
    � Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│  ┌──────────────────────┐     ┌──────────────────────┐     │
│  │   Streamlit App      │     │    CLI Interface     │     │
│  │   (app.py - 986L)    │     │   (main.py - 218L)   │     │
│  └──────────┬───────────┘     └──────────┬───────────┘     │
## 📂 Project Structure

```
Tutor/
├── 📄 app.py                          # Streamlit web interface (986 lines)
├── 📄 main.py                         # CLI demo script (218 lines)
├── 📄 requirements.txt                # Python dependencies
├── 📄 README.md                       # This file
├── 📄 DOCUMENTATION.md                # Complete technical docs
├── 📄 PROJECT_STRUCTURE.md            # Detailed structure guide
├── 📄 .env                            # API keys (create from .env.example)
│
├── 📁 src/                            # Source code
│   ├── 📁 models/                     # Data models (checkpoint, state)
│   ├── 📁 graph/                      # LangGraph workflow (756 lines)
│   ├── 📁 modules/                    # Core logic (6 modules, ~1,440 lines)
│   │   ├── context_manager.py
│   │   ├── vector_store_manager.py
│   │   ├── question_generator.py
│   │   ├── understanding_verifier.py
│   │   └── feynman_teacher.py
│   └── 📁 utils/                      # Utilities (4 files, ~1,070 lines)
│       ├── llm_provider.py
│       ├── search_tools.py
│       ├── pdf_generator.py
│       └── database_manager.py
│
├── 📁 notebooks/                      # Development artifacts (optional)
├── 📁 tests/                          # Unit tests
└── 📄 learning_sessions.db            # SQLite database (auto-generated)
```

> **📂 For complete file breakdown, see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**

---

## 💻 API Examples

### Quick Start Example

```python
from src.models.checkpoint import Checkpoint
from src.models.state import create_initial_state
from src.graph.learning_graph import LearningGraph

# 1. Create checkpoints
checkpoint = Checkpoint(
    topic="Python Functions",
    objectives=[
        "Understand function syntax",
        "Learn about parameters and return values"
    ],
    difficulty_level="beginner"
)

# 2. Initialize state
state = create_initial_state(
    checkpoints=[checkpoint],
    user_notes="Focus on practical examples"
)

# 3. Create and run workflow
graph = LearningGraph().build_graph()
result = graph.invoke(state)

# 4. Check results
print(f"Score: {result['understanding_score']:.1%}")
print(f"Passed: {result['passed_checkpoint']}")
```

### Generate PDF Report

```python
from src.utils.pdf_generator import LearningReportGenerator

generator = LearningReportGenerator()
pdf_buffer = generator.generate_report({
    'checkpoints': checkpoint_history,
    'overall_score': 0.85,
    'total_time': 1800,
    'completion_date': datetime.now()
})

# Save PDF
with open('report.pdf', 'wb') as f:
    f.write(pdf_buffer.getvalue())
```

### Access Database

```python
from src.utils.database_manager import SessionDatabase

db = SessionDatabase('learning_sessions.db')

# Get recent sessions
history = db.get_session_history(limit=10)

# Get performance statistics
stats = db.get_performance_stats()
print(f"Average Score: {stats['avg_score']:.1%}")
print(f"Pass Rate: {stats['pass_rate']:.1%}")
```

> **📚 For complete API reference, see [DOCUMENTATION.md](DOCUMENTATION.md)**m src.utils.database_manager import SessionDatabase

db = SessionDatabase('learning_sessions.db')

# Save session
session_id = db.save_session(session_data)

# Get history
history = db.get_session_history(limit=10)

# Get trends
trends = db.get_performance_trends()

# Get statistics
stats = db.get_statistics()
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AZURE_API_KEY` | Azure OpenAI API key | - | ✅ Yes |
| `SERP_API_KEY` | SERP API key | - | ⚠️ Optional |
| `UNDERSTANDING_THRESHOLD` | Pass threshold (0-1) | 0.70 | No |
| `MAX_RETRIES` | Context gathering retries | 3 | No |
| `CHUNK_SIZE` | Text chunk size | 1000 | No |
| `MAX_FEYNMAN_ATTEMPTS` | Retry attempts | 3 | No |

### Streamlit Configuration

Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
port = 8501
headless = false
enableCORS = false
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. API Key Errors
```
Error: Invalid API key
```
**Solution**:
- Verify `.env` file exists in project root
- Check key format: `AIza...` for Google
- Ensure no extra spaces or quotes
- Restart application after adding keys

#### 2. Import Errors
```
ModuleNotFoundError: No module named 'sentence_transformers'
```
**Solution**:
```bash
pip install sentence-transformers
# Or reinstall all
pip install -r requirements.txt
```

#### 3. TensorFlow DLL Error (Windows)
```
DLL load failed while importing _pywrap_tensorflow_internal
```
**Solution**:
- Install Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Or uninstall TensorFlow if not needed: `pip uninstall tensorflow`

#### 4. FAISS Installation Issues
```
ImportError: DLL load failed for faiss
```
**Solution**:
```bash
pip uninstall faiss-cpu
pip install faiss-cpu --no-cache-dir
```

#### 5. Streamlit Not Starting
```
Error: No module named 'streamlit'
```
**Solution**:
```bash
# Ensure venv is activated
source venv/bin/activate  # or .\venv\Scripts\activate

# Install Streamlit
pip install streamlit

# Run explicitly
python -m streamlit run app.py
```

### Performance Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Slow question generation | LLM API latency | Use `gemini-1.5-flash` model |
| High memory usage | FAISS vectors in RAM | Reduce `CHUNK_SIZE` to 500 |
| Long processing time | Web search timeout | Set `MAX_SEARCH_RESULTS=3` |

### Debug Mode

Enable logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🧪 Testing

### Run Tests
```bash
# Full workflow test (3 checkpoints)
python test_milestone4.py

# Interactive testing
python interactive_milestone4.py

# Quick demo (2 checkpoints)
python main.py

# Unit tests (if available)
pytest tests/
```

### Test Coverage

| Component | File | Status |
|-----------|------|--------|
| Workflow | `test_milestone4.py` | ✅ Complete |
| Context Manager | `tests/test_context.py` | ✅ Unit tests |
| Vector Store | `tests/test_vectors.py` | ✅ Unit tests |
| Question Generator | `tests/test_questions.py` | ✅ Unit tests |
| Verifier | `tests/test_verifier.py` | ✅ Unit tests |

## 📚 Documentation

### Available Documentation

- **[README.md](README.md)** (this file) - Quick start and overview
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete technical documentation
  - Architecture deep-dive
  - API reference
  - Database schema
  - Configuration guide
  - Development milestones
  
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Detailed structure guide
  - Complete directory tree
  - File-by-file breakdown
  - Module dependencies
  - Data flow diagrams
  - Code organization

---

## 🧪 Testing

```bash
# Run main demo (2 checkpoints)
python main.py

# Web interface (full features)
streamlit run app.py
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangChain/LangGraph** - Agentic workflow framework
- **Azure OpenAI** - OpenAI LLM access
- **HuggingFace** - Pre-trained embedding models
- **Streamlit** - Rapid web application framework
- **Facebook AI** - FAISS vector similarity search
- **Richard Feynman** - Teaching methodology inspiration

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Total Code** | 4,500+ lines |
| **Components** | 15+ classes |
| **Workflow Nodes** | 8 specialized nodes |
| **Dependencies** | 20+ packages |
| **Documentation** | 3 comprehensive files |
| **Development Time** | 4 milestone phases |

---

## 🎯 Quick Reference

```bash
# Start web application
streamlit run app.py

# Run CLI demo
python main.py

# Access at
http://localhost:8501
```

**Database:** `learning_sessions.db` (auto-created)  
**Reports:** Generated as PDF on session completion  
**Configuration:** `.env` file (create from `.env.example`)

---

## 📞 Support & Contact

- **Issues:** [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation:** See [DOCUMENTATION.md](DOCUMENTATION.md)


---

**Built with ❤️ by Saket using LangGraph, LangChain, and Streamlit**

**Transform your learning experience with AI-powered adaptive education