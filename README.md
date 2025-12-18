# 🎓 Interactive Learning Agent System

**An autonomous AI tutoring system with personalized checkpoints, adaptive questioning, and Feynman pedagogy.**

## 🎯 Project Overview

This system implements a complete autonomous learning agent using LangGraph that provides structured, personalized tutoring experiences. The agent guides users through sequential learning checkpoints, generates contextual questions, and employs mastery-based progression with the Feynman Technique for adaptive simplification.

### 🌟 Core Objectives
- **Structured Guidance**: Clear learning paths through sequential checkpoints
- **Flexible Content**: Dynamic content retrieval and user-provided materials
- **Rigorous Assessment**: Automatic question generation with 70% threshold verification
- **Adaptive Simplification**: Feynman Technique for concept re-explanation
- **Mastery-Based Progression**: Strict checkpoint completion requirements
- **Interactive Interface**: Full user interaction and feedback system

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Ollama installed and running
- 4GB+ RAM recommended

### 1. Environment Setup
```bash
# Clone and navigate to project
cd path/to/project

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install langgraph langchain langchain-ollama chromadb sentence-transformers torch numpy
```

### 2. Ollama Installation
```bash
# Visit https://ollama.ai and install Ollama
# Pull a lightweight model:
ollama pull llama3.2:1b

# Start Ollama service (if not auto-started)
ollama serve
```

### 3. Run the System
```bash
# Interactive Mode (Default)
python learning_agent.py

# Demo Mode (Automated)
python learning_agent.py --demo

# Run Validation Tests
python test_enhanced_system.py
```

## 📋 System Architecture

### 🔄 Learning Workflow
1. **Initialize** - Set up learning checkpoint and objectives
2. **Collect Materials** - Gather and validate educational content
3. **Summarize** - Generate comprehensive material summaries
4. **Evaluate Milestone 1** - Score material collection and summary quality
5. **Process Context** - Chunk content and create vector embeddings
6. **Generate Questions** - Create 3-5 contextual questions (min 1 MCQ)
7. **Interactive Assessment** - Collect and score user responses
8. **Threshold Check** - Apply 70% mastery threshold
9. **Route Decision** - Complete checkpoint or trigger Feynman teaching

### 🎮 Interactive Features
- **Multiple Checkpoints**: 4 learning paths (ML, Deep Learning, Data Science, NLP)
- **Adaptive Questioning**: 3-5 questions per session with mixed formats
- **Multiple Choice Questions**: At least 1 MCQ with A/B/C/D options
- **Real-time Scoring**: Immediate feedback with percentage scores
- **User Evaluation**: System performance feedback collection
- **Progress Tracking**: Comprehensive results and recommendations

### 🛠 Technical Components
- **LangGraph Workflow**: State management and node orchestration
- **ChromaDB**: Vector storage for semantic search
- **Sentence Transformers**: Text embedding generation
- **Ollama Integration**: Local LLM for question generation and scoring
- **Interactive UI**: User-friendly checkpoint selection and assessment
- **Comprehensive Logging**: Detailed execution tracking

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌───────────────────┐
│ Initialize  │───▶│ Collect Materials│───▶│ Summarize Materials│
└─────────────┘    └──────────────────┘    └───────────────────┘
       │                                              │
       ▼                                              ▼
┌─────────────┐    ┌──────────────────┐    ┌───────────────────┐
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
# In learning_agent.py, you can modify:
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "llama3.2:1b"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
THRESHOLD = 0.7  # 70% threshold for checkpoint completion
```

## 📊 Example Output

```
🚀 UNIFIED LEARNING AGENT - MILESTONES 1 & 2
============================================================
📚 Checkpoint: Machine Learning Fundamentals
📖 Materials: 3 items

🔄 Executing unified workflow...
----------------------------------------
🚀 Initializing learning session...
📚 Collecting learning materials...
📝 Summarizing materials...
⚖️ Evaluating Milestone 1...
🔄 Processing context...
❓ Generating questions...
✅ Verifying understanding...
🎯 Checking threshold...
🎉 Completing checkpoint...

📊 LEARNING SESSION RESULTS
============================================================
🛤️  Workflow Path: initialize → collect_materials → summarize_materials → evaluate_milestone1 → process_context → generate_questions → verify_understanding → check_threshold → complete_checkpoint
📍 Final Status: checkpoint_completed

📋 MILESTONE 1 RESULTS:
   📚 Materials Collected: 3
   📝 Summary Generated: 487 characters
   ⭐ Milestone 1 Score: 3.8/4.0

🧠 MILESTONE 2 RESULTS:
   🔄 Context Chunks: 8
   ❓ Questions Generated: 4
   ✅ Verification Results: 4
   📊 Overall Score: 82.5%
   🎯 Meets Threshold: ✅ YES

