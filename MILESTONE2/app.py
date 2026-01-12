import streamlit as st
from checkpoints import CHECKPOINTS
from graph import build_question_graph, build_evaluation_graph

st.set_page_config(
    page_title="Autonomous Computer Vision Tutor",
    layout="wide"
)

st.title("🧠 Autonomous Computer Vision Tutor")

# -------------------------------------------------
# Checkpoint selection
# -------------------------------------------------
checkpoint_names = [cp.topic for cp in CHECKPOINTS]
selected = st.selectbox("Select Checkpoint", checkpoint_names)
checkpoint = CHECKPOINTS[checkpoint_names.index(selected)]
#Objectives
# -------------------------------------------------
# Objectives
# -------------------------------------------------
st.subheader("🎯 Objectives")
for obj in checkpoint.objectives:
    st.write("•", obj)

# -------------------------------------------------
# Generate questions
# -------------------------------------------------
q_graph = build_question_graph()
q_state = q_graph.invoke({"checkpoint": checkpoint})
questions = q_state["questions"]

# -------------------------------------------------
# Answer input
# -------------------------------------------------
st.subheader("✍️ Answer the Questions")
answers = {}

for i, q in enumerate(questions):
    st.markdown(f"**Q{i+1}. {q}**")
    answers[i] = st.text_area(f"Answer {i+1}", height=120)

# -------------------------------------------------
# Evaluate 
# -------------------------------------------------
if st.button("🚀 Evaluate Checkpoint"):

    eval_graph = build_evaluation_graph()

    final_state = eval_graph.invoke({
        "checkpoint": checkpoint,
        "questions": questions,
        "answers": answers
    })

    st.subheader("📊 Results")

    for i, res in enumerate(final_state["results"]):
        with st.expander(f"Question {i+1}"):
            st.write("**Status:**", res["status"])
            st.write("**Final Score:**", res["final_score"])
            st.write("**Semantic Alignment:**", res["semantic_score"])

    st.subheader("📈 Average Score")
    st.write(final_state["average_score"], "%")

    # -------------------------------------------------
    # Feynman Teaching Output 
    # -------------------------------------------------
    if "feynman_explanations" in final_state:
        st.subheader("🧩 Feynman Teaching (Simplified Explanations)")
        for concept, explanation in final_state["feynman_explanations"].items():
            with st.expander(concept):
                st.write(explanation)

    st.subheader("📝 Overall Feedback")
    st.success(final_state["feedback"])
