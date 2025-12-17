# Autonomous Learning Agent

An AI-powered tutoring system using LangGraph that provides personalized learning experiences with checkpoint-based progression and adaptive teaching using the Feynman technique.

## Features

- **Structured Learning Path**: Sequential checkpoints with specific objectives
- **Adaptive Content**: Uses user notes and web search for dynamic content
- **Rigorous Assessment**: Automated question generation and scoring
- **Feynman Teaching**: Simplifies complex concepts when understanding is insufficient
- **Local AI**: Runs completely offline using Ollama
- **Real-time Interface**: Web-based chat interface with file upload

## Tech Stack

- **LangGraph**: Workflow orchestration
- **Ollama**: Local LLM (Llama 3.1, Mistral, etc.)
- **Chroma DB**: Vector storage for embeddings
- **Streamlit**: Web interface
- **DuckDuckGo**: Web search API
- **SQLite**: Progress persistence

## Installation

1. **Install Ollama**
   ```bash
   # Download from https://ollama.com/
   # Then pull a model (e.g., llama3.1)
   ollama pull llama3.1
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## Project Structure

```
├── src/
│   ├── models/          # Data models and schemas
│   ├── agents/          # LangGraph workflow nodes
│   ├── tools/           # Search, document processing, etc.
│   ├── storage/         # Vector DB and progress storage
│   └── interface/       # Streamlit UI components
├── data/
│   ├── checkpoints/     # Learning checkpoint definitions
│   └── user_notes/      # User uploaded documents
├── tests/               # Test cases and evaluation
├── config/              # Configuration files
└── app.py              # Main Streamlit application
```

## Development Milestones

- [x] **Milestone 1**: Checkpoint Structure & Context Gathering (Weeks 1-2)
- [ ] **Milestone 2**: Context Processing & Initial Verification (Weeks 3-4)  
- [ ] **Milestone 3**: Feynman Teaching Implementation (Weeks 5-6)
- [ ] **Milestone 4**: Integration & End-to-End Testing (Weeks 7-8)

## License

MIT License - see LICENSE file for details.