import streamlit as st
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

from src.main import run_single_checkpoint, run_learning_path
from src.checkpoints import CHECKPOINTS

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="AI Autonomous Tutor",
    layout="wide"
)

st.title("🎓 AI Autonomous Tutor")
st.caption(
    "Checkpoint-based learning with assessment, Feynman teaching, and re-quiz"
)

# =================================================
# SESSION STATE INITIALIZATION
# =================================================
defaults = {
    "mode": "Interactive (UI-based)",
    "current_checkpoint": 0,
    "questions": None,
    "last_result": None,
    "quiz_round": 1,
    "attempt_history": []
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =================================================
# MODE SELECT
# =================================================
st.subheader("🧭 Select Learning Mode")
st.session_state.mode = st.radio(
    "",
    ["Autonomous (Auto-run)", "Interactive (UI-based)"],
    horizontal=True
)

# =================================================
# AUTONOMOUS MODE
# =================================================
if st.session_state.mode == "Autonomous (Auto-run)":
    if st.button("🚀 Start Autonomous Learning"):
        st.json(run_learning_path())
    st.stop()

# =================================================
# INTERACTIVE MODE
# =================================================
if st.session_state.current_checkpoint >= len(CHECKPOINTS):
    st.success("🎉 All checkpoints completed!")
    st.balloons()
    st.stop()

cp = CHECKPOINTS[st.session_state.current_checkpoint]

st.header(f"📘 Checkpoint {cp['id']}: {cp['topic']}")
st.caption(f"Attempt Round: {st.session_state.quiz_round}")

# =================================================
# GENERATE QUESTIONS
# =================================================
if st.session_state.questions is None:
    with st.spinner("Generating questions..."):
        res = run_single_checkpoint(cp)
    st.session_state.questions = res.get("questions", [])

questions = st.session_state.questions

# =================================================
# QUIZ INPUT  ✅ INDEX-BASED (CRITICAL FIX)
# =================================================
st.subheader("✍️ Quiz")

answers = {}

for idx, q in enumerate(questions):
    answers[idx] = st.text_area(
        f"Q{idx + 1}. {q['text']}",
        height=90,
        key=f"{cp['id']}_{st.session_state.quiz_round}_{idx}"
    )

# =================================================
# SUBMIT ANSWERS
# =================================================
if st.button("✅ Submit Answers"):
    with st.spinner("Evaluating your answers..."):
        result = run_single_checkpoint(
            cp,
            answers,
            quiz_round=st.session_state.quiz_round
        )

    st.session_state.last_result = result

    # ---------------- SAVE FULL HISTORY ----------------
    st.session_state.attempt_history.append({
        "time": datetime.now().isoformat(timespec="seconds"),
        "checkpoint": cp["topic"],
        "round": st.session_state.quiz_round,
        "score": result["score"],
        "passed": result["passed"],

        "questions": [q["text"] for q in questions],
        "answers": dict(answers),  # index → answer
        "per_question_scores": list(result["per_question_scores"]),
        "feedback": list(result["feedback"]),
        "feynman_explanations": result.get("feynman_explanations", [])
    })

# =================================================
# RESULTS DISPLAY
# =================================================
if st.session_state.last_result:
    r = st.session_state.last_result

    st.divider()
    st.subheader("📊 Result Analysis")

    for i, (q, s, fb) in enumerate(
        zip(questions, r["per_question_scores"], r["feedback"])
    ):
        with st.expander(f"Q{i+1} — Score {s}/100"):
            st.markdown(f"**Question:** {q['text']}")
            st.write("**Your Answer:**", answers.get(i, ""))
            st.caption(fb)

    # ---------------- PASS ----------------
    if r["passed"]:
        st.success(f"🎉 Passed with {r['score']}%")

        if st.button("➡️ Next Checkpoint"):
            st.session_state.current_checkpoint += 1
            st.session_state.questions = None
            st.session_state.last_result = None
            st.session_state.quiz_round = 1
            st.rerun()

    # ---------------- FAIL → FEYNMAN → REQUIZ ----------------
    else:
        st.error(f"❌ Score {r['score']}%. Review and retry.")

        if r.get("feynman_explanations"):
            st.subheader("🧠 Feynman Explanations")
            for fx in r["feynman_explanations"]:
                with st.expander(fx["question"]):
                    st.info(fx["explanation"])

        if st.button("🔁 Re-Quiz After Explanation"):
            st.session_state.quiz_round += 1
            st.session_state.questions = None
            st.session_state.last_result = None
            st.rerun()

# =================================================
# FULL ATTEMPT HISTORY
# =================================================
st.divider()
st.subheader("🕒 Full Learning History")

for h in reversed(st.session_state.attempt_history):
    status = "✅ Passed" if h["passed"] else "❌ Failed"

    with st.expander(
        f"[{h['time']}] {h['checkpoint']} | "
        f"Attempt {h['round']} | "
        f"{h['score']}% | {status}"
    ):
        for i, q in enumerate(h["questions"]):
            st.markdown(f"**Q{i+1}. {q}**")
            st.write("**Your Answer:**", h["answers"].get(i, ""))
            st.write(f"**Score:** {h['per_question_scores'][i]}/100")
            st.caption(h["feedback"][i])

        if h["feynman_explanations"]:
            st.subheader("🧠 Feynman Explanations")
            for fx in h["feynman_explanations"]:
                st.info(f"**{fx['question']}**\n\n{fx['explanation']}")
