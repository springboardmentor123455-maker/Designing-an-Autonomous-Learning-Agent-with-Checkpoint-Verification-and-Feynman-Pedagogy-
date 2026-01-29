import streamlit as st
from checkpoint_1 import CHECKPOINTS
from graph_workflow import workflow
from langgraph.types import Command
from state import LearningState
from ui_progress_store import ProgressStore
from ui_upload_view import upload_view

# streamlit run Learning_Agent_Ai\app_ex.py
# """
#     Main Streamlit dashboard for the Autonomous Learning Agent.
#     Handles:
#     - Checkpoint navigation
#     - Notes / PDF upload
#     - Progress display
#     """
# ======================================================
# STREAMLIT CONFIG
# ======================================================
st.set_page_config(
    page_title="Autonomous Learning Agent",
    layout="wide",
)

st.title("🎓 Autonomous Learning Agent")

    # -------------------------
    # Load progress
    # -------------------------
store = ProgressStore()
saved = store.load()

if "cp" not in st.session_state:
    st.session_state.cp = saved["checkpoint"] if saved else 0
if "config" not in st.session_state:
    st.session_state.config = {'configurable': {'thread_id': 'thread-1'}}
if st.session_state.cp >=1:
    st.session_state.cp = 0
    st.session_state.learning_state = None
    st.session_state.answers = []

    store.save(
        user_id="default_user",
        checkpoint_index=0,
    )

    # st.rerun()

total = len(CHECKPOINTS)
current = st.session_state.cp

  
    # -------------------------
    # Completion state
    # -------------------------
checkpoint = CHECKPOINTS[current]
notes = None
if current >= total:
    st.success("🎉 Congratulations! You completed all checkpoints.")
    st.balloons()
    notes = None
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
    for obj in checkpoint['objectives']:
        st.write("•", obj)

st.caption(f"✅ Success Criteria: {checkpoint['success_criteria']}")

    # -------------------------
    # Notes input (PDF + Text)
    # -------------------------
pdf_text = upload_view()

notes = st.text_area(
    "✍️ Enter your notes (optional)",
    value=pdf_text if pdf_text else "",
    height=200,
)


if checkpoint is None:
    st.stop()

# ======================================================
# SESSION STATE INITIALIZATION
# ======================================================
if "learning_state" not in st.session_state:
    st.session_state.learning_state = None

if "answers" not in st.session_state:
    st.session_state.answers = []
# ======================================================
# START / CONTINUE LEARNING
# ======================================================
config = st.session_state.config
state = LearningState(
    checkpoint=checkpoint,
    user_Notes=notes,

    answers=[],            # ✅ REQUIRED (prevents KeyError)
    questions=[],
    max_iteration=2,
    context_iteration=1,
    feynman_iteration=1,

    gether_context= "",
    chunks = [] ,
    vectore_semalirty = [],
    score_percentage = [],

    gaps_list = {},
    gaps = "",
    feynman_explanation = "",
    
    passed=False
)
if st.button("🚀 Start / Continue Learning", type="primary"):

    
    print(state)
    st.session_state.learning_state = workflow.invoke(state , config=config)
    # st.rerun()
    

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
    st.caption(f"Relevance score: {state['revelence_score'][-1]}")

# ======================================================
# QUESTIONS UI
# ======================================================
if "questions" in state and state["questions"]:

    st.subheader("❓ Assessment Questions")
    if len(st.session_state.answers) != len(state["questions"]):
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

        state = workflow.invoke(Command(resume={"approved": "yes", 'answers':st.session_state.answers}),
                config=config)
        st.session_state.learning_state = state
        # st.rerun()

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

            
            if st.button("➡️ Go to Next Checkpoint"):
                store.save(
                    user_id="default_user",
                    checkpoint_index=st.session_state.cp + 1,
                )
                st.session_state.cp += 1
                st.session_state.learning_state = None
                st.session_state.answers = []
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

            if st.button("🔁 Retry Same Checkpoint"):
                st.session_state.learning_state = None
                st.session_state.answers = []
                st.rerun()