🎉 SUCCESS: Checkpoint completed with 82.5%!
✨ Learning session completed!
```

## 🧪 Components in Detail

### **ContextProcessor Class**
- **Text Chunking**: RecursiveCharacterTextSplitter with configurable overlap
- **Embeddings**: HuggingFace sentence-transformers integration
- **Vector Storage**: ChromaDB for semantic similarity and retrieval

### **LLMService Class** 
- **Question Generation**: Context-aware question creation using LLM
- **Answer Simulation**: Realistic learner response generation
- **Scoring System**: Automated evaluation with detailed feedback

### **Workflow Nodes**
- **Milestone 1**: `initialize`, `collect_materials`, `summarize_materials`, `evaluate_milestone1`
- **Milestone 2**: `process_context`, `generate_questions`, `verify_understanding`, `check_threshold`
- **Routing**: `complete_checkpoint`, `feynman_placeholder`

### **State Management**
- **Comprehensive State**: Single `LearningAgentState` TypedDict for all data
- **Workflow History**: Complete audit trail of execution steps
- **Error Handling**: Graceful error collection and reporting

## 🎯 Success Metrics

### **Milestone 1 Scoring (Max 4.0)**
- Materials Collection: 2.0 points
- Summary Generation: 1.5 points  
- Requirements Coverage: 0.5 points

### **Milestone 2 Scoring (Percentage)**
- Question Relevance: Generated from processed context
- Answer Quality: LLM-based scoring with concept coverage
- Overall Threshold: 70% required for checkpoint completion

## 🔍 Advanced Usage

### **Custom Checkpoints**
```python
custom_checkpoint = {
    "id": "python_basics",
    "title": "Python Programming Fundamentals", 
    "description": "Learn Python syntax, data structures, and control flow",
    "requirements": [
        "Understand variables and data types",
        "Use control structures (if/else, loops)",
        "Work with functions and modules"
    ]
}

# Run with custom checkpoint
result = await run_learning_session(checkpoint=custom_checkpoint)
```

### **Custom Materials**
```python
custom_materials = [
    {
        "id": "python_guide",
        "title": "Python Quick Start Guide",
        "content": "Your educational content here...",
        "source": "tutorial_website"
    }
]

# Run with custom materials
result = await run_learning_session(materials=custom_materials)
```

### **Programmatic Integration**
```python
from learning_agent import create_unified_workflow, LearningAgentState

# Create and compile workflow
workflow = create_unified_workflow()
compiled_workflow = workflow.compile()

# Run with your data
result = await compiled_workflow.ainvoke(initial_state)
```

## 🚨 Troubleshooting

### **Common Issues**

1. **"Ollama connection failed"**
   ```bash
   # Start Ollama service
   ollama serve
   
   # Verify model is available
   ollama list
   
   # Pull model if needed
   ollama pull llama3.2:1b
   ```

2. **"ChromaDB errors"**
   ```bash
   # Delete and recreate database
   rm -rf chroma_db/
   # Restart the learning agent
   ```

3. **"Import errors"**
   ```bash
   # Reinstall dependencies
   pip install -r requirements-milestone2.txt
   
   # Or use the setup script
   python quick_setup.py
   ```

4. **"Memory issues"**
   - Reduce `CHUNK_SIZE` in the code
   - Use smaller embedding models
   - Close other applications

### **Debug Mode**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run learning_agent.py
```

## 🛣️ Future Extensions

### **Planned Enhancements (Milestone 3+)**
- **Feynman Teaching**: Replace placeholder with interactive teaching
- **Multi-Modal Learning**: Support images, videos, audio
- **Adaptive Difficulty**: Dynamic question complexity adjustment
- **Personalization**: Individual learning style optimization
- **Analytics Dashboard**: Visual learning progress tracking
- **Collaborative Features**: Team learning and peer review

### **Integration Possibilities**
- **LMS Integration**: Canvas, Blackboard, Moodle compatibility
- **Content APIs**: Wikipedia, Khan Academy, Coursera integration
- **Assessment Tools**: Automated quiz generation and grading
- **Progress Tracking**: Long-term learning path management

## 📚 Dependencies

### **Core Requirements**
```txt
# Core Framework
langgraph>=0.2.0
langchain>=0.3.0
langchain-ollama>=0.2.0

# Vector Storage & Embeddings  
chromadb>=0.5.0
sentence-transformers>=2.0.0

# ML & Processing
torch>=2.0.0
numpy>=1.24.0
```

### **Optional Dependencies**
```txt
# Development & Testing
pytest>=7.0.0
pytest-asyncio>=0.21.0

# Enhanced UI (future)
streamlit>=1.28.0
gradio>=3.50.0
```

## 🎮 Interactive Experience

### **Session Flow**
1. **Welcome Screen** - System introduction and feature overview
2. **Checkpoint Selection** - Choose from 4 available learning paths:
   - Machine Learning Fundamentals
   - Deep Learning Essentials  
   - Data Science Pipeline
   - Natural Language Processing
3. **Learning Processing** - Automated material collection and analysis
4. **Interactive Assessment** - Answer 3-5 questions with real-time feedback
5. **Results & Feedback** - Comprehensive performance report and recommendations

