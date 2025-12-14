import streamlit as st
import time
from src.graph import build_graph
from src.models import LearningCheckpoint

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AI Tutor - Sequential Mode",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; color: #2E86C1; }
    .metric-box { padding: 10px; background-color: #f0f2f6; border-radius: 10px; text-align: center; }
    .stSuccess, .stError, .stWarning { padding: 15px; border-radius: 10px; border: 1px solid #ddd; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
# Logic: We need to store the LIST of objectives and which INDEX we are currently on.
if "checklist" not in st.session_state:
    st.session_state.checklist = []  # Stores ["Obj 1", "Obj 2", "Obj 3"]
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "agent_run_completed" not in st.session_state:
    st.session_state.agent_run_completed = False
if "final_state" not in st.session_state:
    st.session_state.final_state = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

# --- HEADER ---
st.title("AI Tutor: Sequential Mastery")
st.markdown("##### *Define a path. Master it one step at a time.*")
st.divider()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuration")
    st.success(f"Model Active: gpt-5-nano")
    with st.expander("Upload Notes (Optional)"):
        uploaded_file = st.file_uploader("Upload .txt file", type="txt")
        user_notes_text = uploaded_file.read().decode("utf-8") if uploaded_file else ""
    
    # Show Course Progress in Sidebar
    if st.session_state.checklist:
        st.markdown("### Course Map")
        for i, item in enumerate(st.session_state.checklist):
            if i < st.session_state.current_index:
                st.markdown(f"~~{item}~~")
            elif i == st.session_state.current_index:
                st.markdown(f"**{item}** (Current)")
            else:
                st.markdown(f"{item}")

# --- MAIN INPUT AREA (Only shows if course not started) ---
if not st.session_state.checklist:
    col1, col2 = st.columns([1, 2])
    with col1:
        topic_input = st.text_input("Main Topic", value="Photosynthesis", placeholder="e.g. Linear Algebra")
    with col2:
        # User enters COMMA SEPARATED list
        objectives_input = st.text_input("Objectives (Comma Separated)", value="Light-dependent reactions, Calvin cycle, ATP Synthase", placeholder="Step 1, Step 2, Step 3")

    if st.button("Generate Learning Path", type="primary"):
        if not topic_input or not objectives_input:
            st.error("Please provide both a Topic and Objectives.")
            st.stop()
        
        # 1. PARSE & STORE CHECKPOINTS
        raw_list = [obj.strip() for obj in objectives_input.split(",") if obj.strip()]
        st.session_state.checklist = raw_list
        st.session_state.topic = topic_input
        st.session_state.current_index = 0
        st.session_state.agent_run_completed = False # Reset run state
        st.rerun()

# --- ACTIVE COURSE VIEW ---
else:
    # Get current objective
    current_obj = st.session_state.checklist[st.session_state.current_index]
    total_steps = len(st.session_state.checklist)
    
    st.info(f"**Current Checkpoint ({st.session_state.current_index + 1}/{total_steps}):** {current_obj}")

    # --- AGENT TRIGGER (Auto-runs if not completed for this step) ---
    if not st.session_state.agent_run_completed:
        with st.status(f"Agent is researching '{current_obj}'...", expanded=True) as status:
            # Initialize State strictly for THIS single objective
            active_cp = LearningCheckpoint(
                topic=st.session_state.topic,
                objectives=[current_obj], # Single item list
                success_criteria=f"User must demonstrate understanding of {current_obj}."
            )
            
            initial_state = {
                "active_checkpoint": active_cp,
                "user_notes": user_notes_text,
                "retry_count": 0,
                "logs": [],
                "relevance_score": 0,
                "gathered_context": "",
                "feedback": "",
                "processed_context": [],
                "quiz_questions": []
            }

            graph = build_graph()
            current_state_buffer = {}

            for event in graph.stream(initial_state):
                for key, value in event.items():
                    if "relevance_score" in value: current_state_buffer["relevance_score"] = value["relevance_score"]
                    if "gathered_context" in value: current_state_buffer["gathered_context"] = value["gathered_context"]
                    if "feedback" in value: current_state_buffer["feedback"] = value["feedback"]
                    if "retry_count" in value: current_state_buffer["retry_count"] = value["retry_count"]
                    if "quiz_questions" in value: current_state_buffer["quiz_questions"] = value["quiz_questions"]
                    
                    if "logs" in value and value["logs"]:
                        if "logs" not in current_state_buffer: current_state_buffer["logs"] = []
                        current_state_buffer["logs"].extend(value["logs"])
                        for log in value["logs"]:
                            st.write(log)
                            if "Searching" in log: status.update(label="Searching Context...", state="running")
                            elif "Validation" in log: status.update(label="Validating Relevance...", state="running")
                            elif "Generating" in log: status.update(label="Creating Assessment...", state="running")

            status.update(label="Ready for Verification!", state="complete", expanded=False)
        
        # Save state & rerun to show interface
        st.session_state.final_state = current_state_buffer
        st.session_state.agent_run_completed = True
        st.rerun()

    # --- VERIFICATION INTERFACE ---
    if st.session_state.agent_run_completed:
        final_state = st.session_state.final_state
        quiz_data = final_state.get("quiz_questions", [])
        
        t1, t2 = st.tabs(["Assessment", "Study Material"])
        
        with t1:
            st.subheader(f"Checkpoint: {current_obj}")
            if not quiz_data:
                st.warning("No questions generated. Try refreshing.")
                if st.button("Retry Agent"):
                    st.session_state.agent_run_completed = False
                    st.rerun()
            else:
                with st.form("quiz_form"):
                    user_answers = {}
                    for idx, q in enumerate(quiz_data):
                        st.markdown(f"**Q{idx+1}: {q.get('question', 'Error')}**")
                        options = q.get('options', [])
                        user_answers[idx] = st.radio("Select answer:", options, key=f"q_{idx}_{st.session_state.current_index}", index=None, label_visibility="collapsed")
                        st.markdown("---")
                    
                    if st.form_submit_button("Submit & Verify"):
                        st.session_state.quiz_submitted = True
                
                # SCORING
                if st.session_state.quiz_submitted:
                    correct_count = 0
                    for idx, q in enumerate(quiz_data):
                        if user_answers.get(idx) == q.get('answer'): correct_count += 1
                    
                    score_pct = (correct_count / len(quiz_data)) * 100
                    st.metric("Score", f"{score_pct:.0f}%", delta="Threshold: 70%")
                    
                    if score_pct >= 70:
                        st.balloons()
                        st.success(f"PASSED! You have mastered '{current_obj}'.")
                        
                        # --- THE PROGRESSION LOGIC (Milestone 4 Logic) ---
                        if st.session_state.current_index < len(st.session_state.checklist) - 1:
                            if st.button(f"Proceed to Next: {st.session_state.checklist[st.session_state.current_index + 1]}", type="primary"):
                                st.session_state.current_index += 1
                                st.session_state.agent_run_completed = False # Reset for next step
                                st.session_state.quiz_submitted = False
                                st.rerun()
                        else:
                            st.success("COURSE COMPLETE! You have mastered all objectives.")
                            if st.button("Start New Topic"):
                                st.session_state.clear()
                                st.rerun()
                    else:
                        st.error("HALT: Score below 70%. Review the material and try again.")
                        # Reset quiz button (Logic for retaking)
                        if st.button("🔄 Retake Quiz"):
                            st.session_state.quiz_submitted = False
                            st.rerun()

        with t2:
            st.markdown(f"### Notes: {current_obj}")
            st.markdown(final_state.get("gathered_context", "No context."))
            st.divider()
            st.caption("Logs:")
            st.text("\n".join(final_state.get("logs", [])))