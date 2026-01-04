# 🎓 Autonomous Learning Agent

An intelligent tutoring system that provides personalized, structured learning experiences through adaptive checkpoint verification and simplified explanations using the Feynman Technique.

---

## 🌟 Features

### **Core Capabilities**

- **📍 Checkpoint-Based Learning** - Structured progression through 3 sequential learning milestones
- **🤖 AI-Powered Assessment** - Automated question generation and intelligent answer evaluation
- **💡 Feynman Technique** - Simplified explanations using analogies when understanding is insufficient
- **📊 Mastery-Based Progression** - 70% threshold requirement before advancing
- **📝 Flexible Content Sources** - Uses learner's notes or dynamically retrieves web content
- **🔄 Adaptive Teaching** - Loop-back mechanism for re-assessment after simplified explanations

### **Technical Highlights**

- **LangGraph State Management** - Graph-based workflow orchestration
- **Groq LLM Integration** - Ultra-fast inference with Llama 3.3 70B
- **Real-time Feedback** - Instant scoring and detailed breakdown
- **User-Friendly Interface** - Clean, responsive web UI

---
📚 Usage Guide
Starting a Learning Session
Enter your learning topic (e.g., "Machine Learning", "Blockchain")

Optionally paste your study materials in the notes field

Click "Begin Learning Journey"

Assessment Process
Read the provided learning content

Answer all 5 questions thoroughly

Submit for AI evaluation

Review your detailed score breakdown

If Score < 70%
Click "Get Feynman Explanation" for simplified teaching

Take a new assessment with different questions

Maximum 2 retry attempts per checkpoint

Progression
Pass checkpoint (≥70%) → Advance to next checkpoint

Complete all 3 checkpoints → Learning path finished!

🛠️ Tech Stack
Category	Technology
Backend	Python 3.11+, Flask
Workflow Engine	LangGraph 0.2.34
LLM Framework	LangChain 0.3.0
AI Model	Groq API (Llama 3.3 70B)
Web Search	Wikipedia API + LLM Fallback
Frontend	HTML5, CSS3, Vanilla JavaScript
Text Processing	RecursiveCharacterTextSplitter
Environment	python-dotenv


🔑 Environment Variables
Variable	Description	Required
GROQ_API_KEY	Your Groq API key from console.groq.com	✅ Yes


🎯 Key Components
LangGraph State Graph
The core workflow engine orchestrating:

State management across learning stages

Conditional routing based on assessment scores

Loop-back mechanism for adaptive teaching

Checkpoint System
Checkpoint 1: Introduction & Fundamentals

Checkpoint 2: Core Concepts & Techniques

Checkpoint 3: Applications & Implementation

Assessment Module
Generates 5 context-specific questions per checkpoint

Each question scored 0-5 points (25 points total)

70% threshold = 17.5/25 points required

Feynman Teaching
Activated when score < 70%:

Identifies knowledge gaps

Generates simplified explanations with analogies

Uses 8th-grade vocabulary

Includes emojis for engagement


🙏 Acknowledgments
LangGraph - For the state graph framework

Groq - For ultra-fast LLM inference

Feynman Technique - For the teaching methodology inspiration

Open Source Community - For the amazing tools and libraries


👨‍💻 Author
Nidhin R
