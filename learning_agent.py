#!/usr/bin/env python3
"""
Unified Learning Agent System - Main Entry Point

This is the main entry point for the modular Learning Agent System that combines 
Milestone 1 (Material Collection & Summarization) and Milestone 2 (Context Processing 
& Understanding Verification) functionalities.

The system is now split into modular components:
- models.py: Type definitions and state models
- context_processor.py: Text processing and embeddings
- llm_service.py: LLM integration and scoring
- workflow_nodes.py: All workflow node functions
- workflow.py: Workflow creation and routing
- main.py: Main execution logic
- sample_data.py: Sample checkpoints and materials

Usage:
    python learning_agent.py [--interactive]

Features:
- Material collection and summarization (Milestone 1)
- Context processing with embeddings (Milestone 2)  
- Question generation and understanding verification (Milestone 2)
- 70% threshold logic with conditional routing (Milestone 2)
- Complete workflow integration
"""

import logging
import sys
from pathlib import Path
import io

# Configure logging with Unicode support for Windows
def create_unicode_stream_handler():
    """Create a StreamHandler that can handle Unicode characters on Windows"""
    try:
        # Try to create a handler with UTF-8 encoding
        handler = logging.StreamHandler()
        if sys.platform.startswith('win'):
            # On Windows, wrap stdout to handle Unicode
            handler.stream = io.TextIOWrapper(
                sys.stdout.buffer, 
                encoding='utf-8', 
                errors='replace'
            )
        return handler
    except Exception:
        # Fallback to regular handler
        return logging.StreamHandler()

def sanitize_log_message(message):
    """Remove or replace Unicode characters that might cause encoding issues"""
    if sys.platform.startswith('win'):
        # Replace problematic emojis with text equivalents
        emoji_replacements = {
            '🚀': '[START]',
            '📚': '[MATERIALS]', 
            '📝': '[SUMMARY]',
            '🎯': '[TARGET]',
            '📖': '[COLLECT]',
            '📄': '[PROCESS]',
            '🔄': '[PROCESSING]',
            '❓': '[QUESTION]',
            '✅': '[SUCCESS]',
            '⚖️': '[EVALUATE]',
            '📊': '[SCORE]',
            '🏗️': '[BUILD]',
            '🎉': '[COMPLETE]',
            '⚠️': '[WARNING]',
            '❌': '[FAIL]',
            '🛤️': '[PATH]',
            '💡': '[TIP]',
            '🔍': '[SEARCH]',
            '📋': '[LIST]',
            '📈': '[STATS]',
            '🌟': '[FEATURE]',
            '🎓': '[LEARN]'
        }
        for emoji, replacement in emoji_replacements.items():
            message = message.replace(emoji, replacement)
    return message

# Custom formatter that sanitizes messages on Windows
class UnicodeFormatter(logging.Formatter):
    def format(self, record):
        try:
            # Sanitize the message on Windows
            if hasattr(record, 'msg'):
                record.msg = sanitize_log_message(str(record.msg))
            if hasattr(record, 'args') and record.args:
                # Handle format strings that expect numeric values
                sanitized_args = []
                for arg in record.args:
                    if isinstance(arg, str):
                        # Try to convert to int for %d formats
                        if arg.isdigit():
                            sanitized_args.append(int(arg))
                        else:
                            # Try to extract numeric part from strings like "200 OK"
                            import re
                            match = re.search(r'\b(\d+)\b', arg)
                            if match:
                                sanitized_args.append(int(match.group(1)))
                            else:
                                sanitized_args.append(sanitize_log_message(str(arg)))
                    else:
                        sanitized_args.append(arg)
                record.args = tuple(sanitized_args)
            return super().format(record)
        except Exception:
            # Fallback to basic formatting if sanitization fails
            return f"{record.levelname}: {record.getMessage()}"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        create_unicode_stream_handler(),
        logging.FileHandler("learning_agent.log", mode="w", encoding="utf-8")
    ]
)

# Disable noisy third-party library logging that causes format errors
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("ollama").setLevel(logging.WARNING)
logging.getLogger("langchain").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)

# Apply Unicode formatter to all handlers
for handler in logging.getLogger().handlers:
    handler.setFormatter(UnicodeFormatter("%(asctime)s - %(levelname)s - %(message)s"))

# Load environment variables for LangSmith
from dotenv import load_dotenv
load_dotenv()

# Check for dependencies and import main components
try:
    from src.main import main
    # Import key functions to maintain backward compatibility
    from src.sample_data import create_sample_checkpoint, create_sample_materials
    from src.workflow import create_unified_workflow
    from src.main import run_learning_session, interactive_mode
    # Initialize LangSmith configuration
    from src.langsmith_config import langsmith_config
    
    if langsmith_config.enabled:
        print("✅ LangSmith tracing enabled")
    else:
        print("⚠️ LangSmith tracing disabled")
        
except ImportError as e:
    print(f"Missing dependencies or modules. Install with: pip install -r requirements.txt")
    print(f"Error: {e}")
    sys.exit(1)

if __name__ == "__main__":
    main()