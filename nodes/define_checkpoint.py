from state import AgentState
import streamlit as st
from checkpoints import CHECKPOINTS

def define_checkpoint(state: AgentState) -> AgentState:
    cp_id = state.get("selected_cp_id")

    # Use session-level checkpoints if present (dynamic mode)
    active_checkpoints = st.session_state.get("active_checkpoints", CHECKPOINTS)

    checkpoint = active_checkpoints.get(cp_id)

    if not checkpoint:
        raise ValueError(f"Checkpoint ID {cp_id} not found.")

    return {
        "checkpoint": checkpoint
    }
