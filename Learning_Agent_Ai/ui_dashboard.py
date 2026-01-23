import streamlit as st
from checkpoint_1 import CHECKPOINTS
from ui_pdf_loader import upload_view
from ui_progress_store import ProgressStore


def render_dashboard():
    """
    Main Streamlit dashboard for the Autonomous Learning Agent.
    Handles:
    - Checkpoint navigation
    - Notes / PDF upload
    - Progress display
    """

    st.title("🎓 Autonomous Learning Agent")

    # -------------------------
    # Load progress
    # -------------------------
    store = ProgressStore()
    saved = store.load()

    if "cp" not in st.session_state:
        st.session_state.cp = saved["checkpoint"] if saved else 0

    total = len(CHECKPOINTS)
    current = st.session_state.cp

  
    # -------------------------
    # Completion state
    # -------------------------
    if current >= total:
        st.success("🎉 Congratulations! You completed all checkpoints.")
        st.balloons()
        return None, None

    # -------------------------
    # Progress bar
    # -------------------------
    st.progress(current / total)
    st.caption(f"Checkpoint {current + 1} of {total}")

    checkpoint = CHECKPOINTS[current]


    # -------------------------
    # Checkpoint display
    # -------------------------
    st.subheader(f"📌 {checkpoint['topic']}")

    with st.expander("🎯 Learning Objectives", expanded=True):
        for obj in checkpoint["objectives"]:
            st.write("•", obj)

    st.caption(f"✅ Success Criteria: {checkpoint['objectives']}")

    # -------------------------
    # Notes input (PDF + Text)
    # -------------------------
    pdf_text = upload_view()

    notes = st.text_area(
        "✍️ Enter your notes (optional)",
        value=pdf_text if pdf_text else "",
        height=200,
    )

    return checkpoint, notes
