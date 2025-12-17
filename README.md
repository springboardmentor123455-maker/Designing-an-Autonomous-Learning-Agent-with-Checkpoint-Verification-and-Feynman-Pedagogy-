# Autonomous Learning Agent

An AI-powered tutoring system using LangGraph that provides personalized learning experiences with checkpoint-based progression and adaptive teaching using the Feynman technique.

**🎯 Status: Milestone 1 Complete** - Context gathering, validation, and checkpoint structure fully implemented.

## Features

### ✅ Implemented (Milestone 1)
- **Structured Learning Path**: Sequential checkpoints with defined objectives
- **Adaptive Content**: User notes → web search fallback for dynamic content  
- **Context Validation**: LLM-based relevance scoring and quality assurance
- **Local AI**: Runs completely offline using Ollama (llama3.1)
- **LangGraph Workflow**: State-based orchestration with retry logic

### 🚧 In Development
- **Rigorous Assessment**: Automated question generation and scoring
- **Feynman Teaching**: Simplifies complex concepts when understanding is insufficient
- **Web Interface**: Streamlit-based UI for learner interaction

## Tech Stack

### Core Framework
- **LangGraph**: Workflow orchestration and state management
- **Ollama**: Local LLM integration (llama3.1)
- **Python 3.11**: Primary development language

### Implemented Components  
- **DuckDuckGo**: Web search API for content gathering
- **Pydantic**: Data validation and modeling
- **AsyncIO**: Asynchronous workflow processing

### Prepared for Future Milestones
- **ChromaDB**: Vector storage for embeddings
- **Streamlit**: Web interface framework  
- **SQLite**: Progress persistence database

## Quick Start

1. **Install Ollama**
   ```bash
   # Download from https://ollama.com/
   # Pull the llama3.1 model
   ollama pull llama3.1
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Milestone 1 Demo**
   ```bash
   python milestone1.py
   ```

4. **Explore Available Checkpoints**
   ```bash
   python app.py --action list-checkpoints
   ```

## Project Structure

```
├── src/
│   ├── agents/          # LangGraph workflow nodes & state management
│   ├── models/          # Pydantic data models and schemas  
│   ├── tools/           # LLM integration, web search, document processing
│   └── storage/         # Vector DB and progress storage (prepared)
├── data/
│   ├── checkpoints/     # Sample learning checkpoint definitions
│   └── user_notes/      # User uploaded documents
├── config/              # Environment and configuration files
├── milestone1.py        # Milestone 1 comprehensive demo
└── app.py              # Utility commands and checkpoint management
```

## Usage Examples

### Run Complete Milestone 1 Demo
```bash
python milestone1.py
# Demonstrates: System verification, component testing, 
# workflow execution, and multi-checkpoint evaluation
```

### List Available Checkpoints  
```bash
python app.py --action list-checkpoints
# Shows all 8 sample checkpoints across different subjects
```

## Development Milestones

- [x] **Milestone 1**: Checkpoint Structure & Context Gathering ✅ **COMPLETE**
  - ✅ Project environment setup (Python, LangGraph, Ollama, DuckDuckGo)
  - ✅ Data structures for checkpoints, objectives, success criteria  
  - ✅ LangGraph workflow nodes for context gathering and validation
  - ✅ Context validation logic with 1-5 relevance scoring
  - ✅ Evaluation: 8 checkpoints tested, 3.97/4.0 average relevance score

- [ ] **Milestone 2**: Context Processing & Initial Verification (Weeks 3-4)  
  - [ ] Context chunking, embedding, and vector storage
  - [ ] Question generation (3-5 per checkpoint) 
  - [ ] Initial verification scoring system

- [ ] **Milestone 3**: Feynman Teaching Implementation (Weeks 5-6)
  - [ ] Knowledge gap identification
  - [ ] Simplified explanation generation
  - [ ] Loop-back mechanism integration

- [ ] **Milestone 4**: Integration & End-to-End Testing (Weeks 7-8)
  - [ ] Multi-checkpoint progression logic
  - [ ] End-to-end learning path simulation
  - [ ] Optional web interface integration

## Current Implementation Details

### Milestone 1 Achievements
- **LangGraph Workflow**: Fully operational state-based workflow with conditional routing
- **Context Gathering**: User notes priority → web search fallback system
- **Quality Validation**: LLM-powered relevance scoring with automatic retry logic  
- **Data Models**: Comprehensive Pydantic models for structured learning data
- **Error Handling**: Robust error handling with configurable retry mechanisms

### Configuration
- Environment variables in `.env` (copy from `.env.example`)
- Configurable thresholds and parameters in `config/settings.py`
- Sample checkpoints across multiple subjects (science, math, history, etc.)

### Next Steps (Milestone 2)
- Implement ChromaDB vector storage for context embeddings
- Develop question generation system based on processed context
- Create scoring mechanism for learner answer evaluation
- Build conditional logic for 70% threshold progression

## License

MIT License - see LICENSE file for details.