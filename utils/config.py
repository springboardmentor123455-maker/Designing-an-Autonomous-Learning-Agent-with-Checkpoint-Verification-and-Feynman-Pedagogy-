import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # HuggingFace
    HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")
    
    # Model settings
    MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Learning settings
    MAX_ATTEMPTS = 2
    PASSING_SCORE = 70  # Percentage
    QUIZ_QUESTIONS_COUNT = 5
    
    # UI settings
    THEME_PRIMARY = "#6366f1"
    THEME_SECONDARY = "#8b5cf6"
    THEME_SUCCESS = "#10b981"
    THEME_WARNING = "#f59e0b"
    THEME_DANGER = "#ef4444"
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.HUGGINGFACE_API_TOKEN:
            raise ValueError("HUGGINGFACE_API_TOKEN is required in environment variables")