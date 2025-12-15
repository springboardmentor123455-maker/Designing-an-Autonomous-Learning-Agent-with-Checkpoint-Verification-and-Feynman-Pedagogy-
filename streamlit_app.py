# app/streamlit_app.py
import os
import sys
from pathlib import Path
import streamlit as st
import importlib

# Ensure project root is importable (useful if running from inside app/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# show which file is running (helpful to debug which copy you edited)
st.set_page_config(page_title="Autonomous Learning Agent", layout="wide", page_icon="🧠")

importlib.invalidate_caches()
from app.core.checkpoints import list_checkpoint_ids, get_checkpoint_by_id
from app.core.graph import build_graph
from app.core.state import LearningState

st.title("🧠 Autonomous Learning Agent")

st.sidebar.header("Run Settings")
checkpoint_ids = list_checkpoint_ids()
if not checkpoint_ids:
    st.sidebar.error("No checkpoints found in app/data/checkpoints.json")
    st.stop()

selected_checkpoint = st.sidebar.selectbox("Checkpoint", checkpoint_ids, index=0)

backend_choice = st.sidebar.selectbox(
    "Validation backend (overrides env)",
    options=["auto", "local", "hf", "heuristic"],
    index=0,
    help="auto = try local -> hf -> heuristic. local uses transformers pipeline, hf uses HuggingFace Inference API"
)

hf_model = st.sidebar.text_input(
    "HF model repo id (HF_MODEL_REPO_ID)",
    value=os.getenv("HF_MODEL_REPO_ID", ""),
    help="Optional: override HF_MODEL_REPO_ID used by local/HF backends"
)

# --- Optional: custom user query (new) ---
st.sidebar.header("Optional: custom query")
user_query = st.sidebar.text_area(
    "Enter a custom question or text to search/use alongside the checkpoint",
    value="",
    height=140,
    placeholder="e.g. Explain regularization with an example..."
)

run_button = st.sidebar.button("Run Agent 🚀")

st.markdown(
    """
    **Notes**
    - This UI does not modify the core LangGraph workflow. It sets `VALIDATION_BACKEND` in the environment
      before invoking the graph so the validator uses the chosen backend.
    - For `local` backend you must have `transformers` installed and the model available locally.
    - For `hf` backend set `HUGGINGFACEHUB_API_TOKEN` in your `.env`.
    """
)

# Show checkpoint details
cp = get_checkpoint_by_id(selected_checkpoint)
st.subheader(f"Checkpoint: {cp['id']} — {cp['title']}")
st.markdown(f"**Description:** {cp.get('description','')}")
with st.expander("Learning objectives", expanded=True):
    for obj in cp["objectives"]:
        st.markdown(f"- {obj}")

with st.expander("Success criteria"):
    st.write(cp.get("success_criteria", "Not specified."))

if not run_button:
    st.info("Select a backend and click **Run Agent 🚀** in the sidebar to start.")
    st.stop()

# set env var so validate_context picks desired backend
os.environ["VALIDATION_BACKEND"] = backend_choice
if hf_model:
    os.environ["HF_MODEL_REPO_ID"] = hf_model

st.write(f"Running with validation backend = **{backend_choice}**")
if hf_model:
    st.write(f"Using HF_MODEL_REPO_ID = **{hf_model}**")

# Build initial state and inject user_query (if provided)
initial_state: LearningState = {
    "checkpoint_id": cp["id"],
    "checkpoint": cp,
    "trace": [],
}
if user_query and user_query.strip():
    initial_state["user_query"] = user_query.strip()
    st.markdown("**User query provided:**")
    st.code(user_query.strip())

graph_app = build_graph()

with st.spinner("Running LangGraph agent... this may take a few seconds"):
    try:
        final_state = graph_app.invoke(initial_state)
    except Exception as e:
        st.error(f"Agent crashed: {e}")
        raise

# Display results
st.markdown("---")
st.subheader("✅ Final Result")
col1, col2, col3 = st.columns([2, 2, 2])
col1.metric("Checkpoint ID", final_state.get("checkpoint_id", "N/A"))
col2.metric("Context Source", final_state.get("context_source", "unknown"))
score = final_state.get("context_relevance_score", None)
col3.metric("Relevance (1–5)", f"{score:.2f}" if score is not None else "N/A")

st.markdown("**Validator feedback:**")
st.write(final_state.get("context_validation_feedback", "(no feedback)"))

# Show gathered context documents
st.markdown("### 📚 Gathered Context Documents")
docs = final_state.get("gathered_context", [])
if not docs:
    st.warning("No context documents were gathered.")
else:
    for i, d in enumerate(docs, start=1):
        src = d.metadata.get("source", "unknown") if hasattr(d, "metadata") else "unknown"
        with st.expander(f"Document {i} — source: {src}", expanded=False):
            st.write(d.page_content if hasattr(d, "page_content") else str(d))

# Execution trace
st.markdown("### 🧵 Execution Trace")
trace = final_state.get("trace", []) or []
# show which backend validated (if validator appended that info in trace)
for line in trace:
    st.code(line)

# show used user_query (if any) from final_state trace/state
used_q = final_state.get("user_query") or initial_state.get("user_query") or "(none)"
st.markdown(f"**User query used:** `{used_q}`")

st.markdown("---")
st.caption("Agent run completed. Use the sidebar to run another checkpoint or change backend.")
