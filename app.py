"""
Streamlit App for Autonomous Learning Agent - Milestone 4 Demo (Enhanced)
Interactive interface with Phase 1-3 Features:
- Auto Feynman trigger
- PDF Report generation
- Real-time analytics
- Auto-submit & Auto-save
- Historical tracking

Run with: streamlit run app.py
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import time

# Conditional imports for Phase 3 features
try:
    import plotly.graph_objects as go
    import pandas as pd
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly not installed. Analytics charts will be disabled. Run: pip install plotly pandas")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.checkpoint import Checkpoint
from src.models.state import create_initial_state
from src.graph.learning_graph import LearningGraph
from src.utils.pdf_generator import LearningReportGenerator
from src.utils.database_manager import SessionDatabase

# Page configuration
st.set_page_config(
    page_title="Autonomous Learning Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .checkpoint-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .question-box {
        background-color: #ffffff;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .score-pass {
        color: #28a745;
        font-weight: bold;
        font-size: 1.8rem;
    }
    .score-fail {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.8rem;
    }
    .feynman-box {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #ffc107;
        margin: 1rem 0;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.checkpoints = []
        st.session_state.user_notes = ""
        st.session_state.current_checkpoint_index = 0
        st.session_state.stage = "setup"
        st.session_state.learning_graph = None
        st.session_state.state = None
        st.session_state.questions = []
        st.session_state.answers = {}
        st.session_state.score = None
        st.session_state.passed = False
        st.session_state.feynman_explanations = []
        st.session_state.completed_checkpoints = []
        st.session_state.attempt_count = 0
        
        # Phase 1-3: Enhanced features
        st.session_state.session_start_time = None
        st.session_state.checkpoint_start_time = None
        st.session_state.checkpoint_history = []  # Track all checkpoint data for PDF
        st.session_state.auto_submit_enabled = True
        st.session_state.auto_feynman = True  # Auto-trigger Feynman
        st.session_state.analytics_data = {
            'scores': [],
            'times': [],
            'topics': []
        }
        
        # Initialize database
        try:
            st.session_state.db = SessionDatabase()
        except Exception:
            st.session_state.db = None

init_session_state()

def setup_page():
    """Setup page for configuring learning path."""
    st.markdown('<h1 class="main-header">🎓 Autonomous Learning Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;"></p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📚 Configure Your Learning Journey")
        st.write("Set up your learning path with multiple checkpoints. The system will guide you through each topic, assess your understanding, and provide Feynman-style explanations when needed.")
    
    with col2:
        st.info("""
        **Key Features:**
        - Multiple checkpoints
        - Real-time assessment
        - Feynman teaching
        - Progress tracking
        """)
    
    st.markdown("---")
    
    # Predefined templates
    st.subheader("🎯 Quick Start Templates")
    
    template_col1, template_col2, template_col3 = st.columns(3)
    
    with template_col1:
        if st.button("📘 Python Basics (2 topics)", use_container_width=True):
            apply_template("python_basics")
            return
    
    with template_col2:
        if st.button("🔧 Python Advanced (3 topics)", use_container_width=True):
            apply_template("python_advanced")
            return
    
    with template_col3:
        if st.button("⚙️ Custom Setup", use_container_width=True):
            st.session_state.custom_setup = True
    
    # Custom setup
    if st.session_state.get('custom_setup', False):
        st.markdown("---")
        st.subheader("✏️ Custom Checkpoint Configuration")
        
        num_checkpoints = st.number_input(
            "Number of Checkpoints",
            min_value=1,
            max_value=5,
            value=2,
            help="How many topics to learn in this session"
        )
        
        checkpoints = []
        for i in range(num_checkpoints):
            with st.expander(f"📖 Checkpoint {i+1}", expanded=(i==0)):
                topic = st.text_input(
                    f"Topic",
                    value=f"Topic {i+1}",
                    key=f"topic_{i}"
                )
                
                objectives_text = st.text_area(
                    f"Learning Objectives (one per line)",
                    value=f"Understand {topic.lower()} basics\nLearn {topic.lower()} syntax",
                    key=f"objectives_{i}",
                    height=80
                )
                
                objectives = [obj.strip() for obj in objectives_text.split('\n') if obj.strip()]
                
                checkpoints.append(Checkpoint(
                    topic=topic,
                    objectives=objectives,
                    difficulty_level="beginner"
                ))
        
        # User notes
        st.subheader("📝 Learning Materials (Optional)")
        user_notes = st.text_area(
            "Provide your own notes or leave empty to use web search",
            value="",
            height=150,
            placeholder="Enter your learning materials here..."
        )
        
        # Start button
        if st.button("🚀 Start Learning Journey", type="primary", use_container_width=True):
            start_learning(checkpoints, user_notes)

def apply_template(template_name):
    """Apply a predefined template."""
    if template_name == "python_basics":
        checkpoints = [
            Checkpoint(
                topic="Python Functions and Parameters",
                objectives=[
                    "Understand function definition syntax",
                    "Learn how to use function parameters",
                    "Master return values and function calls"
                ],
                difficulty_level="beginner"
            ),
            Checkpoint(
                topic="Python Lists and Iteration",
                objectives=[
                    "Understand list data structure",
                    "Learn list methods and operations",
                    "Master list iteration with loops"
                ],
                difficulty_level="beginner"
            )
        ]
        user_notes = """Functions in Python are defined using the 'def' keyword.
