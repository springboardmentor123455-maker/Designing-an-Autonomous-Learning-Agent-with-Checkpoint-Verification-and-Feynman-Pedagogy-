"""
Configuration management for the learning agent system.
Handles environment variables and system configuration.
"""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Ollama Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.1", alias="OLLAMA_MODEL")
    
    # Vector Store Configuration
    chroma_db_path: str = Field(default="./data/chroma_db", alias="CHROMA_DB_PATH")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    
    # Search Configuration
    search_engine: str = Field(default="duckduckgo", alias="SEARCH_ENGINE")
    max_search_results: int = Field(default=5, alias="MAX_SEARCH_RESULTS")
    
    # Assessment Configuration
    passing_threshold: float = Field(default=0.7, alias="PASSING_THRESHOLD")
    max_questions_per_checkpoint: int = Field(default=5, alias="MAX_QUESTIONS_PER_CHECKPOINT")
    min_questions_per_checkpoint: int = Field(default=3, alias="MIN_QUESTIONS_PER_CHECKPOINT")
    
    # Context Configuration
    max_context_length: int = Field(default=4000, alias="MAX_CONTEXT_LENGTH")
    context_overlap: int = Field(default=200, alias="CONTEXT_OVERLAP")
    relevance_threshold: float = Field(default=4.0, alias="RELEVANCE_THRESHOLD")
    
    # Database Configuration
    database_path: str = Field(default="./data/progress.db", alias="DATABASE_PATH")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    enable_langsmith: bool = Field(default=False, alias="ENABLE_LANGSMITH")
    langsmith_project_name: str = Field(default="learning-agent", alias="LANGSMITH_PROJECT_NAME")
    
    # File Upload Configuration
    max_file_size_mb: int = Field(default=10, alias="MAX_FILE_SIZE_MB")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_ignore_empty": True,
        "extra": "ignore"
    }
    
    @property
    def allowed_file_types(self) -> List[str]:
        """Get allowed file types as a list."""
        return ["pdf", "docx", "txt"]


# Global settings instance
settings = Settings()