"""
Colorful theme definitions for AI Tutor Pro
"""

class ColorTheme:
    # Modern gradient palette
    PRIMARY_GRADIENT = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    SECONDARY_GRADIENT = "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
    SUCCESS_GRADIENT = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
    WARNING_GRADIENT = "linear-gradient(135deg, #f6d365 0%, #fda085 100%)"
    DANGER_GRADIENT = "linear-gradient(135deg, #ff758c 0%, #ff7eb3 100%)"
    
    # Solid colors
    PRIMARY = "#6366f1"
    SECONDARY = "#8b5cf6"
    ACCENT = "#ec4899"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    INFO = "#3b82f6"
    
    # Backgrounds
    BG_LIGHT = "#f8fafc"
    BG_CARD = "#ffffff"
    BG_DARK = "#1e293b"
    
    # Text
    TEXT_PRIMARY = "#1e293b"
    TEXT_SECONDARY = "#64748b"
    TEXT_LIGHT = "#cbd5e1"
    
    # Charts
    CHART_COLORS = [
        "#4f46e5", "#7c3aed", "#ec4899", "#f59e0b", 
        "#10b981", "#3b82f6", "#8b5cf6", "#ef4444"
    ]

def get_css_theme():
    return f"""
    <style>
    /* Global Styles */
    .main .block-container {{
        padding-top: 2rem;
        background: linear-gradient(135deg, {ColorTheme.BG_LIGHT} 0%, #f1f5f9 100%);
        min-height: 100vh;
    }}
    
    /* Rainbow Header */
    .rainbow-header {{
        background: linear-gradient(90deg, 
            {ColorTheme.CHART_COLORS[0]} 0%, 
            {ColorTheme.CHART_COLORS[1]} 25%, 
            {ColorTheme.CHART_COLORS[2]} 50%, 
            {ColorTheme.CHART_COLORS[3]} 75%, 
            {ColorTheme.CHART_COLORS[4]} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 900;
    }}
    
    /* Neon Cards */
    .neon-card {{
        background: {ColorTheme.BG_CARD};
        border-radius: 20px;
        padding: 25px;
        box-shadow: 
            0 10px 25px rgba(99, 102, 241, 0.1),
            0 5px 10px rgba(99, 102, 241, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .neon-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: {ColorTheme.PRIMARY_GRADIENT};
    }}
    
    .neon-card:hover {{
        transform: translateY(-5px);
        box-shadow: 
            0 20px 40px rgba(99, 102, 241, 0.2),
            0 10px 20px rgba(99, 102, 241, 0.1);
    }}
    
    /* Glow Buttons */
    .glow-button {{
        background: {ColorTheme.PRIMARY_GRADIENT};
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .glow-button:hover {{
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
    }}
    
    .glow-button::after {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent 30%,
            rgba(255, 255, 255, 0.1) 50%,
            transparent 70%
        );
        transform: rotate(45deg);
        transition: all 0.5s ease;
    }}
    
    .glow-button:hover::after {{
        left: 100%;
    }}
    
    /* Study Plan Items */
    .plan-item {{
        background: linear-gradient(135deg, 
            rgba(99, 102, 241, 0.05) 0%, 
            rgba(139, 92, 246, 0.05) 100%);
        border-left: 5px solid;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }}
    
    .plan-item:hover {{
        transform: translateX(10px);
        background: linear-gradient(135deg, 
            rgba(99, 102, 241, 0.1) 0%, 
            rgba(139, 92, 246, 0.1) 100%);
    }}
    
    /* Progress Bars */
    .progress-bar {{
        height: 10px;
        background: linear-gradient(90deg, 
            {ColorTheme.SUCCESS} 0%, 
            {ColorTheme.WARNING} 50%, 
            {ColorTheme.DANGER} 100%);
        border-radius: 5px;
        margin: 10px 0;
    }}
    
    /* Quiz Cards */
    .quiz-card {{
        background: linear-gradient(135deg, 
            rgba(59, 130, 246, 0.05) 0%, 
            rgba(16, 185, 129, 0.05) 100%);
        border: 2px solid {ColorTheme.INFO};
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
    }}
    
    /* Score Badges */
    .score-badge {{
        background: {ColorTheme.SUCCESS_GRADIENT};
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }}
    
    /* Animated Background */
    .animated-bg {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        background: 
            radial-gradient(circle at 20% 50%, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(236, 72, 153, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 80%, rgba(16, 185, 129, 0.1) 0%, transparent 50%);
        animation: float 20s infinite ease-in-out;
    }}
    
    @keyframes float {{
        0%, 100% {{ transform: translate(0, 0) rotate(0deg); }}
        25% {{ transform: translate(10px, 10px) rotate(1deg); }}
        50% {{ transform: translate(0, 20px) rotate(0deg); }}
        75% {{ transform: translate(-10px, 10px) rotate(-1deg); }}
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: rgba(99, 102, 241, 0.1);
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {ColorTheme.PRIMARY_GRADIENT};
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {ColorTheme.SECONDARY_GRADIENT};
    }}
    
    /* Input Fields */
    .stTextInput > div > div > input {{
        border-radius: 12px;
        border: 2px solid rgba(99, 102, 241, 0.2);
        padding: 12px 16px;
        transition: all 0.3s ease;
        background: white;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {ColorTheme.PRIMARY};
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: rgba(99, 102, 241, 0.05);
        padding: 8px;
        border-radius: 12px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 10px 20px;
        background: transparent;
        transition: all 0.3s ease;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {ColorTheme.PRIMARY_GRADIENT};
        color: white !important;
    }}
    </style>
    """