They can take parameters and return values.
Example: def greet(name): return f"Hello {name}"

Lists in Python are ordered, mutable collections.
Created with square brackets: [1, 2, 3]
Common methods include append(), remove(), sort()."""
        
    elif template_name == "python_advanced":
        checkpoints = [
            Checkpoint(
                topic="Python Functions",
                objectives=[
                    "Understand function definition and parameters",
                    "Master return values"
                ],
                difficulty_level="beginner"
            ),
            Checkpoint(
                topic="Python Lists",
                objectives=[
                    "Understand list data structure",
                    "Learn list methods"
                ],
                difficulty_level="beginner"
            ),
            Checkpoint(
                topic="Python Dictionaries",
                objectives=[
                    "Understand dictionary key-value pairs",
                    "Learn dictionary methods"
                ],
                difficulty_level="beginner"
            )
        ]
        user_notes = """Python Functions: def keyword, parameters, return values
Python Lists: ordered collections, [1,2,3], methods like append()
Python Dictionaries: key-value pairs, {'key': 'value'}, methods like keys()"""
    
    start_learning(checkpoints, user_notes)

def start_learning(checkpoints, user_notes):
    """Initialize learning session with time tracking (Phase 2)."""
    st.session_state.checkpoints = checkpoints
    st.session_state.user_notes = user_notes if user_notes and user_notes.strip() else None
    st.session_state.stage = "learning"
    st.session_state.current_checkpoint_index = 0
    st.session_state.completed_checkpoints = []
    st.session_state.attempt_count = 0
    
    # PHASE 2: Start time tracking
    st.session_state.session_start_time = datetime.now()
    st.session_state.checkpoint_start_time = time.time()
    st.session_state.checkpoint_history = []
    st.session_state.analytics_data = {'scores': [], 'times': [], 'topics': []}
    
    st.rerun()

def process_checkpoint():
    """Process current checkpoint through the workflow."""
    if st.session_state.learning_graph is None:
        with st.spinner("🔧 Initializing learning system..."):
            st.session_state.learning_graph = LearningGraph(force_poor_answers=False)
            st.session_state.state = create_initial_state(
                checkpoints=st.session_state.checkpoints,
                user_notes=st.session_state.user_notes
            )
            st.session_state.state['current_checkpoint_index'] = st.session_state.current_checkpoint_index
    
    state = st.session_state.state
    graph = st.session_state.learning_graph
    
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    
    try:
        # Define checkpoint
        status_placeholder.info("📖 Defining checkpoint...")
        progress_bar.progress(20)
        state = graph.define_checkpoint_node(state)
        
        # Gather and validate context
        status_placeholder.info("🔍 Gathering learning materials...")
        progress_bar.progress(40)
        state = graph.gather_context_node(state)
        
        status_placeholder.info("✅ Validating content relevance...")
        progress_bar.progress(60)
        state = graph.validate_context_node(state)
        
        if not state.get('context_valid'):
            st.error("❌ Failed to gather sufficient context. Please check your internet connection.")
            return False
        
        # Process context
        status_placeholder.info("⚙️ Processing learning materials...")
        progress_bar.progress(80)
        state = graph.process_context_node(state)
        
        # Generate questions
        status_placeholder.info("📝 Generating assessment questions...")
        progress_bar.progress(100)
        state = graph.generate_questions_node(state)
        
        status_placeholder.success("✅ Ready for assessment!")
        
        st.session_state.state = state
        st.session_state.questions = state.get('questions', [])
        st.session_state.stage = "questions"
        return True
        
    except Exception as e:
        st.error(f"❌ Error processing checkpoint: {str(e)}")
        return False

def learning_page():
    """Main learning interface."""
    st.markdown('<h1 class="main-header">🎓 Learning in Progress</h1>', unsafe_allow_html=True)
    
    # Progress indicator
    total_checkpoints = len(st.session_state.checkpoints)
    current = st.session_state.current_checkpoint_index + 1
    completed = len(st.session_state.completed_checkpoints)
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        progress_value = completed / total_checkpoints if total_checkpoints > 0 else 0
        st.progress(progress_value)
    with col2:
        st.metric("Current", f"{current}/{total_checkpoints}")
    with col3:
        st.metric("Completed", completed)
    
    st.markdown("---")
    
    # Current checkpoint info
    checkpoint = st.session_state.checkpoints[st.session_state.current_checkpoint_index]
    
    st.markdown(f'<div class="checkpoint-card">', unsafe_allow_html=True)
    st.markdown(f"### 📖 Checkpoint {current}: {checkpoint.topic}")
    st.markdown("**🎯 Learning Objectives:**")
    for i, obj in enumerate(checkpoint.objectives, 1):
        st.markdown(f"{i}. {obj}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process checkpoint
    if process_checkpoint():
        st.rerun()

def questions_page():
    """Display questions and collect answers with auto-submit (Phase 2)."""
    st.markdown('<h1 class="main-header">📝 Assessment Time</h1>', unsafe_allow_html=True)
    
    checkpoint = st.session_state.checkpoints[st.session_state.current_checkpoint_index]
    current = st.session_state.current_checkpoint_index + 1
    total = len(st.session_state.checkpoints)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"**Checkpoint {current}/{total}**: {checkpoint.topic}")
    with col2:
        st.metric("Pass Threshold", "70%")
    
    st.markdown("---")
    
    # PHASE 2: Auto-submit toggle
    with st.expander("⚙️ Settings", expanded=False):
        st.session_state.auto_submit_enabled = st.checkbox(
            "Enable Auto-Submit (submit when all questions answered)",
            value=st.session_state.get('auto_submit_enabled', True)
        )
    
    st.markdown("### 💭 Answer the following questions:")
    
    questions = st.session_state.questions
    
    # Display questions and collect answers
    for i, q in enumerate(questions, 1):
        st.markdown(f'<div class="question-box">', unsafe_allow_html=True)
        st.markdown(f"**Question {i}** · `{q['difficulty'].upper()}`")
        st.markdown(f"{q['question']}")
        st.caption(f"🎯 Testing: {q['objective']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        answer = st.text_area(
            f"Your Answer",
            key=f"answer_{q['id']}",
            height=100,
            placeholder="Type your detailed answer here..."
        )
        
        st.session_state.answers[q['id']] = {
            "question_id": q['id'],
            "answer": answer,
            "objective": q['objective']
        }
        
        if i < len(questions):
            st.markdown("---")
    
    st.markdown("")
    
    # Check if all answered for auto-submit
    all_answered = all(st.session_state.answers.get(q['id'], {}).get('answer', '').strip() for q in questions)
    
    # PHASE 2: Auto-submit indicator
    if all_answered and st.session_state.auto_submit_enabled:
        st.success("✅ All questions answered! Auto-submitting...")
        time.sleep(0.5)  # Brief pause for UX
        with st.spinner("🤔 Evaluating your answers..."):
            evaluate_answers()
        st.rerun()
    
    # Manual submit button
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        if st.button("✅ Submit Answers", type="primary", use_container_width=True, disabled=(all_answered and st.session_state.auto_submit_enabled)):
            if all_answered:
                with st.spinner("🤔 Evaluating your answers..."):
                    evaluate_answers()
                st.rerun()
            else:
                st.warning("⚠️ Please answer all questions before submitting.")
    
    # Progress indicator
    answered_count = sum(1 for q in questions if st.session_state.answers.get(q['id'], {}).get('answer', '').strip())
    st.progress(answered_count / len(questions), text=f"Progress: {answered_count}/{len(questions)} questions answered")

def evaluate_answers():
    """Evaluate learner's answers."""
    state = st.session_state.state
    graph = st.session_state.learning_graph
    
    # Convert answers dict to list
    answers_list = [st.session_state.answers[q['id']] for q in st.session_state.questions]
    state['answers'] = answers_list
    
    # Verify understanding
    state = graph.verify_understanding_node(state)
    
    st.session_state.state = state
    st.session_state.score = state.get('understanding_score', 0.0)
    st.session_state.passed = state.get('passed_checkpoint', False)
    st.session_state.stage = "results"

