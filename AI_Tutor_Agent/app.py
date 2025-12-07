import streamlit as st
import time
from src.graph import build_graph
from src.models import LearningCheckpoint

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AI Tutor Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR STRUCTURE & FONTS ---
st.markdown("""
    <style>
    .big-font {
        font-size:24px !important;
        font-weight: bold;
        color: #2E86C1;
    }
    .metric-box {
        padding: 10px;
        background-color: #f0f2f6;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("Autonomous AI Tutor Agent")
st.markdown("##### *Your Personal AI Research Assistant & Validator*")
st.divider()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuration")
    st.success(f"Model Active: gpt-5-nano")
    
    with st.expander("Upload Context (Optional)"):
        uploaded_file = st.file_uploader("Upload Notes (.txt)", type="txt")
        user_notes_text = uploaded_file.read().decode("utf-8") if uploaded_file else ""
    
    st.info("**Tip:** Detailed objectives help the agent find better content.")

# --- MAIN INPUT AREA ---
col1, col2 = st.columns([1, 2])

with col1:
    topic_input = st.text_input("Topic", value="Photosynthesis", placeholder="e.g. Black Holes")

with col2:
    objectives_input = st.text_input(
        "Learning Objectives", 
        value="Light-dependent reactions, Calvin cycle",
        placeholder="e.g. Event Horizon, Singularity theory"
    )

start_btn = st.button("Start Research Session", type="primary", use_container_width=True)

# --- EXECUTION LOGIC ---
if start_btn:
    if not topic_input or not objectives_input:
        st.error("Please provide both a Topic and Objectives.")
        st.stop()

    # 1. Initialize State
    active_cp = LearningCheckpoint(
        topic=topic_input,
        objectives=[obj.strip() for obj in objectives_input.split(",")],
        success_criteria="User must demonstrate understanding of key concepts."
    )
    
    initial_state = {
        "active_checkpoint": active_cp,
        "user_notes": user_notes_text,
        "retry_count": 0,
        "logs": [],
        "relevance_score": 0,
        "gathered_context": "",
        "feedback": ""
    }

    graph = build_graph()
    
    # 2. Run Agent with "Status" Widget
    final_state = {}
    
    # This creates a cool collapsible box for the logs
    with st.status("Agent is working...", expanded=True) as status:
        st.write("Initializing agent workflow...")
        
        # Stream the graph events
        for event in graph.stream(initial_state):
            for key, value in event.items():
                # Store final state for display
                if "relevance_score" in value:
                    final_state["relevance_score"] = value["relevance_score"]
                if "gathered_context" in value:
                    final_state["gathered_context"] = value["gathered_context"]
                if "feedback" in value:
                    final_state["feedback"] = value["feedback"]
                if "retry_count" in value:
                    final_state["retry_count"] = value["retry_count"]
                
                # Live Log Update
                if "logs" in value and value["logs"]:
                    for log in value["logs"]:
                        st.write(log)  # This prints inside the status box
                        # Auto-update status label based on activity
                        if "Searching" in log:
                            status.update(label="Searching the web...", state="running")
                        elif "Validation" in log:
                            status.update(label="Validating content...", state="running")
                        elif "Retry" in log:
                            status.update(label="Refining search query...", state="running")

        status.update(label="Mission Complete!", state="complete", expanded=False)

    # 3. DISPLAY RESULTS (Structured)
    score = final_state.get("relevance_score", 0)
    context = final_state.get("gathered_context", "No context found.")
    retries = final_state.get("retry_count", 0)
    
    st.divider()
    
    # Metrics Row
    m1, m2, m3 = st.columns(3)
    m1.metric("Relevance Score", f"{score}/5", delta="Target: 4/5")
    m2.metric("Retries Used", f"{retries}/5", delta_color="inverse")
    m3.metric("Status", "Success" if score >= 4 else "Optimization Ended")

    # Tabs for clean organization
    tab1, tab2, tab3 = st.tabs(["Study Material", "Agent Evaluation", "Raw Logs"])
    
    with tab1:
        st.markdown(f"### {topic_input}")
        st.markdown(context)
        
    with tab2:
        st.markdown("### Agent Feedback")
        if score >= 4:
            st.success("The agent determined this content meets your objectives.")
        else:
            st.warning("The content might not be perfect. Here is what the agent thought was missing:")
        
        st.info(f"**Improvement Hint:** {final_state.get('feedback', 'None')}")
        
    with tab3:
        st.text_area("System Logs", value="\n".join(final_state.get("logs", [])), height=300)