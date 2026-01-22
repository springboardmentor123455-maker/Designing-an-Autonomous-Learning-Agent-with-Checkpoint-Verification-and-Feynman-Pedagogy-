import streamlit as st
import sys
import os
from datetime import datetime

# Import the learning agent
from learning_agent import build_learning_graph, LearningState

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="AI Learning Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .checkpoint-box {
        background-color: #E3F2FD;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin: 1rem 0;
    }
    .score-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .feynman-box {
        background-color: #FFF3E0;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF9800;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE INITIALIZATION ====================
def init_session_state():
    """Initialize session state variables"""
    if 'graph' not in st.session_state:
        st.session_state.graph = build_learning_graph()
    
    if 'state' not in st.session_state:
        st.session_state.state = None
    
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'setup'
    
    if 'checkpoints_defined' not in st.session_state:
        st.session_state.checkpoints_defined = False
    
    if 'learning_started' not in st.session_state:
        st.session_state.learning_started = False

init_session_state()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 🎓 AI Learning Agent")
    st.markdown("---")
    
    # API Keys Check
    st.markdown("#### 🔑 API Configuration")
    
    # Groq API Key Check
    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key and groq_key != "your_groq_api_key_here":
        st.success("✅ Groq API Key Loaded")
        groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        st.caption(f"Model: {groq_model}")
    else:
        st.error("❌ Groq API Key Missing")
        st.info("Add GROQ_API_KEY to .env file")
        st.caption("Get key: https://console.groq.com/keys")
    
    # Tavily API Key Check
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    if tavily_key and tavily_key != "your_tavily_api_key_here":
        st.success("✅ Tavily API Key Loaded")
    else:
        st.error("❌ Tavily API Key Missing")
        st.info("Add TAVILY_API_KEY to .env file")
    
    # LangSmith Check
    langsmith_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    langsmith_key = os.getenv("LANGSMITH_API_KEY", "")
    
    if langsmith_enabled and langsmith_key:
        st.success("✅ LangSmith Tracing Enabled")
        langsmith_project = os.getenv("LANGSMITH_PROJECT", "learning-agent-groq")
        st.caption(f"Project: {langsmith_project}")
        st.markdown(f"[View Traces →](https://smith.langchain.com/)")
    else:
        st.info("ℹ️ LangSmith Tracing Disabled")
        st.caption("Optional: Add LANGSMITH_API_KEY to enable")
    
    st.markdown("---")
    
    # Embeddings Info
    st.markdown("#### 🧮 Embeddings")
    st.success("✅ HuggingFace Embeddings")
    st.caption("Model: all-MiniLM-L6-v2")
    st.caption("(Local, no API key needed)")
    
    st.markdown("---")
    
    # Progress Tracker
    if st.session_state.state:
        st.markdown("#### 📊 Progress")
        current = st.session_state.state.get("current_checkpoint_index", 0)
        total = len(st.session_state.state.get("all_checkpoints", []))
        
        if total > 0:
            progress = current / total
            st.progress(progress)
            st.markdown(f"**Checkpoint {current + 1} of {total}**")
            
            if current < total:
                topic = st.session_state.state.get("checkpoint_topic", "N/A")
                st.info(f"Current Topic: {topic}")
    
    st.markdown("---")
    
    # Reset Button
    if st.button("🔄 Reset Learning Path"):
        st.session_state.state = None
        st.session_state.current_step = 'setup'
        st.session_state.checkpoints_defined = False
        st.session_state.learning_started = False
        st.rerun()

# ==================== MAIN CONTENT ====================
st.markdown('<p class="main-header">🎓 AI Learning Agent with Feynman Technique</p>', 
            unsafe_allow_html=True)

st.caption("Powered by Groq ⚡ | Ultra-fast AI inference")

# ==================== SETUP PHASE ====================
if st.session_state.current_step == 'setup':
    st.markdown("### 📚 Setup Your Learning Path")
    
    # User Notes Input
    st.markdown("#### 📝 Your Study Notes (Optional)")
    st.info("Provide your own notes. If they don't cover a topic, the agent will search the web.")
    user_notes = st.text_area(
        "Paste your study notes here:",
        height=150,
        placeholder="Enter any study materials you have...",
        key="user_notes_input"
    )
    
    # Define Checkpoints
    st.markdown("#### 🎯 Define Learning Checkpoints")
    
    num_checkpoints = st.number_input(
        "How many checkpoints?",
        min_value=1,
        max_value=10,
        value=3,
        step=1
    )
    
    checkpoints = []
    
    for i in range(num_checkpoints):
        with st.expander(f"📍 Checkpoint {i+1}", expanded=(i==0)):
            topic = st.text_input(
                "Topic:",
                key=f"topic_{i}",
                placeholder=f"e.g., Introduction to Python Variables"
            )
            
            objectives_text = st.text_area(
                "Learning Objectives (one per line):",
                key=f"objectives_{i}",
                placeholder="e.g.,\nUnderstand variable declaration\nLearn data types\nPractice assignments",
                height=100
            )
            
            if topic and objectives_text:
                objectives = [obj.strip() for obj in objectives_text.split('\n') if obj.strip()]
                checkpoints.append({
                    "topic": topic,
                    "objectives": objectives
                })
    
    # Start Learning Button
    st.markdown("---")
    
    # Check API keys before allowing start
    can_start = groq_key and tavily_key
    
    if not can_start:
        st.error("⚠️ Please configure required API keys in .env file!")
        st.markdown("""
        **Required API Keys:**
        1. `GROQ_API_KEY` - Get from [Groq Console](https://console.groq.com/keys)
        2. `TAVILY_API_KEY` - Get from [Tavily](https://tavily.com)
        
        **Optional:**
        - `LANGSMITH_API_KEY` - For observability (optional)
        """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Learning Journey", type="primary", use_container_width=True, disabled=not can_start):
            if len(checkpoints) == 0:
                st.error("⚠️ Please define at least one checkpoint!")
            else:
                # Initialize state
                initial_state = {
                    "current_checkpoint_index": 0,
                    "checkpoint_topic": "",
                    "checkpoint_objectives": [],
                    "context": "",
                    "questions": [],
                    "learner_answers": [],
                    "score": 0.0,
                    "threshold": 70.0,
                    "feynman_explanation": "",
                    "status": "initialized",
                    "user_notes": user_notes,
                    "all_checkpoints": checkpoints,
                    "retry_count": 0
                }
                
                st.session_state.state = initial_state
                st.session_state.current_step = 'learning'
                st.session_state.learning_started = True
                st.rerun()

# ==================== LEARNING PHASE ====================
elif st.session_state.current_step == 'learning':
    state = st.session_state.state
    
    # Check if learning is complete
    if state.get("status") == "learning_complete":
        st.balloons()
        st.success("🎉 Congratulations! You've completed all checkpoints!")
        
        total_checkpoints = len(state.get("all_checkpoints", []))
        st.markdown(f"""
        ### 🏆 Learning Journey Complete!
        
        You successfully mastered **{total_checkpoints} checkpoints**!
        
        Great job on your learning journey! 🌟
        """)
        
        if st.button("📚 Start New Learning Path"):
            st.session_state.current_step = 'setup'
            st.session_state.state = None
            st.rerun()
        
    else:
        # Display current checkpoint
        current_checkpoint_index = state.get("current_checkpoint_index", 0)
        topic = state.get("checkpoint_topic", "Loading...")
        objectives = state.get("checkpoint_objectives", [])
        
        st.markdown(f'<div class="checkpoint-box">', unsafe_allow_html=True)
        st.markdown(f"### 📍 Checkpoint {current_checkpoint_index + 1}: {topic}")
        if objectives:
            st.markdown("**Learning Objectives:**")
            for obj in objectives:
                st.markdown(f"- {obj}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Process workflow if questions not yet generated
        if not state.get("questions") or state.get("status") in ["initialized", "checkpoint_complete"]:
            with st.spinner("🔄 Preparing your learning materials... (Powered by Groq ⚡)"):
                try:
                    # Run workflow until questions are generated
                    result = st.session_state.graph.invoke(state)
                    st.session_state.state = result
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Tip: Check your API keys and internet connection")
                    
                    # Show error details in expander
                    with st.expander("🔍 Error Details"):
                        st.code(str(e))
        
        # Display Feynman explanation if exists
        if state.get("feynman_explanation"):
            st.markdown('<div class="feynman-box">', unsafe_allow_html=True)
            st.markdown("### 💡 Simplified Explanation (Feynman Technique)")
            st.markdown(state["feynman_explanation"])
            st.markdown('</div>', unsafe_allow_html=True)
            st.info("📚 Read the explanation above, then try the questions again!")
        
        # Display questions and collect answers
        questions = state.get("questions", [])
        
        if questions:
            st.markdown("### ❓ Assessment Questions")
            st.info("Answer these questions to demonstrate your understanding.")
            
            answers = []
            for i, question in enumerate(questions):
                st.markdown(f"**Question {i+1}:** {question}")
                answer = st.text_area(
                    f"Your answer:",
                    key=f"answer_{current_checkpoint_index}_{i}_{state.get('status', '')}",
                    height=100,
                    placeholder="Type your answer here..."
                )
                answers.append(answer)
            
            # Submit button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("✅ Submit Answers", type="primary", use_container_width=True):
                    # Check if all answers are filled
                    if all(ans.strip() for ans in answers):
                        # Update state with answers
                        state["learner_answers"] = answers
                        
                        with st.spinner("🤔 Evaluating your answers... (Groq AI at work ⚡)"):
                            try:
                                # Run assessment
                                result = st.session_state.graph.invoke(state)
                                st.session_state.state = result
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Assessment error: {str(e)}")
                    else:
                        st.warning("⚠️ Please answer all questions before submitting!")
        
        # Display score if assessed
        score = state.get("score", 0)
        if score > 0 and state.get("status") not in ["questions_generated"]:
            threshold = state.get("threshold", 70)
            
            st.markdown('<div class="score-box">', unsafe_allow_html=True)
            if score >= threshold:
                st.markdown(f"### ✅ Score: {score:.1f}% - PASSED!")
                st.markdown(f"You've mastered this checkpoint! 🎉")
            else:
                st.markdown(f"### 📊 Score: {score:.1f}%")
                st.markdown(f"Threshold: {threshold}% - Let's review!")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Progress to next checkpoint or apply Feynman
            if score >= threshold:
                st.success("Moving to next checkpoint...")
                # Update state
                state["status"] = "passed"
                try:
                    result = st.session_state.graph.invoke(state)
                    st.session_state.state = result
                    st.rerun()
                except Exception as e:
                    st.error(f"Error progressing: {str(e)}")
            else:
                st.info("💡 Generating a simpler explanation for you...")
                state["status"] = "needs_feynman"
                try:
                    result = st.session_state.graph.invoke(state)
                    st.session_state.state = result
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating explanation: {str(e)}")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <small>Built with LangGraph + Groq AI ⚡ + Tavily Search | Powered by Feynman Technique 🧠</small>
    <br>
    <small>Using: Groq LLM | HuggingFace Embeddings | LangSmith Observability</small>
</div>
""", unsafe_allow_html=True)