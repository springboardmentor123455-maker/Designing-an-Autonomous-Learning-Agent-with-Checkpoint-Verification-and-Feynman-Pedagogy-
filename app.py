import streamlit as st
import re
import json
from graph import build_graph
from checkpoints import CHECKPOINTS
from utils.dynamic_checkpoints import generate_checkpoints_from_topic

st.set_page_config(page_title="Autonomous Learning Agent")

st.markdown(
    """
    <style>
    .explanation-box {
        background-color: #0f2a44;
        color: #e6eef6;
        padding: 20px;
        border-radius: 10px;
        line-height: 1.7;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def format_feynman(text: str) -> str:
    text = re.sub(r"\n?\s*\d+\.\s*", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def build_dynamic_checkpoints(raw_json: str):
    checkpoints = {}
    data = json.loads(raw_json)

    for cp in data:
        checkpoints[cp["id"]] = {
            "topic": cp["topic"],
            "objectives": cp["objectives"],
            "success_criteria": "Understand the topic and answer verification questions."
        }

    return checkpoints

if "graph_app" not in st.session_state:
    st.session_state.graph_app = build_graph()

if "state" not in st.session_state:
    st.session_state.state = None

if "page" not in st.session_state:
    st.session_state.page = "start"

if "active_checkpoints" not in st.session_state:
    st.session_state.active_checkpoints = CHECKPOINTS.copy()

if st.session_state.page == "start":
    st.title("Autonomous Learning Agent")
    st.write("Enter a topic to begin the learning journey.")

    topic = st.text_input("Enter topic", value="Machine Learning")

    st.subheader("📄 Upload Notes (Optional)")
    uploaded_file = st.file_uploader(
        "Upload your notes as a .txt file",
        type=["txt"]
    )

    user_notes = ""
    if uploaded_file is not None:
        try:
            user_notes = uploaded_file.read().decode("utf-8")
            st.success("Notes uploaded successfully!")
        except Exception:
            st.error("Unable to read the uploaded file.")

    if st.button("Start Learning"):
        topic_clean = topic.strip().lower()

        if "machine learning" in topic_clean:
            st.session_state.active_checkpoints = CHECKPOINTS.copy()
            learning_path = ["1", "2", "3"]
        else:
            try:
                with st.spinner("Generating learning path..."):
                    raw = generate_checkpoints_from_topic(topic)
                    st.session_state.active_checkpoints = build_dynamic_checkpoints(raw)
                    learning_path = list(st.session_state.active_checkpoints.keys())
            except Exception:
                st.session_state.active_checkpoints = CHECKPOINTS.copy()
                learning_path = ["1", "2", "3"]

        st.session_state.state = st.session_state.graph_app.invoke(
            {
                "learning_path": learning_path,
                "current_checkpoint_index": 0,
                "completed_checkpoints": [],
                "selected_cp_id": learning_path[0],
                "user_notes": user_notes,
            }
        )

        st.session_state.page = "questions"


elif st.session_state.page == "questions":
    state = st.session_state.state

    st.header("Answer the Questions")

    answers = []
    for i, q in enumerate(state.get("questions", []), 1):
        st.write(f"Q{i}. {q}")
        answers.append(
            st.text_area("Your answer", key=f"ans_{i}", height=80)
        )

    if st.button("Submit"):
        state["answers"] = answers
        st.session_state.state = st.session_state.graph_app.invoke(state)
        st.session_state.page = "result"

elif st.session_state.page == "result":
    state = st.session_state.state
    score = state.get("score_percent", 0.0)

    st.header("Result")
    st.write(f"Score: {score:.2f}%")

    if score < 70:
        st.warning("Needs improvement")

        if "feynman_explanation" in state:
            st.subheader("Simple Explanation")
            st.markdown(
                f"<div class='explanation-box'>{format_feynman(state['feynman_explanation'])}</div>",
                unsafe_allow_html=True
            )

        if st.button("Try Again"):
            st.session_state.page = "questions"

    else:
        st.success("Checkpoint Passed")

        idx = state.get("current_checkpoint_index", 0)
        path = state.get("learning_path", [])

        if idx + 1 < len(path):
            if st.button("Continue to Next Checkpoint"):
                next_idx = idx + 1
                state["current_checkpoint_index"] = next_idx
                state["selected_cp_id"] = path[next_idx]

                st.session_state.state = st.session_state.graph_app.invoke(state)
                st.session_state.page = "questions"
        else:
            st.balloons()
            st.success("🎉 Learning Path Completed Successfully!")
