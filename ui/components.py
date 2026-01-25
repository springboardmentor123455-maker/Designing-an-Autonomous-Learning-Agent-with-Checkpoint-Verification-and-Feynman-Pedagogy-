import streamlit as st
from typing import List, Optional
from core.models import StudyPlanItem, QuizItem, LearningMetrics
from ui.themes import ColorTheme, get_css_theme

def apply_theme():
    """Apply the colorful theme to the app"""
    st.markdown(get_css_theme(), unsafe_allow_html=True)
    st.markdown('<div class="animated-bg"></div>', unsafe_allow_html=True)

def render_header(title: str, subtitle: str = ""):
    """Render a colorful header"""
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h1 class="rainbow-header" style="font-size: 3rem; margin-bottom: 0.5rem;">{title}</h1>
        <p style="color: {ColorTheme.TEXT_SECONDARY}; font-size: 1.2rem;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(title: str, value: str, icon: str = "📊", color: str = ColorTheme.PRIMARY):
    """Render a metric card with gradient background"""
    st.markdown(f"""
    <div class="neon-card" style="text-align: center; margin: 10px;">
        <div style="font-size: 2rem; margin-bottom: 10px;">{icon}</div>
        <div class="metric-value" style="font-size: 2rem; font-weight: 800; 
             background: {ColorTheme.PRIMARY_GRADIENT}; -webkit-background-clip: text; 
             -webkit-text-fill-color: transparent; background-clip: text;">
            {value}
        </div>
        <div class="metric-label" style="color: {ColorTheme.TEXT_SECONDARY}; 
             font-size: 0.9rem; margin-top: 5px;">
            {title}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_study_plan_item(item: StudyPlanItem, show_action: bool = True):
    """Render a study plan item with gradient colors"""
    colors = ColorTheme.CHART_COLORS
    color = colors[(item.id - 1) % len(colors)]
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"""
        <div class="plan-item" style="border-left-color: {color};">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <span style="font-size: 1.5rem;">{item.icon}</span>
                <h3 style="margin: 0; color: {ColorTheme.TEXT_PRIMARY};">{item.topic}</h3>
            </div>
            <p style="color: {ColorTheme.TEXT_SECONDARY}; margin: 0; font-size: 0.95rem;">
                {item.objective}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if show_action and st.button("▶ Start", key=f"start_{item.id}", 
                                     use_container_width=True,
                                     type="primary" if not item.completed else "secondary"):
            return True
    return False

def render_quiz_question(question: str, index: int, total: int):
    """Render a quiz question with colorful styling"""
    progress = (index + 1) / total * 100
    colors = ColorTheme.CHART_COLORS
    
    st.markdown(f"""
    <div class="quiz-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <div style="background: {colors[index % len(colors)]}; color: white; 
                 padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                Question {index + 1} of {total}
            </div>
            <div style="width: 100px; height: 5px; background: rgba(99, 102, 241, 0.1); 
                 border-radius: 3px; overflow: hidden;">
                <div style="width: {progress}%; height: 100%; background: {colors[index % len(colors)]}; 
                     transition: width 0.3s ease;"></div>
            </div>
        </div>
        <h4 style="color: {ColorTheme.TEXT_PRIMARY}; margin-bottom: 15px;">{question}</h4>
    </div>
    """, unsafe_allow_html=True)

def render_score_breakdown(results: List[QuizItem]):
    """Render a colorful score breakdown chart"""
    import plotly.graph_objects as go
    
    questions = [f"Q{i+1}" for i in range(len(results))]
    scores = [item.score for item in results]
    max_scores = [item.max_score for item in results]
    
    fig = go.Figure()
    
    # Add bar for max score
    fig.add_trace(go.Bar(
        name='Possible Score',
        x=questions,
        y=max_scores,
        marker_color='rgba(99, 102, 241, 0.3)',
        hovertemplate='Max: %{y}<extra></extra>'
    ))
    
    # Add bar for actual score
    fig.add_trace(go.Bar(
        name='Your Score',
        x=questions,
        y=scores,
        marker_color=ColorTheme.PRIMARY,
        hovertemplate='Score: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Score Breakdown',
            'font': {'color': ColorTheme.TEXT_PRIMARY}
        },
        barmode='overlay',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': ColorTheme.TEXT_SECONDARY},
        showlegend=True,
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_progress_tracker(metrics: LearningMetrics):
    """Render a progress tracker with colorful rings"""
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    # Progress ring
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics.average_score,
        title={'text': "Average Score", 'font': {'color': ColorTheme.TEXT_PRIMARY}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': ColorTheme.PRIMARY},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': ColorTheme.DANGER},
                {'range': [50, 75], 'color': ColorTheme.WARNING},
                {'range': [75, 100], 'color': ColorTheme.SUCCESS}
            ],
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': ColorTheme.TEXT_SECONDARY}
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_lesson_content(content: str, title: str):
    """Render lesson content with beautiful formatting"""
    col1, col2, col3 = st.columns([1, 8, 1])
    
    with col2:
        st.markdown(f"""
        <div class="neon-card">
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="background: {ColorTheme.PRIMARY_GRADIENT}; 
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                    background-clip: text; margin-bottom: 10px;">
                    {title}
                </h2>
                <div style="width: 100px; height: 4px; background: {ColorTheme.PRIMARY_GRADIENT}; 
                     margin: 0 auto; border-radius: 2px;"></div>
            </div>
            <div style="color: {ColorTheme.TEXT_SECONDARY}; line-height: 1.6; font-size: 1.05rem;">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)