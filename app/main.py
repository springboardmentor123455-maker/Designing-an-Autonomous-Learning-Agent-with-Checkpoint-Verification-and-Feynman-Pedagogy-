import streamlit as st
from dotenv import load_dotenv

from app.core.state import LearningState, LearningCheckpoint
from app.core.context_gatherer import collect_learning_context
from app.core.context_processor import build_vector_index
from app.core.question_generator import build_assessment_questions
from app.core.answer_evaluator import evaluate_user_responses
from app.core.feynman_explainer import simplify_with_feynman
import os

os.environ["LANGSMITH_PROJECT"] = "GenAI-Learning-System"

# --------------------------------------------------
# Environment setup
# --------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="GenAI Learning Navigator",
    page_icon="🧭",
    layout="wide"
)

# --------------------------------------------------
# Define learning path (CHECKPOINTS)
# --------------------------------------------------
LEARNING_PATH = [
    LearningCheckpoint(
        id="cp1",
        title="Introduction to Generative AI",
        goals=[
            "Define Generative AI and how it differs from traditional AI",
            "Identify common examples of Generative AI systems",
            "Understand why Generative AI is important today"
        ]
    ),

    LearningCheckpoint(
        id="cp2",
        title="Large Language Models (LLMs)",
        goals=[
            "Explain what a Large Language Model is",
            "Understand how LLMs are trained using large datasets",
            "Identify popular LLMs such as GPT, LLaMA, and Gemini"
        ]
    ),

    LearningCheckpoint(
        id="cp3",
        title="Prompt Engineering",
        goals=[
            "Understand what a prompt is",
            "Learn how prompt wording affects model output",
            "Differentiate between zero-shot, one-shot, and few-shot prompting"
        ]
    ),

    LearningCheckpoint(
        id="cp4",
        title="Agentic AI Concepts",
        goals=[
            "Understand what an AI agent is",
            "Difference between LLMs and AI agents",
            "Role of tools, memory, and decision-making in agents"
        ]
    ),

    LearningCheckpoint(
        id="cp5",
        title="Applications of Generative AI",
        goals=[
            "Use of GenAI in education and learning",
            "Use of GenAI in software development",
            "Ethical concerns and responsible AI usage"
        ]
    ),
]
# --------------------------------------------------
# Initialize session state
# --------------------------------------------------
if "agent_state" not in st.session_state:
    st.session_state.agent_state = LearningState()

state: LearningState = st.session_state.agent_state

# --------------------------------------------------
# UI helpers
# --------------------------------------------------
def header():
    st.title("🧭 GenAI Learning Navigator")
    st.caption("Checkpoint-based learning with understanding verification")
    st.divider()

# --------------------------------------------------
# Stage 1: Checkpoint Selection
# --------------------------------------------------
def select_checkpoint():
    st.subheader("Select Your Learning Checkpoint")

    remaining = [
        cp for cp in LEARNING_PATH
        if cp.id not in state.completed
    ]

    if not remaining:
        st.success("🎉 You have completed all checkpoints!")
        if st.button("Restart Learning"):
            state.completed.clear()
            st.rerun()
        return

    for cp in remaining:
        if st.button(cp.title, use_container_width=True):
            state.active_checkpoint = cp
            state.flow_state = "study"
            state.context = None
            state.vector_index = None
            state.questions.clear()
            state.responses.clear()
            st.rerun()


# --------------------------------------------------
# Stage 2: Study Material
# --------------------------------------------------
def study_stage():
    cp = state.active_checkpoint
    st.subheader(f"📘 Study: {cp.title}")

    if state.context is None:
        with st.spinner("Collecting learning material..."):
            material, source = collect_learning_context(cp)
            state.context = material
            state.vector_index = build_vector_index(material)
            st.info(source)

    with st.expander("View Study Material", expanded=True):
        st.markdown(state.context)

    if st.button("Begin Assessment", type="primary"):
        state.flow_state = "quiz"
        st.rerun()


# --------------------------------------------------
# Stage 3: Quiz
# --------------------------------------------------
def quiz_stage():
    cp = state.active_checkpoint
    st.subheader(f"📝 Assessment: {cp.title}")
    st.caption("Answer all questions to continue")

    if not state.questions:
        with st.spinner("Preparing questions..."):
            state.questions = build_assessment_questions(cp)

    for idx, q in enumerate(state.questions):
        st.markdown(f"**Q{idx + 1}. {q}**")
        state.responses[idx] = st.text_area(
            "Your answer",
            value=state.responses.get(idx, ""),
            height=100,
            key=f"ans_{idx}"
        )
        st.divider()

    if st.button("Submit Answers", type="primary"):
        answers = list(state.responses.values())
        score, weak = evaluate_user_responses(state.questions, answers)
        state.score = score
        state.weak_topics = weak

        if score >= cp.pass_score:
            state.flow_state = "result"
        else:
            state.flow_state = "feynman"

        st.rerun()


# --------------------------------------------------
# Stage 4: Feynman Explanation
# --------------------------------------------------
def feynman_stage():
    cp = state.active_checkpoint
    st.subheader("🧩 Let’s Simplify the Confusing Parts")

    st.info(f"Score: {state.score*100:.1f}% — let’s improve your understanding")

    for q in state.weak_topics:
        with st.expander(q):
            explanation = simplify_with_feynman(
                question=q,
                wrong_answer="",
                context=state.context
            )
            st.success(explanation)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Try Again"):
            state.responses.clear()
            state.flow_state = "quiz"
            st.rerun()
            
    with col2:
        if st.button("View Result"):
            state.flow_state = "result"
            st.rerun()


# --------------------------------------------------
# Stage 5: Result
# --------------------------------------------------
def result_stage():
    cp = state.active_checkpoint
    passed = state.score >= cp.pass_score

    st.subheader("📊 Assessment Result")

    st.metric("Score", f"{state.score*100:.1f}%")
    st.metric("Pass Mark", f"{int(cp.pass_score*100)}%")

    if passed:
        st.success("✅ Checkpoint Completed")
        if st.button("Complete & Continue"):
            state.completed.append(cp.id)
            state.active_checkpoint = None
            state.flow_state = "select"
            st.rerun()
    else:
        st.error("❌ Not Passed")
        if st.button("Review with Simplified Explanation"):
            state.flow_state = "feynman"
            st.rerun()


# --------------------------------------------------
# Main Router
# --------------------------------------------------
def main():
    header()

    if state.flow_state == "select":
        select_checkpoint()
    elif state.flow_state == "study":
        study_stage()
    elif state.flow_state == "quiz":
        quiz_stage()
    elif state.flow_state == "feynman":
        feynman_stage()
    elif state.flow_state == "result":
        result_stage()


if __name__ == "__main__":
    main()
