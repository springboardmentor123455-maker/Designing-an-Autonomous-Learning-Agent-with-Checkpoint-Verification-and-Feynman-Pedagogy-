import streamlit as st
import time
from src.graph import build_graph
from src.models import LearningCheckpoint
from src.subjective_evaluator import evaluate_subjective_answers
from src.feyman_instructor import identify_knowledge_gaps, generate_feynman_explanation, format_feynman_for_display

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
    .study-material { 
        background-color: #f8f9fa; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #2E86C1;
        line-height: 1.6;
    }
    .feynman-box {
        background-color: #fff4e6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff9800;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "checklist" not in st.session_state:
    st.session_state.checklist = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "agent_run_completed" not in st.session_state:
    st.session_state.agent_run_completed = False
if "final_state" not in st.session_state:
    st.session_state.final_state = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "assessment_type" not in st.session_state:
    st.session_state.assessment_type = None
if "subjective_evaluation" not in st.session_state:
    st.session_state.subjective_evaluation = None
if "show_feynman" not in st.session_state:
    st.session_state.show_feynman = False
if "feynman_explanation" not in st.session_state:
    st.session_state.feynman_explanation = ""
if "feynman_attempt_count" not in st.session_state:
    st.session_state.feynman_attempt_count = 0
if "knowledge_gaps" not in st.session_state:
    st.session_state.knowledge_gaps = []

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
    
    if st.session_state.checklist:
        st.markdown("### Course Map")
        for i, item in enumerate(st.session_state.checklist):
            if i < st.session_state.current_index:
                st.markdown(f"~~{item}~~")
            elif i == st.session_state.current_index:
                st.markdown(f"**{item}** (Current)")
            else:
                st.markdown(f"{item}")
        
        # Show Feynman attempt count if active
        if st.session_state.feynman_attempt_count > 0:
            st.info(f"📚 Feynman Explanations: {st.session_state.feynman_attempt_count}")

# --- MAIN INPUT AREA ---
if not st.session_state.checklist:
    col1, col2 = st.columns([1, 2])
    with col1:
        topic_input = st.text_input("Main Topic", value="Photosynthesis", placeholder="e.g. Linear Algebra")
    with col2:
        objectives_input = st.text_input("Objectives (Comma Separated)", value="Light-dependent reactions, Calvin cycle, ATP Synthase", placeholder="Step 1, Step 2, Step 3")

    if st.button("Generate Learning Path", type="primary"):
        if not topic_input or not objectives_input:
            st.error("Please provide both a Topic and Objectives.")
            st.stop()
        
        raw_list = [obj.strip() for obj in objectives_input.split(",") if obj.strip()]
        st.session_state.checklist = raw_list
        st.session_state.topic = topic_input
        st.session_state.current_index = 0
        st.session_state.agent_run_completed = False
        st.session_state.assessment_type = None
        st.session_state.feynman_attempt_count = 0
        st.rerun()

# --- ACTIVE COURSE VIEW ---
else:
    current_obj = st.session_state.checklist[st.session_state.current_index]
    total_steps = len(st.session_state.checklist)
    
    st.info(f"**Current Checkpoint ({st.session_state.current_index + 1}/{total_steps}):** {current_obj}")

    # --- AGENT RUNS ONCE TO GATHER & FORMAT CONTEXT ---
    if not st.session_state.agent_run_completed:
        with st.status(f"Researching '{current_obj}'...", expanded=True) as status:
            active_cp = LearningCheckpoint(
                topic=st.session_state.topic,
                objectives=[current_obj],
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
                "formatted_content": "",
                "processed_context": []
            }

            graph = build_graph()
            current_state_buffer = {}

            for event in graph.stream(initial_state):
                for key, value in event.items():
                    if "relevance_score" in value: current_state_buffer["relevance_score"] = value["relevance_score"]
                    if "gathered_context" in value: current_state_buffer["gathered_context"] = value["gathered_context"]
                    if "formatted_content" in value: current_state_buffer["formatted_content"] = value["formatted_content"]
                    if "feedback" in value: current_state_buffer["feedback"] = value["feedback"]
                    if "retry_count" in value: current_state_buffer["retry_count"] = value["retry_count"]
                    if "processed_context" in value: current_state_buffer["processed_context"] = value["processed_context"]
                    
                    if "logs" in value and value["logs"]:
                        if "logs" not in current_state_buffer: current_state_buffer["logs"] = []
                        current_state_buffer["logs"].extend(value["logs"])
                        for log in value["logs"]:
                            st.write(log)
                            if "Searching" in log: status.update(label="🔍 Searching Context...", state="running")
                            elif "Validation" in log: status.update(label="✅ Validating Relevance...", state="running")
                            elif "Formatting" in log: status.update(label="📝 Formatting Content...", state="running")
                            elif "Processing" in log: status.update(label="🔧 Processing for Questions...", state="running")

            status.update(label="Study Material Ready!", state="complete", expanded=False)
        
        st.session_state.final_state = current_state_buffer
        st.session_state.agent_run_completed = True
        st.rerun()

    # --- DISPLAY FORMATTED STUDY MATERIAL ---
    if st.session_state.agent_run_completed:
        final_state = st.session_state.final_state
        
        st.markdown(f"### 📚 Study Material: {current_obj}")
        
        # Show formatted content in a nice box
        formatted_material = final_state.get("formatted_content", final_state.get("gathered_context", "No content available."))
        
        with st.container():
            st.markdown('<div class="study-material">', unsafe_allow_html=True)
            st.markdown(formatted_material)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # --- DISPLAY FEYNMAN EXPLANATION IF AVAILABLE ---
        if st.session_state.show_feynman and st.session_state.feynman_explanation:
            st.divider()
            with st.container():
                st.markdown('<div class="feynman-box">', unsafe_allow_html=True)
                st.markdown(format_feynman_for_display(
                    st.session_state.feynman_explanation,
                    st.session_state.feynman_attempt_count
                ))
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()

        # --- ASSESSMENT TYPE SELECTION ---
        if st.session_state.assessment_type is None:
            st.subheader("Choose Assessment Type")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📝 Objective Questions (MCQ)", use_container_width=True):
                    st.session_state.assessment_type = "objective"
                    st.session_state.show_feynman = False  # Reset Feynman display
                    st.rerun()
            with col2:
                if st.button("✍️ Subjective Questions", use_container_width=True):
                    st.session_state.assessment_type = "subjective"
                    st.session_state.show_feynman = False  # Reset Feynman display
                    st.rerun()

        # --- OBJECTIVE ASSESSMENT ---
        elif st.session_state.assessment_type == "objective":
            if "quiz_questions" not in final_state or not final_state["quiz_questions"]:
                with st.spinner("Generating objective questions..."):
                    from src.graph import generate_quiz_from_context
                    quiz_result = generate_quiz_from_context(final_state["processed_context"])
                    final_state["quiz_questions"] = quiz_result["quiz_questions"]
                    st.session_state.final_state = final_state
                    st.rerun()
            
            quiz_data = final_state.get("quiz_questions", [])
            st.subheader(f"📝 Objective Assessment: {current_obj}")
            
            if not quiz_data:
                st.error("Failed to generate questions. Please try again.")
                if st.button("Retry"):
                    st.session_state.assessment_type = None
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
                
                if st.session_state.quiz_submitted:
                    correct_count = sum(1 for idx, q in enumerate(quiz_data) if user_answers.get(idx) == q.get('answer'))
                    score_pct = (correct_count / len(quiz_data)) * 100
                    st.metric("Score", f"{score_pct:.0f}%", delta="Threshold: 70%")
                    
                    if score_pct >= 70:
                        st.balloons()
                        st.success(f"✅ PASSED! You have mastered '{current_obj}'.")
                        if st.session_state.current_index < len(st.session_state.checklist) - 1:
                            if st.button(f"Proceed to Next: {st.session_state.checklist[st.session_state.current_index + 1]}", type="primary"):
                                st.session_state.current_index += 1
                                st.session_state.agent_run_completed = False
                                st.session_state.quiz_submitted = False
                                st.session_state.assessment_type = None
                                st.session_state.feynman_attempt_count = 0
                                st.session_state.show_feynman = False
                                st.rerun()
                        else:
                            st.success("🎉 COURSE COMPLETE!")
                            if st.button("Start New Topic"):
                                st.session_state.clear()
                                st.rerun()
                    else:
                        st.error("❌ Score below 70%. Let's simplify the concepts.")
                        
                        # --- FEYNMAN TEACHING TRIGGER ---
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🎓 Get Simplified Explanation", use_container_width=True):
                                with st.spinner("Generating Feynman explanation..."):
                                    # Identify gaps
                                    correct_answers_map = {idx: q.get('answer') for idx, q in enumerate(quiz_data)}
                                    gaps = identify_knowledge_gaps(
                                        quiz_data,
                                        user_answers,
                                        correct_answers_map,
                                        "objective"
                                    )
                                    st.session_state.knowledge_gaps = gaps
                                    
                                    # Generate Feynman explanation
                                    feynman_text = generate_feynman_explanation(
                                        gaps,
                                        formatted_material,
                                        current_obj
                                    )
                                    st.session_state.feynman_explanation = feynman_text
                                    st.session_state.feynman_attempt_count += 1
                                    st.session_state.show_feynman = True
                                    
                                    # Clear quiz submission to allow retake
                                    st.session_state.quiz_submitted = False
                                    del final_state["quiz_questions"]  # Force new questions
                                    st.rerun()
                        
                        with col2:
                            if st.button("🔄 Retake Quiz Directly", use_container_width=True):
                                st.session_state.quiz_submitted = False
                                del final_state["quiz_questions"]  # Force new questions
                                st.rerun()

        # --- SUBJECTIVE ASSESSMENT ---
        elif st.session_state.assessment_type == "subjective":
            if "subjective_questions" not in final_state or not final_state["subjective_questions"]:
                with st.spinner("Generating subjective questions..."):
                    from src.graph import generate_subjective_questions
                    subj_result = generate_subjective_questions(final_state["processed_context"], current_obj)
                    final_state["subjective_questions"] = subj_result["subjective_questions"]
                    st.session_state.final_state = final_state
                    st.rerun()
            
            subj_questions = final_state.get("subjective_questions", [])
            st.subheader(f"✍️ Subjective Assessment: {current_obj}")
            
            if not subj_questions:
                st.error("Failed to generate questions.")
                if st.button("Retry"):
                    st.session_state.assessment_type = None
                    st.rerun()
            else:
                with st.form("subjective_form"):
                    user_answers = {}
                    for idx, q in enumerate(subj_questions):
                        st.markdown(f"**Q{idx+1}: {q}**")
                        user_answers[idx] = st.text_area(f"Your Answer:", key=f"subj_{idx}_{st.session_state.current_index}", height=100)
                        st.markdown("---")
                    
                    if st.form_submit_button("Submit for Evaluation"):
                        # if all(user_answers.values()):
                        with st.spinner("Evaluating your answers..."):
                            evaluation = evaluate_subjective_answers(
                                subj_questions, 
                                user_answers, 
                                final_state["formatted_content"],
                                current_obj
                            )
                            st.session_state.subjective_evaluation = evaluation
                            st.session_state.quiz_submitted = True
                        # else:
                            # st.warning("Please answer all questions before submitting.")
                
                if st.session_state.quiz_submitted and st.session_state.subjective_evaluation:
                    eval_data = st.session_state.subjective_evaluation
                    
                    st.subheader("📊 Evaluation Results")
                    for idx, result in enumerate(eval_data["results"]):
                        with st.expander(f"Q{idx+1} - Score: {result['score']}/100"):
                            st.markdown(f"**Question:** {result['question']}")
                            st.markdown(f"**Your Answer:** {result['user_answer']}")
                            st.info(f"**Comments:** {result['comments']}")
                    
                    avg_score = eval_data["average_score"]
                    st.metric("Average Score", f"{avg_score:.1f}/100", delta="Threshold: 70")
                    
                    if avg_score >= 70:
                        st.balloons()
                        st.success(f"✅ PASSED! You have mastered '{current_obj}'.")
                        if st.session_state.current_index < len(st.session_state.checklist) - 1:
                            if st.button(f"Proceed to Next: {st.session_state.checklist[st.session_state.current_index + 1]}", type="primary"):
                                st.session_state.current_index += 1
                                st.session_state.agent_run_completed = False
                                st.session_state.quiz_submitted = False
                                st.session_state.assessment_type = None
                                st.session_state.subjective_evaluation = None
                                st.session_state.feynman_attempt_count = 0
                                st.session_state.show_feynman = False
                                st.rerun()
                        else:
                            st.success("🎉 COURSE COMPLETE!")
                            if st.button("Start New Topic"):
                                st.session_state.clear()
                                st.rerun()
                    else:
                        st.error("❌ Average score below 70%. Let's simplify the concepts.")
                        
                        # --- FEYNMAN TEACHING TRIGGER ---
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🎓 Get Simplified Explanation", use_container_width=True):
                                with st.spinner("Generating Feynman explanation..."):
                                    # Identify gaps from subjective evaluation
                                    eval_results_map = {idx: result for idx, result in enumerate(eval_data["results"])}
                                    gaps = identify_knowledge_gaps(
                                        subj_questions,
                                        user_answers,
                                        eval_results_map,
                                        "subjective"
                                    )
                                    st.session_state.knowledge_gaps = gaps
                                    
                                    # Generate Feynman explanation
                                    feynman_text = generate_feynman_explanation(
                                        gaps,
                                        formatted_material,
                                        current_obj
                                    )
                                    st.session_state.feynman_explanation = feynman_text
                                    st.session_state.feynman_attempt_count += 1
                                    st.session_state.show_feynman = True
                                    
                                    # Clear evaluation to allow retake
                                    st.session_state.quiz_submitted = False
                                    st.session_state.subjective_evaluation = None
                                    del final_state["subjective_questions"]  # Force new questions
                                    st.rerun()
                        
                        with col2:
                            if st.button("🔄 Retake Assessment Directly", use_container_width=True):
                                st.session_state.quiz_submitted = False
                                st.session_state.subjective_evaluation = None
                                del final_state["subjective_questions"]  # Force new questions
                                st.rerun()
        
        # Back button
        if st.session_state.assessment_type is not None:
            if st.button("← Back to Assessment Selection"):
                st.session_state.assessment_type = None
                st.session_state.quiz_submitted = False
                st.session_state.subjective_evaluation = None
                st.session_state.show_feynman = False
                st.rerun()