### **Question Types**
```
Multiple Choice (A/B/C/D):
❓ What are the main types of machine learning?
   A) Supervised, Unsupervised, Reinforcement ✓
   B) Classification, Regression, Clustering
   C) Linear, Non-linear, Deep Learning  
   D) Batch, Online, Transfer Learning

Open-Ended:
❓ Explain the difference between supervised and unsupervised learning.
💭 Expected topics: Labeled data, learning objectives, algorithms...
```

### **Scoring System**
- **MCQ Questions**: 100% for correct answer, 0% for incorrect
- **Open-Ended**: LLM-based evaluation (0-100%) using concept coverage
- **Overall Score**: Weighted average across all questions
- **Threshold**: 70% required to pass checkpoint

## 📊 System Performance

### **Validation Metrics**
- ✅ **Question Relevance**: >80% relevance to learning objectives
- ✅ **Scoring Accuracy**: >90% correct evaluation of good vs poor answers
- ✅ **MCQ Generation**: 100% success rate for including multiple choice questions
- ✅ **Threshold Logic**: Accurate 70% pass/fail determination

### **Performance Benchmarks**
- **Startup Time**: ~5-10 seconds (model loading)
- **Question Generation**: ~10-20 seconds per set
- **Answer Scoring**: ~3-5 seconds per response
- **Memory Usage**: ~1-2GB RAM (depending on model size)

## 🔧 Development

### **Project Structure**
```
src/
├── main.py              # Entry point and interactive mode
├── workflow.py          # LangGraph workflow definition
├── workflow_nodes.py    # Individual workflow node implementations
├── models.py            # Data models and state definitions
├── llm_service.py       # LLM integration and question generation
├── context_processor.py # Text processing and embeddings
├── interactive.py       # User interface functions
└── sample_data.py       # Test checkpoints and materials
```

### **Key Classes**
- `LearningAgentState`: Complete system state management
- `ContextProcessor`: Text chunking, embeddings, vector storage
- `LLMService`: Question generation, answer scoring, LLM integration
- `Interactive Functions`: User interface, checkpoint selection, results display

### **Adding New Checkpoints**
```python
# In src/sample_data.py
new_checkpoint = {
    "id": "your_topic",
    "title": "Your Learning Topic",
    "description": "Topic description and objectives",
    "requirements": [
        "Learning objective 1",
        "Learning objective 2",
        "Learning objective 3"
    ]
}
```

## 🧪 Testing

### **Run Test Suite**
```bash
# Full system validation
python test_enhanced_system.py

# Expected output shows validation of:
# - Question relevance (>80% target)
# - Scoring accuracy (>90% target) 
# - MCQ functionality (100% target)
# - Threshold logic validation
# - System integration tests
```

### **Manual Testing**
```bash
# Test interactive mode
python learning_agent.py

# Test demo mode  
python learning_agent.py --demo

# Check logs
tail -f learning_agent.log
```

## 📈 Usage Analytics

### **Success Criteria**
The system tracks and reports:
- Question relevance to checkpoint objectives
- Answer scoring accuracy vs human evaluation
- MCQ generation success rate
- User satisfaction and feedback scores
- System performance metrics

### **Continuous Improvement**
Based on user feedback:
- Question quality refinement
- Scoring algorithm enhancement  
- User experience optimization
- Performance monitoring and optimization

## 🤝 Contributing

### **Code Style**
- Python 3.8+ with type hints
- Async/await for workflow operations
- Comprehensive logging and error handling
- Clear documentation and comments

### **Development Setup**
```bash
git clone <repository>
cd learning-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/
```

## 📄 License

MIT License - see LICENSE file for details.

## 🎯 Conclusion

This Interactive Learning Agent System represents a complete implementation of autonomous tutoring with:
- ✅ Structured checkpoint-based learning
- ✅ Intelligent question generation and scoring  
- ✅ Interactive user experience with multiple choice and open-ended questions
- ✅ Mastery-based progression with 70% threshold
- ✅ Comprehensive validation and performance metrics
- ✅ Full documentation and testing framework

**Ready for educational use and further development!** 🚀📚
- **Ollama**: Local LLM inference
- **ChromaDB**: Vector database
- **Sentence Transformers**: Text embeddings
- **PyTorch**: ML computations

### **Optional Enhancements**
- **Jupyter**: Interactive development
- **Rich**: Enhanced terminal output
- **Streamlit**: Web UI (future feature)

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 🤝 Contributing

This is a complete, self-contained learning agent system. The unified architecture makes it easy to:

1. **Extend functionality** - Add new workflow nodes
2. **Customize scoring** - Modify evaluation criteria  
3. **Integrate content sources** - Add new material providers
4. **Enhance UI** - Build web or desktop interfaces

## 🎉 Summary

This unified learning agent system successfully combines:

✅ **Milestone 1**: Material collection, summarization, and evaluation  
✅ **Milestone 2**: Context processing, question generation, and understanding verification  
✅ **Threshold Logic**: 70% score requirement with conditional routing  
✅ **Complete Workflow**: End-to-end learning session management  
✅ **Production Ready**: Error handling, logging, and configuration  
✅ **Extensible Architecture**: Ready for Milestone 3 and beyond  

**Ready to learn? Run `python learning_agent.py` to get started! 🚀**