import streamlit as st
from checkpoints import CHECKPOINTS
from graph import build_graph

st.set_page_config(
    page_title="Autonomous Computer Vision Tutor",
    layout="wide"
)

st.title("Autonomous Computer Vision Tutor")

# -------------------------------------------------
# Session state for progress tracking (NEW)
# -------------------------------------------------
if "score_history" not in st.session_state:
    st.session_state.score_history = []

# -------------------------------------------------
# Checkpoint selection
# -------------------------------------------------
checkpoint_names = [cp.topic for cp in CHECKPOINTS]
selected = st.selectbox("Select Checkpoint", checkpoint_names)

cp_index = checkpoint_names.index(selected)
checkpoint = CHECKPOINTS[cp_index]

# -------------------------------------------------
# Objectives
# -------------------------------------------------
st.subheader("Objectives")
for obj in checkpoint.objectives:
    st.write("•", obj)

# -------------------------------------------------
# NEW: Learning style selection
# -------------------------------------------------
learning_style = st.selectbox(
    "Preferred Learning Style",
    ["Theory-based", "Example-based", "Exam-oriented"]
)

# -------------------------------------------------
# NEW: Confidence slider
# -------------------------------------------------
confidence = st.slider(
    "How confident are you about this topic?",
    1, 5, 3
)

# -------------------------------------------------
# Answers
# -------------------------------------------------
st.subheader("Your Answers")
user_answers = st.text_area(
    "Write your answers here",
    height=200
)

# -------------------------------------------------
# Evaluate
# -------------------------------------------------
if st.button("🚀 Evaluate Checkpoint"):
    with st.spinner("Evaluating your understanding..."):
        app = build_graph()
        final_state = app.invoke({
            "checkpoint_index": cp_index,
            "answers": user_answers,
            "learning_style": learning_style,
            "confidence": confidence
        })

# -------------------------------------------------
# Questions
# -------------------------------------------------
    if "questions" in final_state:
        st.subheader("Generated Questions")
        st.markdown(final_state["questions"])

# -------------------------------------------------
# Result
# -------------------------------------------------
    st.subheader("Result")
    col1, col2 = st.columns(2)
    col2.metric("Status", final_state.get("status", "UNKNOWN"))
    st.session_state.score_history.append(final_state.get("score", 0))

# -------------------------------------------------
# Feedback
# -------------------------------------------------
    if "feedback" in final_state:
        st.subheader("Feedback")
        st.markdown(final_state["feedback"])

# -------------------------------------------------
# Confidence analysis
# -------------------------------------------------
    if "confidence_feedback" in final_state:
        st.subheader("🔍 Confidence Insight")
        st.info(final_state["confidence_feedback"])

# -------------------------------------------------
# Hints
# -------------------------------------------------
    if final_state.get("status") == "RETRY" and "hints" in final_state:
        st.subheader("💡 Hints to Improve")
        st.warning(final_state["hints"])

# -------------------------------------------------
# Follow-up
# -------------------------------------------------
    if "followup_question" in final_state:
        st.subheader("Follow-up Question")
        st.info(final_state["followup_question"])

# -------------------------------------------------
# Progress chart 
# -------------------------------------------------
if st.session_state.score_history:
    st.subheader("📈 Learning Progress")
    st.line_chart(st.session_state.score_history)
