import os
import sys
from types import SimpleNamespace

import streamlit as st

# 🔧 PATH FIX (do NOT remove)
# ======================================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ======================================================
# 🔧 MONKEY PATCH: FIX upload_view IMPORT
# ======================================================
import ui_pdf_loader  # loads the module
from ui_upload_view import upload_view

# Inject upload_view into ui_pdf_loader namespace
ui_pdf_loader.upload_view = upload_view

# ======================================================
# 🔧 FIX CHECKPOINT dict → object
# ======================================================
import checkpoint_1

checkpoint_1.CHECKPOINTS = [
 cp if isinstance(cp, SimpleNamespace) else SimpleNamespace(**cp)
    for cp in checkpoint_1.CHECKPOINTS
]

from graph_workflow import workflow
from state import LearningState
from ui_dashboard import render_dashboard
from ui_progress_store import ProgressStore

# ======================================================
# STREAMLIT CONFIG
# ======================================================
st.set_page_config(
    page_title="Autonomous Learning Agent",
    layout="wide",
)

# ======================================================
# DASHBOARD (Checkpoint + Notes)
# ======================================================
checkpoint, notes = render_dashboard()

# If learning completed
if checkpoint is None:
    st.stop()

# ======================================================
# SESSION STATE INITIALIZATION
# ======================================================
if "learning_state" not in st.session_state:
    st.session_state.learning_state = None

if "answers" not in st.session_state:
    st.session_state.answers = []

store = ProgressStore()

# ======================================================
# START / CONTINUE LEARNING
# ======================================================
if st.button("🚀 Start / Continue Learning", type="primary"):

    state = LearningState(
        checkpoint=checkpoint,
        user_Notes=notes,
        max_iteration=3,
        context_iteration=1,
        feynman_iteration=1,
    )

    st.session_state.learning_state = workflow.invoke(state)
    st.rerun()

# ======================================================
# SHOW LEARNING STATE
# ======================================================
state = st.session_state.learning_state

if not state:
    st.stop()

st.divider()

# ======================================================
# CONTEXT DISPLAY
# ======================================================
st.subheader("📚 Learning Context")
st.write(state.get("gether_context", ""))

if "revelence_score" in state:
    st.caption(f"Relevance score: {state['revelence_score']}")

# ======================================================
# QUESTIONS UI
# ======================================================
if "questions" in state and state["questions"]:

    st.subheader("❓ Assessment Questions")
    st.session_state.answers = []

    for idx, question in enumerate(state["questions"]):
        st.markdown(f"**Q{idx + 1}. {question}**")
        answer = st.text_area(
            f"Your answer for Q{idx + 1}",
            key=f"answer_{idx}",
        )
        st.session_state.answers.append(answer)

    # ==================================================
    # SUBMIT ANSWERS
    # ==================================================
    if st.button("✅ Submit Answers"):

        state["answers"] = st.session_state.answers
        state = workflow.invoke(state)
        st.session_state.learning_state = state

        st.divider()
        st.subheader("📊 Evaluation Result")

        scores = state.get("score_percentage")

        if scores:
            avg_score = sum(scores) / len(scores)
            st.write(f"**Average Score:** {avg_score:.2f}%")

        # =========================
        # PASS CASE
        # =========================
        if state.get("passed", False):
            st.success("🎉 Checkpoint PASSED!")

            store.save(
                user_id="default_user",
                checkpoint_index=st.session_state.cp + 1,
            )

            st.session_state.cp += 1
            st.session_state.learning_state = None
            st.info("Moving to next checkpoint...")
            st.rerun()

        # =========================
        # FEYNMAN CASE
        # =========================
        else:
            st.error("❌ Checkpoint NOT passed")

            if "feynman_explanation" in state:
                st.subheader("🧠 Feynman Explanation")
                st.info(state["feynman_explanation"])

            st.caption("Review the explanation and try again.")
