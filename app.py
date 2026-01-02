import streamlit as st
from dotenv import load_dotenv
load_dotenv()

import re
import os
from graph import build_graph
from checkpoints import CHECKPOINTS
from progress_storage import save_progress
from langchain_groq import ChatGroq

# ---------------- ENV ----------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found in environment")
    st.stop()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0
)

graph = build_graph()

# ---------------- UI CONFIG ----------------
st.set_page_config("Autonomous AI Tutor – Milestone 2", layout="wide")
st.title("🚀 Autonomous AI Tutor – Milestone 2")

# ---------------- PERFORMANCE LABEL ----------------
def performance_label(score_percent: float):
    if score_percent >= 90:
        return "🟢 Excellent", "Strong understanding"
    elif score_percent >= 70:
        return "🟢 Good", "Minor gaps"
    elif score_percent >= 50:
        return "🟡 Average", "Needs improvement"
    elif score_percent >= 30:
        return "🔴 Weak", "Significant gaps"
    else:
        return "🚨 Very Weak", "Relearning required"

# ---------------- HELPERS ----------------
def generate_questions(topic, context):
    prompt = f"""
Generate exactly 3 exam-style questions.

Rules:
- No explanation
- No headings
- Format exactly as:
Q1. ...
Q2. ...
Q3. ...

Topic: {topic}
Context:
{context[:1500]}
"""
    resp = llm.invoke(prompt).content
    return re.findall(r"Q\d+\.\s*(.*)", resp)

def evaluate_answer(question, answer, context):
    prompt = f"""
Evaluate the answer using this rubric:

90–100: Excellent
70–89: Good
50–69: Average
30–49: Poor
0–29: Incorrect

Question:
{question}

Student Answer:
{answer}

Reference Content:
{context[:2000]}

Respond ONLY in this format:
Score: <number>
Feedback: <one sentence>
"""
    resp = llm.invoke(prompt).content

    score_match = re.search(r"Score:\s*(\d{1,3})", resp)
    score = int(score_match.group(1)) if score_match else 0

    fb_match = re.search(r"Feedback:\s*(.*)", resp, re.DOTALL)
    feedback = fb_match.group(1).strip() if fb_match else resp.strip()

    return score, feedback

# ---------------- INPUT SECTION ----------------
checkpoint_index = st.selectbox(
    "Select Checkpoint",
    range(len(CHECKPOINTS)),
    format_func=lambda i: CHECKPOINTS[i].topic
)

uploaded = st.file_uploader("Upload notes (.txt)", type=["txt"])
notes = st.text_area("Or paste notes here")

mode = st.radio(
    "Retrieval Mode",
    ["Auto", "Force Local Notes", "Force RAG"]
)

# ---------------- RUN PIPELINE ----------------
if st.button("Run Evaluation"):
    init_state = {"checkpoint_index": checkpoint_index}

    if mode == "Force Local Notes" or (mode == "Auto" and uploaded):
        init_state["raw_context"] = (
            uploaded.read().decode() if uploaded else notes
        )
        init_state["retrieval_mode"] = "Local"
        init_state["data_source"] = "Local Notes"
    else:
        init_state["retrieval_mode"] = "RAG"

    result = graph.invoke(init_state)
    st.session_state.result = result

    save_progress({
        "checkpoint": result["checkpoint"].topic,
        "score": result["relevance_score"],
        "weak_areas": result["weak_areas"],
        "next": CHECKPOINTS[result["next_checkpoint_index"]].topic
    })

# ---------------- OUTPUT ----------------
if "result" in st.session_state:
    r = st.session_state.result

    st.subheader("📊 Evaluation Result")
    st.write("Checkpoint:", r["checkpoint"].topic)
    st.write("Relevance Score:", r["relevance_score"], "/5")
    st.write("Data Source:", r.get("data_source", "Web RAG"))
    st.write("Weak Areas:", r["weak_areas"])

    if r.get("feynman_explanation"):
        st.subheader("🧠 Feynman Explanation")
        st.info(r["feynman_explanation"])

    st.success(
        f"Next Recommended Checkpoint: {CHECKPOINTS[r['next_checkpoint_index']].topic}"
    )

    # ---------------- SHOW CONTEXT ----------------
    st.divider()
    st.subheader("📄 Retrieved / Provided Content")
    with st.expander("View content used for evaluation"):
        st.write(r.get("raw_context", "No content available"))

    # ---------------- QUESTIONS ----------------
    st.divider()
    st.subheader("📝 Practice Questions")

    if "questions" not in st.session_state:
        st.session_state.questions = []
        st.session_state.answers = []

    if st.button("Generate Questions"):
        st.session_state.questions = generate_questions(
            r["checkpoint"].topic,
            r.get("raw_context", "")
        )
        st.session_state.answers = [""] * len(st.session_state.questions)

    if st.session_state.questions:
        total_score = 0

        for i, q in enumerate(st.session_state.questions):
            st.markdown(f"**Q{i+1}. {q}**")
            st.session_state.answers[i] = st.text_area(
                f"Your Answer {i+1}",
                key=f"ans_{i}"
            )

        if st.button("Evaluate Answers"):
            st.subheader("📈 Answer Evaluation")

            for i, q in enumerate(st.session_state.questions):
                score, feedback = evaluate_answer(
                    q,
                    st.session_state.answers[i],
                    r.get("raw_context", "")
                )
                total_score += score

                q_label, _ = performance_label(score)

                st.markdown(
                    f"""
                    **Q{i+1} Score:** {score}/100  
                    **Performance:** {q_label}  
                    **Feedback:** {feedback}
                    """
                )

            final_percentage = total_score / len(st.session_state.questions)
            label, meaning = performance_label(final_percentage)

            st.divider()
            st.subheader("📊 Overall Performance")

            st.markdown(
                f"""
                **Final Score:** {final_percentage:.1f}%  
                **Overall Level:** {label}  
                **Interpretation:** {meaning}
                """
            )
