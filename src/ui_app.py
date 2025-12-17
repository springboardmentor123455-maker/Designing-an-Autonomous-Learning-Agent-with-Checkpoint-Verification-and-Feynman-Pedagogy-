import streamlit as st
from agent_graph import build_graph

# Build agent once
graph = build_graph()

# Initialize session state
if "state" not in st.session_state:
    st.session_state.state = {
        "checkpoints": [],
        "current_checkpoint": 0,
        "user_input": "",
        "score": 0.0,
        "passed": False,
        "explanation_level": ""
    }

st.set_page_config(page_title="AI Learning Agent", layout="centered")
st.title("🤖 Autonomous Learning Agent (IoT)")

# Load checkpoints only once
if not st.session_state.state["checkpoints"]:
    from pathlib import Path
    import json
    ckpt_path = Path(__file__).parent / "checkpoints" / "ckpts_sample.json"
    with open(ckpt_path, "r", encoding="utf-8") as f:
        st.session_state.state["checkpoints"] = json.load(f)

state = st.session_state.state
cp = state["checkpoints"][state["current_checkpoint"]]

# Progress
st.progress((state["current_checkpoint"] + 1) / len(state["checkpoints"]))
st.markdown(f"### 📘 Checkpoint {state['current_checkpoint'] + 1}")
st.markdown(f"**Topic:** {cp['topic']}")

st.markdown("**Objectives:**")
for obj in cp["objectives"]:
    st.markdown(f"- {obj}")

# User input
answer = st.text_area("Explain in your own words:")

if st.button("Submit Answer"):
    state["user_input"] = answer
    graph.invoke(state)

    if state["passed"]:
        st.success(" Passed! Moving to next checkpoint.")
        state["current_checkpoint"] += 1
        state["user_input"] = ""
    else:
        st.error(" Not sufficient. Read the explanation below.")

# Show explanation if failed
if state.get("explanation_level") == "feynman":
    st.info(" Feynman Explanation provided above. Try again.")
