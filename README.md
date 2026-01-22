AI Learning Agent with Feynman Technique
An intelligent learning system powered by Groq AI that adapts to your learning pace using the Feynman Technique. The agent creates personalized checkpoints, assesses your understanding, and provides simplified explanations when needed.

✨ Features

- Ultra-fast AI inference with Groq's LPU technology
- Adaptive Learning Paths - Create custom checkpoints with specific learning objectives
- Feynman Technique Integration - Automatically generates simplified explanations when you struggle
- Smart Context Gathering - Uses your notes or searches the web for learning materials
- Intelligent Assessment - AI-powered evaluation of your answers
- Progress Tracking - Visual progress indicators and checkpoint management
- LangSmith Observability - Optional tracing for debugging and optimization

🏗️ Architecture
This application uses LangGraph to create a stateful workflow with the following nodes:
┌─────────────────────┐
│ Define Checkpoint   │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Gather Context     │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ Validate Context    │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Process Context    │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ Generate Questions  │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Assess Learner     │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Evaluate Score     │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
┌───▼────┐  ┌────▼─────────────┐
│ Passed │  │ Apply Feynman    │
└───┬────┘  └────┬─────────────┘
    │            │
    │       ┌────▼─────────────┐
    │       │ Regenerate Qs    │
    │       └────┬─────────────┘
    │            │
┌───▼────────────▼──┐
│ Next Checkpoint   │
└───────────────────┘
📋 Prerequisites

Python 3.8 or higher
Groq API key 
Tavily API key 
LangSmith API key (optional, for observability)

🚀 Installation

Clone the repository

bashgit clone https://github.com/yourusername/ai-learning-agent.git
cd ai-learning-agent


# Optional
GROQ_MODEL=llama-3.3-70b-versatile
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=learning-agent-groq
🎯 Usage

Start the application

bashstreamlit run app.py

Access the web interface

Open your browser to http://localhost:8501


Create your learning path

(Optional) Paste your study notes
Define learning checkpoints with topics and objectives
Click "Start Learning Journey"


Learn and assess

Read the learning materials
Answer assessment questions
Get simplified Feynman explanations if needed
Progress through checkpoints



🛠️ Technology Stack
ComponentTechnologyLLMGroq (llama-3.3-70b-versatile)FrameworkLangGraph + LangChainWeb SearchTavily Search APIEmbeddingsHuggingFace (all-MiniLM-L6-v2)Vector StoreFAISSUIStreamlitObservabilityLangSmith (optional)
📁 Project Structure
ai-learning-agent/
│
├── app.py                 # Streamlit UI application
├── learning_agent.py      # LangGraph workflow logic
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── docs/
    ├── SETUP.md          # Detailed setup guide
    ├── USAGE.md          # Usage examples
    └── API.md            # API documentation
🔑 Key Features Explained
Feynman Technique
When your assessment score is below the threshold (default: 70%), the agent automatically:

Analyzes which concepts you struggled with
Generates simplified explanations using analogies
Re-tests you with new questions

Context Gathering
The agent intelligently:

First checks if your provided notes cover the topic
Falls back to web search if notes are insufficient
Validates context quality before proceeding

Adaptive Assessment

AI evaluates your answers for accuracy and completeness
Provides detailed scoring (0-100%)
Adapts difficulty based on your performance

🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.
🙏 Acknowledgments

Groq for blazing-fast LLM inference
LangChain and LangGraph for the agent framework
Tavily for intelligent web search
Streamlit for the beautiful UI framework
Richard Feynman for the teaching technique inspiration

