# 🎓 Learning Agent System

AI-powered tutoring platform with checkpoint-based learning, adaptive assessment, and intelligent concept simplification.

## 🚀 Quick Start

```bash
# 1. Install Ollama (ollama.com) and pull model
ollama pull llama3.1

# 2. Activate environment and install dependencies
source .venv/Scripts/activate  # Windows
pip install -r requirements.txt

# 3. Launch web app
streamlit run app.py  # → http://localhost:8501
```

**CLI Mode:** `python -m src.multi_checkpoint`

## ✨ Features

- **Checkpoint Learning** - Sequential milestone progression
- **AI Assessment** - Auto-generated contextual questions  
- **Adaptive Teaching** - Feynman Technique simplification
- **Document Upload** - PDF, DOCX, MD, TXT support
- **Custom Topics** - Create personalized paths
- **70% Threshold** - Mastery-based advancement

## 📖 How to Use

1. Launch app → Select/create topic
2. Upload materials (optional)
3. Answer AI questions
4. Score ≥70% → Next checkpoint
5. Score <70% → Simplified teaching → Retry

## 🛠️ Troubleshooting

**Ollama Error:**
```bash
ollama serve
ollama list && ollama pull llama3.1
```

**Environment:**
```env
OLLAMA_MODEL=llama3.1:latest
LANGCHAIN_API_KEY=your_key  # Optional
```────────────┐
│Evaluate M1  │◀───│ Process Context  │◀───│  Generate Questions│
└─────────────┘    └──────────────────┘    └───────────────────┘
       │                     │                         │
       ▼                     ▼                         ▼
┌─────────────┐    ┌──────────────────┐    ┌───────────────────┐
│Process Cont.│───▶│ Generate Questions│───▶│ Verify Understanding│
└─────────────┘    └──────────────────┘    └───────────────────┘
                                                      │
                                                      ▼
                    ┌─────────────┐         ┌────────────────┐
                    │Check Thresh.│◀────────│                │
                    └─────────────┘         └────────────────┘
                           │
              ┌────────────┴─────────────┐
              ▼                          ▼
     ┌─────────────┐            ┌─────────────────┐
     │Complete     │            │Feynman Teaching │
     │Checkpoint   │            │(Milestone 3)    │
     │(≥70%)       │            │(<70%)           │
     └─────────────┘            └─────────────────┘
```

## 📁 File Structure

```
learning_agent.py           # Complete unified system (main file)
quick_setup.py             # Automated setup script
README.md                  # This documentation
requirements-milestone2.txt # All dependencies
goal.json                  # Project goals
LICENSE                    # MIT License

# Auto-generated during execution:
learning_agent.log         # Detailed execution logs
chroma_db/                 # Vector database (ChromaDB)
config.json                # Runtime configuration
```

## 🔧 Configuration

The system uses sensible defaults but can be customized:

```python
# Configure in .env file:
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
THRESHOLD=0.7  # 70% threshold for checkpoint completion

# LangSmith Integration (Optional)
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_ENDPOINT=https://eu.api.smith.langchain.com
LANGCHAIN_PROJECT=default
ENABLE_LANGSMITH=true
```

## 🔍 LangSmith Integration

### Real-Time Monitoring
The system includes comprehensive LangSmith integration for monitoring:
## 📚 Documentation

📖 **[Complete Technical Documentation](Documentation.md)** - Architecture, API reference, workflows, development guide

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

**Built with:** LangGraph • Ollama • Streamlit • ChromaDB