def results_page():
    """Display assessment results with auto-Feynman trigger (Phase 1)."""
    st.markdown('<h1 class="main-header">📊 Assessment Results</h1>', unsafe_allow_html=True)
    
    checkpoint = st.session_state.checkpoints[st.session_state.current_checkpoint_index]
    score = st.session_state.score
    passed = st.session_state.passed
    
    # Save checkpoint data for PDF/analytics
    save_checkpoint_data()
    
    st.markdown("---")
    
    # Display score
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        score_class = "score-pass" if passed else "score-fail"
        st.markdown(f'<div style="text-align: center;"><p class="{score_class}">{score:.1%}</p></div>', unsafe_allow_html=True)
        
        if passed:
            st.success("### ✅ PASSED! You've mastered this checkpoint!")
            st.balloons()
        else:
            st.error("### ❌ Below 70% - Activating Feynman Teaching...")
            
            # PHASE 1: AUTO-TRIGGER FEYNMAN
            if st.session_state.auto_feynman and st.session_state.attempt_count == 0:
                with st.spinner("🧠 Automatically generating simplified explanations..."):
                    time.sleep(1)  # Brief pause for UX
                    apply_feynman_teaching()
                st.rerun()
    
    st.markdown("---")
    
    # Show individual question results
    with st.expander("📋 View Detailed Question Breakdown", expanded=False):
        questions = st.session_state.questions
        answers = [st.session_state.answers[q['id']] for q in questions]
        
        for i, q in enumerate(questions):
            st.markdown(f"**Question {i+1}:** {q['question'][:80]}...")
            st.markdown(f"**Your Answer:** {answers[i]['answer'][:200]}...")
            st.markdown(f"**Objective:** {q['objective']}")
            st.markdown("---")
    
    # Show analytics
    if len(st.session_state.analytics_data['scores']) > 0:
        show_analytics_dashboard()
    
    st.markdown("---")
    
    # Action buttons
    st.markdown("### 🎯 What's Next?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not passed and st.session_state.attempt_count > 0:
            # Manual Feynman button only after first auto-trigger
            if st.button("📖 Review Feynman Again", type="secondary", use_container_width=True):
                st.session_state.stage = "feynman"
                st.rerun()
    
    with col2:
        if passed:
            if st.button("➡️ Continue to Next Checkpoint", type="primary", use_container_width=True):
                move_to_next_checkpoint()
                st.rerun()
        else:
            if st.session_state.attempt_count >= 2:
                if st.button("➡️ Move to Next Checkpoint", type="primary", use_container_width=True):
                    st.warning("Moving on after attempts. You can review this topic later.")
                    move_to_next_checkpoint()
                    st.rerun()

def apply_feynman_teaching():
    """Apply Feynman teaching for weak concepts."""
    state = st.session_state.state
    graph = st.session_state.learning_graph
    
    # Apply Feynman teaching
    state = graph.feynman_teaching_node(state)
    
    st.session_state.state = state
    st.session_state.feynman_explanations = state.get('feynman_explanations', [])
    st.session_state.stage = "feynman"

def feynman_page():
    """Display Feynman teaching with intelligent retry (Phase 2)."""
    st.markdown('<h1 class="main-header">🎓 Feynman Teaching</h1>', unsafe_allow_html=True)
    
    st.info("""
    **The Feynman Technique**: Learning through simplification and analogy.  
    We'll break down complex concepts into simpler terms to help you understand better.
    """)
    
    st.markdown("---")
    
    explanations = st.session_state.feynman_explanations
    
    if explanations:
        for i, exp in enumerate(explanations, 1):
            st.markdown(f'<div class="feynman-box">', unsafe_allow_html=True)
            st.markdown(f"### 💡 Concept {i}: {exp['concept']}")
            st.markdown(exp['explanation'])
            st.markdown('</div>', unsafe_allow_html=True)
            if i < len(explanations):
                st.markdown("")
    else:
        st.warning("No explanations available. Please try the assessment again.")
    
    st.markdown("---")
    
    # PHASE 2: Intelligent retry with auto-regeneration toggle
    with st.expander("⚙️ Retry Options", expanded=True):
        auto_retry = st.checkbox(
            "Auto-generate new questions (recommended)",
            value=True,
            help="Automatically generate fresh questions when retrying"
        )
    
    # Try again button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Try New Questions", type="primary", use_container_width=True):
            # Reset for new attempt with auto-retry
            st.session_state.answers = {}
            st.session_state.attempt_count += 1
            if auto_retry:
                st.session_state.questions = []  # Force regeneration
                with st.spinner("🔄 Generating new questions for you..."):
                    time.sleep(1)
            st.session_state.stage = "learning"
            st.rerun()
    
    with col2:
        if st.button("➡️ Skip to Next Checkpoint", use_container_width=True):
            st.warning("Skipping this checkpoint. Consider reviewing the material later.")
            move_to_next_checkpoint()
            st.rerun()

def move_to_next_checkpoint():
    """Move to the next checkpoint with time reset (Phase 2)."""
    # Mark current as completed
    if st.session_state.current_checkpoint_index not in st.session_state.completed_checkpoints:
        st.session_state.completed_checkpoints.append(st.session_state.current_checkpoint_index)
    
    # Check if more checkpoints
    if st.session_state.current_checkpoint_index + 1 < len(st.session_state.checkpoints):
        st.session_state.current_checkpoint_index += 1
        st.session_state.state['current_checkpoint_index'] = st.session_state.current_checkpoint_index
        st.session_state.answers = {}
        st.session_state.attempt_count = 0
        st.session_state.feynman_explanations = []
        
        # PHASE 2: Reset checkpoint timer
        st.session_state.checkpoint_start_time = time.time()
        
        st.session_state.stage = "learning"
    else:
        st.session_state.stage = "complete"

def complete_page():
    """Completion page with PDF download and analytics (Phase 1-3)."""
    st.markdown('<h1 class="main-header">🎉 Congratulations!</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.3rem;">You have completed your learning journey!</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Celebration
    st.balloons()
    
    # Save to database
    save_to_database()
    
    # Summary statistics
    st.markdown("### 📊 Your Learning Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📚 Total Topics",
            len(st.session_state.checkpoints),
            help="Number of topics covered in this session"
        )
    
    with col2:
        st.metric(
            "✅ Completed",
            len(st.session_state.completed_checkpoints),
            help="Successfully completed checkpoints"
        )
    
    with col3:
        completion_rate = (len(st.session_state.completed_checkpoints) / len(st.session_state.checkpoints)) * 100
        st.metric(
            "🎯 Success Rate",
            f"{completion_rate:.0f}%",
            help="Overall completion percentage"
        )
    
    with col4:
        avg_score = sum(st.session_state.analytics_data['scores']) / len(st.session_state.analytics_data['scores']) if st.session_state.analytics_data['scores'] else 0
        st.metric(
            "📈 Avg Score",
            f"{avg_score:.1%}",
            help="Average score across all checkpoints"
        )
    
    st.markdown("---")
    
    # PHASE 1: PDF REPORT DOWNLOAD
    st.markdown("### 📄 Download Your Report")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📥 Generate & Download PDF Report", type="primary", use_container_width=True):
            with st.spinner("Generating comprehensive PDF report..."):
                pdf_buffer = generate_pdf_report()
                if pdf_buffer:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        label="💾 Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"learning_report_{timestamp}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("✅ PDF Report generated successfully!")
    
    st.markdown("---")
    
    # PHASE 3: ANALYTICS DASHBOARD
    if len(st.session_state.analytics_data['scores']) > 0:
        show_analytics_dashboard()
        st.markdown("---")
    
    # PHASE 3: HISTORICAL PERFORMANCE
    show_historical_performance()
    
    st.markdown("---")
    
    # Show all checkpoints
    st.markdown("### ✅ Topics Mastered")
    
    for idx in st.session_state.completed_checkpoints:
        checkpoint = st.session_state.checkpoints[idx]
        checkpoint_data = st.session_state.checkpoint_history[idx] if idx < len(st.session_state.checkpoint_history) else {}
        
        score_badge = f"🟢 {checkpoint_data.get('score', 0):.1%}" if checkpoint_data.get('passed', False) else f"🟡 {checkpoint_data.get('score', 0):.1%}"
        
        with st.expander(f"✓ {checkpoint.topic} {score_badge}", expanded=False):
            st.markdown("**Objectives Covered:**")
            for obj in checkpoint.objectives:
                st.markdown(f"- {obj}")
            if checkpoint_data.get('feynman_used', False):
                st.info("💡 Feynman Teaching was applied for this checkpoint")
    
    st.markdown("---")
    
    # Start over button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Start New Learning Journey", type="primary", use_container_width=True):
            # Reset everything
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ==================== PHASE 1-3 ENHANCEMENT FUNCTIONS ====================

def save_checkpoint_data():
    """Save current checkpoint data to history."""
    if st.session_state.score is not None:
        checkpoint_data = {
            'topic': st.session_state.checkpoints[st.session_state.current_checkpoint_index].topic,
            'subtopic': st.session_state.checkpoints[st.session_state.current_checkpoint_index].objectives[0] if st.session_state.checkpoints[st.session_state.current_checkpoint_index].objectives else '',
            'score': st.session_state.score,
            'passed': st.session_state.passed,
            'questions': st.session_state.questions,
            'answers': [st.session_state.answers[q['id']] for q in st.session_state.questions],
            'feynman_used': len(st.session_state.feynman_explanations) > 0,
            'feynman_explanations': st.session_state.feynman_explanations,
            'attempt_count': st.session_state.attempt_count,
            'time_spent': time.time() - st.session_state.checkpoint_start_time if st.session_state.checkpoint_start_time else 0
        }
        st.session_state.checkpoint_history.append(checkpoint_data)
        
        # Update analytics data
        st.session_state.analytics_data['scores'].append(st.session_state.score)
        st.session_state.analytics_data['times'].append(checkpoint_data['time_spent'])
        st.session_state.analytics_data['topics'].append(checkpoint_data['topic'])

def generate_pdf_report():
    """Generate and download PDF report."""
    try:
        # Prepare session data
        session_data = {
            'checkpoints': st.session_state.checkpoint_history,
            'overall_score': sum(st.session_state.analytics_data['scores']) / len(st.session_state.analytics_data['scores']) if st.session_state.analytics_data['scores'] else 0,
            'total_time': sum(st.session_state.analytics_data['times']),
            'completion_date': datetime.now(),
            'user_notes': st.session_state.user_notes,
            'feynman_used': any(cp.get('feynman_used', False) for cp in st.session_state.checkpoint_history)
        }
        
        # Generate PDF
        pdf_generator = LearningReportGenerator()
        pdf_buffer = pdf_generator.generate_report(session_data)
        
        return pdf_buffer
    except Exception as pdf_error:
        st.error(f"Error generating PDF: {str(pdf_error)}")
        return None

def save_to_database():
    """Save session to database for historical tracking."""
    if st.session_state.db:
        try:
            session_data = {
                'start_time': st.session_state.session_start_time,
                'end_time': datetime.now(),
                'total_time': sum(st.session_state.analytics_data['times']),
                'overall_score': sum(st.session_state.analytics_data['scores']) / len(st.session_state.analytics_data['scores']) if st.session_state.analytics_data['scores'] else 0,
                'checkpoints': st.session_state.checkpoint_history,
                'user_notes': st.session_state.user_notes
            }
            st.session_state.db.save_session(session_data)
        except Exception:
            pass  # Silent fail for database

def show_analytics_dashboard():
    """Display real-time analytics dashboard."""
    if not PLOTLY_AVAILABLE:
        return
        
    if len(st.session_state.analytics_data['scores']) > 0:
        st.markdown("### 📈 Real-Time Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Score progression chart
            fig_scores = go.Figure()
            fig_scores.add_trace(go.Scatter(
                x=list(range(1, len(st.session_state.analytics_data['scores']) + 1)),
                y=st.session_state.analytics_data['scores'],
                mode='lines+markers',
                name='Score',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=10)
            ))
            fig_scores.add_hline(y=0.7, line_dash="dash", line_color="green", annotation_text="Pass Threshold (70%)")
            fig_scores.update_layout(
                title="Score Progression",
                xaxis_title="Checkpoint",
                yaxis_title="Score",
                yaxis_tickformat='.0%',
                height=300
            )
            st.plotly_chart(fig_scores, use_container_width=True)
        
        with col2:
            # Time spent chart
            fig_time = go.Figure()
            fig_time.add_trace(go.Bar(
                x=st.session_state.analytics_data['topics'],
                y=[t/60 for t in st.session_state.analytics_data['times']],  # Convert to minutes
                marker_color='#ff7f0e'
            ))
            fig_time.update_layout(
                title="Time Spent per Checkpoint",
                xaxis_title="Topic",
                yaxis_title="Minutes",
                height=300
            )
            st.plotly_chart(fig_time, use_container_width=True)

def show_historical_performance():
    """Show historical performance from database."""
    if not PLOTLY_AVAILABLE or not st.session_state.db:
        return
        
    if st.session_state.db:
        try:
            history = st.session_state.db.get_session_history(limit=10)
            
            if history:
                st.markdown("### 📚 Historical Performance")
                
                # Convert to DataFrame
                df = pd.DataFrame(history)
                df['overall_score'] = df['overall_score'].apply(lambda x: f"{x:.1%}")
                df['start_time'] = pd.to_datetime(df['start_time']).dt.strftime('%Y-%m-%d %H:%M')
                
                st.dataframe(
                    df[['start_time', 'overall_score', 'checkpoints_count', 'passed_count']],
                    column_config={
                        'start_time': 'Date',
                        'overall_score': 'Score',
                        'checkpoints_count': 'Topics',
                        'passed_count': 'Passed'
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # Statistics
                stats = st.session_state.db.get_statistics()
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Sessions", stats['total_sessions'])
                with col2:
                    st.metric("Avg Score", f"{stats['avg_score']:.1%}")
                with col3:
                    st.metric("Total Hours", f"{stats['total_time_hours']:.1f}")
                with col4:
                    st.metric("Pass Rate", f"{stats['pass_rate']:.1%}")
        except Exception:
            pass  # Silent fail

# Sidebar
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    
    stage_icons = {
        "setup": "⚙️",
        "learning": "📚",
        "questions": "📝",
        "results": "📊",
        "feynman": "🎓",
        "complete": "🎉"
    }
    
    current_stage = st.session_state.stage
    st.markdown(f"**Current Stage:** {stage_icons.get(current_stage, '•')} {current_stage.replace('_', ' ').title()}")
    
    st.markdown("---")
    
    if st.session_state.checkpoints:
        st.markdown("### 📚 Checkpoints")
        for i, cp in enumerate(st.session_state.checkpoints):
            if i in st.session_state.completed_checkpoints:
                status = "✅"
                color = "#28a745"
            elif i == st.session_state.current_checkpoint_index:
                status = "🔄"
                color = "#1f77b4"
            else:
                status = "⏳"
                color = "#6c757d"
            
            st.markdown(f'<span style="color: {color};">{status} {cp.topic}</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### ℹ️ Agent Features")
    st.markdown("""
    **Features Demonstrated:**
    - ✓ Multiple sequential checkpoints
    - ✓ Adaptive Feynman teaching
    - ✓ Real-time assessment (70% threshold)
    - ✓ Progress tracking
    - ✓ User answer collection
    - ✓ Seamless state transfer
    """)
    
    st.markdown("---")
    
    if st.button("🏠 Back to Setup", use_container_width=True):
        if st.session_state.stage != "setup":
            if st.checkbox("Confirm reset (lose progress)"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

# Main content router
if st.session_state.stage == "setup":
    setup_page()
elif st.session_state.stage == "learning":
    learning_page()
elif st.session_state.stage == "questions":
    questions_page()
elif st.session_state.stage == "results":
    results_page()
elif st.session_state.stage == "feynman":
    feynman_page()
elif st.session_state.stage == "complete":
    complete_page()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>Autonomous Learning Agent | </p>
    <p>Built with LangGraph, LangChain, and Streamlit</p>
</div>
""", unsafe_allow_html=True)
