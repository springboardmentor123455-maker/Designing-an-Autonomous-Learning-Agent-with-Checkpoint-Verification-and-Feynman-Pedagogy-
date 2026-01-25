import os
import streamlit as st
from core.tutor_engine import TutorEngine
from core.pdf_processor import extract_text_from_pdf

# Set page config
st.set_page_config(
    page_title="AI Tutor Pro",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        color: #4F46E5;
        text-align: center;
        padding: 20px;
    }
    .module-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .lesson-content {
        background-color: white;
        border-radius: 10px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        line-height: 1.8;
        font-size: 16px;
    }
    .lesson-content h2 {
        color: #4F46E5;
        border-bottom: 2px solid #4F46E5;
        padding-bottom: 10px;
    }
    .lesson-content h3 {
        color: #7C3AED;
        margin-top: 25px;
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        height: 50px;
    }
    .quiz-question {
        background-color: #f8f9fa;
        border-left: 4px solid #4F46E5;
        padding: 20px;
        margin: 15px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session():
    """Initialize session state"""
    if 'engine' not in st.session_state:
        st.session_state.engine = None
    if 'doc_text' not in st.session_state:
        st.session_state.doc_text = ""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = "setup"
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    if 'feynman_explanation' not in st.session_state:
        st.session_state.feynman_explanation = ""
    if 'lesson_generated' not in st.session_state:
        st.session_state.lesson_generated = False

def render_sidebar():
    """Render sidebar"""
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # API Key
        api_key = st.text_input(
            "HuggingFace API Key",
            type="password",
            help="Get from huggingface.co/settings/tokens",
            value=st.session_state.get('api_key', '')
        )
        
        if api_key:
            st.session_state.api_key = api_key
            if not st.session_state.engine:
                st.session_state.engine = TutorEngine(api_key)
        
        st.divider()
        
        # File Upload
        uploaded_file = st.file_uploader(
            "📁 Upload Notes (PDF)",
            type=['pdf'],
            help="Optional: Upload your study materials"
        )
        
        if uploaded_file:
            with st.spinner("Processing PDF..."):
                st.session_state.doc_text = extract_text_from_pdf(uploaded_file)
                st.success("PDF loaded!")
        
        st.divider()
        
        # Progress
        if st.session_state.engine and hasattr(st.session_state.engine.session, 'study_plan'):
            completed = st.session_state.engine.session.modules_completed
            total = len(st.session_state.engine.session.study_plan)
            st.metric("Modules", f"{completed}/{total}")
            
            if completed > 0:
                st.progress(completed / total)
        
        st.divider()
        
        # Reset button
        if st.button("🔄 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def render_setup_view():
    """Render setup view"""
    st.markdown("<h1 class='main-header'>🎓 AI Tutor Pro</h1>", unsafe_allow_html=True)
    st.markdown("### What would you like to learn today?")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        topic = st.text_input(
            "Enter topic",
            placeholder="e.g., Deep Learning, Quantum Computing, Data Structures...",
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("Generate Plan", type="primary", use_container_width=True):
            if not topic:
                st.error("Please enter a topic")
                return
            
            if not st.session_state.get('api_key'):
                st.error("Please enter your HuggingFace API key in the sidebar")
                return
            
            if not st.session_state.engine:
                st.session_state.engine = TutorEngine(st.session_state.api_key)
            
            with st.spinner("Creating your personalized learning path..."):
                st.session_state.engine.start_new_session(topic, st.session_state.doc_text)
                st.session_state.current_step = "plan"
                st.rerun()

def render_plan_view():
    """Render study plan view"""
    engine = st.session_state.engine
    
    if not engine or not engine.session.study_plan:
        st.error("No study plan found. Please go back to setup.")
        if st.button("Back to Setup"):
            st.session_state.current_step = "setup"
            st.rerun()
        return
    
    st.title(f"📚 Learning Path: {engine.session.topic}")
    
    for module in engine.session.study_plan:
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div class='module-card'>
                    <h3>Module {module['id']}: {module['title']}</h3>
                    <p><strong>Objective:</strong> {module['objective']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                status = ""
                if module['id'] <= engine.session.modules_completed:
                    status = "✅ Completed"
                    btn_text = "Review"
                    btn_disabled = False
                elif module['id'] == engine.session.modules_completed + 1:
                    status = "▶️ Next"
                    btn_text = "Start"
                    btn_disabled = False
                else:
                    status = "🔒 Locked"
                    btn_text = "Locked"
                    btn_disabled = True
                
                st.write(f"**{status}**")
                
                if not btn_disabled:
                    if st.button(btn_text, key=f"btn_{module['id']}", use_container_width=True):
                        if engine.start_module(module['id']):
                            st.session_state.current_step = "study"
                            st.session_state.lesson_generated = False
                            st.rerun()
                else:
                    st.button(btn_text, key=f"btn_{module['id']}", disabled=True, use_container_width=True)
            
            st.divider()

def render_study_view():
    """Render study view"""
    engine = st.session_state.engine
    
    if not engine or not engine.session.current_module:
        st.error("No module selected")
        st.session_state.current_step = "plan"
        st.rerun()
        return
    
    module = engine.session.current_module
    
    st.title(f"📖 Module {module['id']}: {module['title']}")
    st.markdown(f"**Objective:** {module['objective']}")
    
    # Check if lesson needs to be generated
    if not engine.session.lesson_content or not st.session_state.lesson_generated:
        with st.spinner("Generating lesson content... This may take a minute."):
            lesson = engine.generate_lesson()
            if lesson and "Error" not in lesson:
                st.success("✅ Lesson generated successfully!")
                st.session_state.lesson_generated = True
                st.rerun()  # Rerun to display the lesson
            else:
                st.error("Failed to generate lesson. Please try again.")
                return
    
    # Display lesson with proper formatting
    st.markdown("---")
    
    # Create tabs for better organization
    tab1, tab2 = st.tabs(["📚 Lesson Content", "📝 Summary"])
    
    with tab1:
        # Display the lesson content with proper formatting
        st.markdown(f"""
        <div class='lesson-content'>
            {engine.session.lesson_content}
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        # Generate a summary
        with st.spinner("Generating summary..."):
            summary = _generate_summary(engine.session.lesson_content)
            st.markdown(summary)
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back to Plan"):
            st.session_state.current_step = "plan"
            st.session_state.lesson_generated = False
            st.rerun()
    
    with col2:
        st.write("")  # Spacer
    
    with col3:
        if st.button("Take Quiz →", type="primary"):
            st.session_state.current_step = "quiz"
            st.rerun()

def _generate_summary(lesson_content):
    """Generate a summary of the lesson"""
    if len(lesson_content) > 500:
        # Take first 500 characters and last 500 characters
        summary = lesson_content[:500] + "...\n\n**Key Points:**\n\n" + lesson_content[-500:]
        return summary
    return lesson_content

def render_quiz_view():
    """Render quiz view"""
    engine = st.session_state.engine
    
    if not engine or not engine.session.current_module:
        st.error("No module selected")
        st.session_state.current_step = "plan"
        st.rerun()
        return
    
    # Generate quiz questions if not already generated
    if not engine.session.quiz_questions:
        with st.spinner("Generating quiz questions..."):
            questions = engine.generate_quiz()
            if not questions:
                st.error("Failed to generate quiz")
                return
    
    st.title(f"🧠 Quiz: {engine.session.current_module['title']}")
    st.info("Answer all 5 questions to test your understanding.")
    
    # Collect answers
    with st.form("quiz_form"):
        st.session_state.user_answers = []
        
        for i, question in enumerate(engine.session.quiz_questions):
            st.markdown(f"""
            <div class='quiz-question'>
                <h4>Question {i+1}/5</h4>
                <p>{question}</p>
            </div>
            """, unsafe_allow_html=True)
            
            answer = st.text_area(
                f"Your answer:",
                key=f"answer_{i}",
                height=150,
                placeholder="Type your answer here...",
                label_visibility="collapsed"
            )
            st.session_state.user_answers.append(answer)
            st.markdown("---")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.form_submit_button("← Back to Lesson"):
                st.session_state.current_step = "study"
                st.rerun()
        
        with col2:
            submitted = st.form_submit_button("✅ Submit Answers", type="primary")
            
            if submitted:
                # Check if all answers are filled
                if all(a.strip() for a in st.session_state.user_answers):
                    with st.spinner("Grading your answers..."):
                        results = engine.grade_quiz(st.session_state.user_answers)
                        st.session_state.quiz_results = results
                        
                        if results.get('passed', False):
                            st.session_state.current_step = "results"
                        else:
                            # Get failed concepts
                            failed_concepts = engine.get_failed_concepts()
                            if failed_concepts:
                                with st.spinner("Preparing simplified explanation..."):
                                    explanation = engine.generate_feynman_explanation(failed_concepts)
                                    st.session_state.feynman_explanation = explanation
                            st.session_state.current_step = "results"
                        st.rerun()
                else:
                    st.warning("⚠️ Please answer all questions before submitting.")

def render_results_view():
    """Render results view"""
    engine = st.session_state.engine
    
    if not engine or not st.session_state.quiz_results:
        st.error("No quiz results found")
        st.session_state.current_step = "quiz"
        st.rerun()
        return
    
    results = st.session_state.quiz_results
    
    # Header with score
    score = results.get('total_score', 0)
    passed = results.get('passed', False)
    
    if passed:
        st.balloons()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.success(f"""
            # 🎉 Congratulations!
            ### You scored: **{score}%**
            ### Status: **PASSED** ✅
            """)
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.warning(f"""
            # 📝 Quiz Results
            ### Score: **{score}%**
            ### Status: **NEEDS IMPROVEMENT** ⚠️
            """)
    
    st.markdown("---")
    
    # Detailed feedback
    with st.expander("📋 View Detailed Feedback", expanded=True):
        feedback_list = results.get('feedback', [])
        
        if feedback_list:
            for i, feedback in enumerate(feedback_list):
                st.markdown(f"### Question {i+1}:")
                st.markdown(f"**Question:** {engine.session.quiz_questions[i] if i < len(engine.session.quiz_questions) else 'N/A'}")
                st.markdown(f"**Your Answer:** {st.session_state.user_answers[i] if i < len(st.session_state.user_answers) else 'N/A'}")
                st.markdown(f"**Feedback:** {feedback}")
                st.markdown("---")
        else:
            st.info("No detailed feedback available.")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 Review Lesson"):
            st.session_state.current_step = "study"
            st.rerun()
    
    with col2:
        if passed:
            if st.button("➡️ Next Module", type="primary"):
                st.session_state.current_step = "plan"
                st.session_state.lesson_generated = False
                st.session_state.user_answers = []
                st.session_state.quiz_results = None
                st.rerun()
        else:
            if st.button("🎯 Get Help", type="primary"):
                st.session_state.current_step = "feynman"
                st.rerun()
    
    with col3:
        if st.button("🔄 Retry Quiz"):
            # Clear previous quiz data
            engine.session.quiz_questions = []
            engine.session.user_answers = []
            engine.session.quiz_results = None
            st.session_state.user_answers = []
            st.session_state.quiz_results = None
            st.session_state.feynman_explanation = ""
            st.session_state.current_step = "quiz"
            st.rerun()

def render_feynman_view():
    """Render Feynman explanation view"""
    if not st.session_state.feynman_explanation:
        st.error("No explanation available")
        st.session_state.current_step = "results"
        st.rerun()
        return
    
    st.title("🎯 Simplified Explanation")
    st.info("Here's a simpler way to understand the concepts you missed:")
    
    # Display explanation in a nice box
    st.markdown("---")
    st.markdown(f"""
    <div style='
        background-color: #f0f9ff;
        border-radius: 10px;
        padding: 30px;
        margin: 20px 0;
        border-left: 5px solid #3b82f6;
    '>
        {st.session_state.feynman_explanation}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Results"):
            st.session_state.current_step = "results"
            st.rerun()
    
    with col2:
        if st.button("📚 Review Lesson Again"):
            st.session_state.current_step = "study"
            st.rerun()
    
    with col3:
        if st.button("🔄 Try Quiz Again", type="primary"):
            # Clear previous quiz data
            engine = st.session_state.engine
            if engine:
                engine.session.quiz_questions = []
                engine.session.user_answers = []
                engine.session.quiz_results = None
            st.session_state.user_answers = []
            st.session_state.quiz_results = None
            st.session_state.feynman_explanation = ""
            st.session_state.current_step = "quiz"
            st.rerun()

def main():
    """Main application"""
    # Initialize session
    initialize_session()
    
    # Render sidebar
    render_sidebar()
    
    # Render main content based on current step
    current_step = st.session_state.current_step
    
    if current_step == "setup":
        render_setup_view()
    elif current_step == "plan":
        render_plan_view()
    elif current_step == "study":
        render_study_view()
    elif current_step == "quiz":
        render_quiz_view()
    elif current_step == "results":
        render_results_view()
    elif current_step == "feynman":
        render_feynman_view()

if __name__ == "__main__":
    main()
    def show_status_indicator():
    
      col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        if st.session_state.get('api_status', 'unknown') == 'loading':
            st.warning("🔄 AI Model is loading... Please wait 30-60 seconds.")
            st.progress(0.5)
        elif st.session_state.get('api_status', 'unknown') == 'rate_limit':
            st.error("⚠️ Rate limit reached. Please wait 1 minute.")
        elif st.session_state.get('api_status', 'unknown') == 'ready':
            st.success("✅ AI Ready")
        else:
            st.info("⏳ Waiting for API key...")