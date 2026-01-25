"""
Streamlit Dashboard for Autonomous Learning Agent
Real-time visualization and analysis of the learning workflow
"""
import streamlit as st
import sys
from pathlib import Path
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.checkpoint import Checkpoint
from src.models.state import create_initial_state
from src.graph.learning_graph import create_learning_graph

# Page configuration
st.set_page_config(
    page_title="Autonomous Learning Agent ",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visualization
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .step-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border-left-color: #28a745;
    }
    .error-box {
        background-color: #f8d7da;
        border-left-color: #dc3545;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left-color: #17a2b8;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left-color: #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'workflow_result' not in st.session_state:
    st.session_state.workflow_result = None
if 'execution_logs' not in st.session_state:
    st.session_state.execution_logs = []

def log_step(message, status="info"):
    """Add a log entry with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.execution_logs.append({
        'time': timestamp,
        'message': message,
        'status': status
    })

def display_logs():
    """Display execution logs in the sidebar"""
    st.sidebar.subheader("📋 Execution Logs")
    for log in reversed(st.session_state.execution_logs[-10:]):
        icon = {
            'info': 'ℹ️',
            'success': '✅',
            'error': '❌',
            'warning': '⚠️'
        }.get(log['status'], 'ℹ️')
        st.sidebar.text(f"{icon} {log['time']} - {log['message']}")

def visualize_workflow_stage(state, stage_name):
    """Visualize current workflow stage"""
    stages = ["initialized", "checkpoint_defined", "context_gathered", "context_validated", "context_processed"]
    current_idx = stages.index(state.get('current_stage', 'initialized')) if state.get('current_stage') in stages else 0
    
    cols = st.columns(len(stages))
    for idx, stage in enumerate(stages):
        with cols[idx]:
            if idx < current_idx:
                st.success(f"✅ {stage.replace('_', ' ').title()}")
            elif idx == current_idx:
                st.info(f"🔄 {stage.replace('_', ' ').title()}")
            else:
                st.text(f"⏳ {stage.replace('_', ' ').title()}")

def run_workflow(checkpoint, user_notes):
    """Execute the learning workflow with real-time updates"""
    log_step("Starting workflow execution", "info")
    
    # Create progress placeholder
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize state
        log_step("Initializing state", "info")
        status_text.text("Initializing state...")
        progress_bar.progress(10)
        time.sleep(0.5)
        
        state = create_initial_state(
            checkpoint=checkpoint,
            user_notes=user_notes
        )
        
        # Create graph
        log_step("Creating workflow graph", "info")
        status_text.text("📊 Creating workflow graph...")
        progress_bar.progress(20)
        time.sleep(0.5)
        
        graph = create_learning_graph()
        
        # Execute workflow
        log_step("Executing workflow nodes", "info")
        status_text.text("⚙️ Executing workflow...")
        progress_bar.progress(40)
        
        result = graph.invoke(state)
        
        progress_bar.progress(100)
        status_text.text("✅ Workflow completed!")
        
        if result.get('error'):
            log_step(f"Workflow completed with error: {result['error']}", "warning")
        else:
            log_step("Workflow completed successfully", "success")
        
        return result
        
    except Exception as e:
        log_step(f"Error: {str(e)}", "error")
        st.error(f"❌ Error: {str(e)}")
        return None

# Main UI
st.markdown('<h1 class="main-header">🎓 Autonomous Learning Agent Dashboard</h1>', unsafe_allow_html=True)

st.markdown("""
This dashboard allows you to visualize and analyze the learning workflow in real-time.
Watch each step execute and see how the system gathers, validates, and processes learning materials.
""")

# Sidebar configuration
st.sidebar.title("⚙️ Configuration")

# Input section
st.sidebar.subheader("📝 Learning Checkpoint")

topic = st.sidebar.text_input(
    "Topic",
    value="Python Functions",
    help="What do you want to learn?"
)

objectives_text = st.sidebar.text_area(
    "Learning Objectives (one per line)",
    value="Understand function syntax\nLearn about parameters\nMaster return values",
    height=100,
    help="Enter your learning objectives, one per line"
)

user_notes = st.sidebar.text_area(
    "Your Notes (Optional)",
    value="Functions are reusable blocks of code in Python.\nThey are defined using the 'def' keyword.\nExample: def greet(name): return f'Hello {name}'",
    height=150,
    help="Any notes or materials you already have"
)

# Parse objectives
objectives = [obj.strip() for obj in objectives_text.split('\n') if obj.strip()]

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Workflow Execution", "📈 Analysis", "🔍 Details", "📋 Logs"])

with tab1:
    st.header("Workflow Execution")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🚀 Run Workflow", type="primary", use_container_width=True):
            st.session_state.execution_logs = []
            
            # Create checkpoint
            checkpoint = Checkpoint(
                topic=topic,
                objectives=objectives
            )
            
            # Display checkpoint info
            st.subheader("📚 Learning Checkpoint")
            st.markdown(f"**Topic:** {checkpoint.topic}")
            st.markdown("**Objectives:**")
            for i, obj in enumerate(checkpoint.objectives, 1):
                st.markdown(f"{i}. {obj}")
            
            st.divider()
            
            # Run workflow
            with st.spinner("Executing workflow..."):
                result = run_workflow(checkpoint, user_notes if user_notes else None)
                st.session_state.workflow_result = result
    
    # Display results if available
    if st.session_state.workflow_result:
        result = st.session_state.workflow_result
        
        st.divider()
        st.subheader("📊 Workflow Progress")
        
        # Visualize stages
        visualize_workflow_stage(result, result.get('current_stage'))
        
        st.divider()
        
        # Results summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Current Stage",
                result.get('current_stage', 'N/A').replace('_', ' ').title()
            )
        
        with col2:
            st.metric(
                "Contexts Gathered",
                len(result.get('gathered_contexts', []))
            )
        
        with col3:
            st.metric(
                "Validation Status",
                "✅ Valid" if result.get('context_valid') else "❌ Invalid"
            )
        
        with col4:
            st.metric(
                "Retry Count",
                result.get('retry_count', 0)
            )
        
        # Error display
        if result.get('error'):
            st.error(f"⚠️ **Error:** {result['error']}")
            if "API key" in result['error'] or "GITHUB_TOKEN" in result['error']:
                st.info("💡 **Note:** Configure your .env file with API keys to enable full functionality.")

with tab2:
    st.header("📈 Workflow Analysis")
    
    if st.session_state.workflow_result:
        result = st.session_state.workflow_result
        
        # Context quality analysis
        st.subheader("📄 Gathered Contexts Analysis")
        
        contexts = result.get('gathered_contexts', [])
        
        if contexts:
            # Show statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Contexts", len(contexts))
            
            with col2:
                user_notes_count = sum(1 for c in contexts if c.source == "user_notes")
                st.metric("From User Notes", user_notes_count)
            
            with col3:
                web_count = sum(1 for c in contexts if c.source != "user_notes")
                st.metric("From Web Search", web_count)
            
            st.divider()
            
            # Display each context
            for i, context in enumerate(contexts, 1):
                with st.expander(f"📝 Context {i} - {context.source} (Relevance: {context.relevance_score:.2f})"):
                    st.markdown(f"**Source:** {context.source}")
                    st.markdown(f"**Relevance Score:** {context.relevance_score:.2f}")
                    if hasattr(context, 'url') and context.url:
                        st.markdown(f"**URL:** {context.url}")
                    st.markdown("**Content:**")
                    st.text_area(
                        "Content",
                        value=context.content,
                        height=150,
                        key=f"context_{i}",
                        label_visibility="collapsed"
                    )
        else:
            st.info("No contexts gathered yet. Run the workflow to see results.")
        
        # Validation message
        if result.get('validation_message'):
            st.divider()
            st.subheader("🔍 Validation Details")
            st.info(result['validation_message'])
    
    else:
        st.info("Run the workflow to see analysis results.")

with tab3:
    st.header("🔍 Detailed State Information")
    
    if st.session_state.workflow_result:
        result = st.session_state.workflow_result
        
        # Display full state
        st.subheader("📋 Complete State")
        
        # Checkpoint details
        with st.expander("📚 Checkpoint Details", expanded=True):
            st.json({
                "topic": result['checkpoint'].topic,
                "objectives": result['checkpoint'].objectives
            })
        
        # User notes
        with st.expander("📝 User Notes"):
            if result.get('user_notes'):
                st.text_area("Notes", value=result['user_notes'], height=100, disabled=True, label_visibility="collapsed")
            else:
                st.info("No user notes provided")
        
        # Workflow messages
        with st.expander("💬 Workflow Messages"):
            messages = result.get('messages', [])
            if messages:
                for i, msg in enumerate(messages, 1):
                    st.text(f"{i}. {msg}")
            else:
                st.info("No workflow messages")
        
        # Full state (for debugging)
        with st.expander("🔧 Full State (Debug)"):
            # Create a clean version without circular references
            debug_state = {
                'current_stage': result.get('current_stage'),
                'retry_count': result.get('retry_count'),
                'context_valid': result.get('context_valid'),
                'validation_message': result.get('validation_message'),
                'error': result.get('error'),
                'contexts_count': len(result.get('gathered_contexts', [])),
                'messages_count': len(result.get('messages', []))
            }
            st.json(debug_state)
    else:
        st.info("Run the workflow to see detailed state information.")

with tab4:
    st.header("📋 Execution Logs")
    
    if st.session_state.execution_logs:
        st.info(f"Showing last {len(st.session_state.execution_logs)} log entries")
        
        for log in reversed(st.session_state.execution_logs):
            icon = {
                'info': 'ℹ️',
                'success': '✅',
                'error': '❌',
                'warning': '⚠️'
            }.get(log['status'], 'ℹ️')
            
            box_class = f"{log['status']}-box"
            st.markdown(
                f'<div class="step-box {box_class}">{icon} <strong>{log["time"]}</strong> - {log["message"]}</div>',
                unsafe_allow_html=True
            )
    else:
        st.info("No execution logs yet. Run the workflow to see logs.")

# Sidebar logs
display_logs()

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🎓 Autonomous Learning Agent </p>
    <p style="font-size: 0.8rem;">Real-time workflow visualization and analysis</p>
</div>
""", unsafe_allow_html=True)
