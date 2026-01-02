"""
LangSmith configuration and tracing utilities.

This module handles LangSmith integration for monitoring and tracing
the Learning Agent System workflow and LLM operations.
"""

import os
import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps
import asyncio
from langsmith import Client, trace
from langchain_core.tracers import LangChainTracer

logger = logging.getLogger(__name__)

class LangSmithConfig:
    """LangSmith configuration and setup."""
    
    def __init__(self):
        self.enabled = os.getenv("LANGSMITH_TRACING_ENABLED", "true").lower() == "true"
        self.api_key = os.getenv("LANGCHAIN_API_KEY")
        self.project = os.getenv("LANGCHAIN_PROJECT", "Learning-Agent-System")
        self.endpoint = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
        self.client: Optional[Client] = None
        
        if self.enabled:
            self._setup_langsmith()
    
    def _setup_langsmith(self):
        """Setup LangSmith client and environment."""
        try:
            if not self.api_key:
                logger.warning("LangSmith API key not found. Tracing will be disabled.")
                self.enabled = False
                return
            
            # Set environment variables for LangChain
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = self.api_key
            os.environ["LANGCHAIN_PROJECT"] = self.project
            os.environ["LANGCHAIN_ENDPOINT"] = self.endpoint
            
            # Initialize LangSmith client with error handling
            self.client = Client(api_url=self.endpoint, api_key=self.api_key)
            
            # Test API connection and project access
            try:
                # Try to list projects to validate API key
                projects = list(self.client.list_projects(limit=1))
                logger.info(f"✅ LangSmith API connection verified")
                
                # If using 'default' project, ensure it exists by creating a test run
                if self.project == "default":
                    logger.info(f"✅ LangSmith tracing enabled for project: {self.project}")
                else:
                    # Try to create project if it doesn't exist
                    try:
                        self.client.create_project(project_name=self.project)
                        logger.info(f"✅ Created new LangSmith project: {self.project}")
                    except Exception as create_error:
                        logger.warning(f"Could not create project '{self.project}': {create_error}")
                        logger.info("Falling back to 'default' project")
                        self.project = "default"
                        os.environ["LANGCHAIN_PROJECT"] = "default"
                
                logger.info(f"✅ LangSmith tracing enabled for project: {self.project}")
                
            except Exception as api_error:
                logger.error(f"LangSmith API validation failed: {api_error}")
                logger.warning("LangSmith tracing will be disabled")
                self.enabled = False
                return
            
        except Exception as e:
            logger.error(f"Failed to setup LangSmith: {e}")
            self.enabled = False
    
    def create_tracer(self) -> Optional[LangChainTracer]:
        """Create a LangChain tracer for workflow monitoring."""
        if not self.enabled:
            return None
            
        try:
            return LangChainTracer(project_name=self.project)
        except Exception as e:
            logger.error(f"Failed to create LangChain tracer: {e}")
            return None

# Global LangSmith configuration
langsmith_config = LangSmithConfig()

def trace_workflow_node(node_name: str):
    """Decorator to trace LangGraph workflow nodes."""
    def decorator(func: Callable):
        if not langsmith_config.enabled:
            return func
            
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                with trace(
                    name=f"workflow_node_{node_name}",
                    metadata={
                        "node_type": "workflow_node",
                        "node_name": node_name,
                        "project": langsmith_config.project
                    }
                ) as run_tree:
                    try:
                        # Extract state information for tracing
                        if args and hasattr(args[0], 'get'):
                            state = args[0]
                            run_tree.metadata.update({
                                "workflow_step": state.get("workflow_step", "unknown"),
                                "checkpoint_id": state.get("current_checkpoint", {}).get("id", "unknown")
                            })
                        
                        result = await func(*args, **kwargs)
                        
                        # Add result information
                        if isinstance(result, dict):
                            run_tree.outputs = {
                                "workflow_step": result.get("workflow_step"),
                                "errors": result.get("errors", []),
                                "success": len(result.get("errors", [])) == 0
                            }
                        
                        return result
                        
                    except Exception as e:
                        run_tree.end(error=str(e))
                        logger.error(f"Error in workflow node {node_name}: {e}")
                        raise
            
            except Exception as tracing_error:
                # If tracing fails, log but continue execution
                logger.warning(f"LangSmith tracing failed for node {node_name}: {tracing_error}")
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def trace_llm_operation(operation_name: str):
    """Decorator to trace LLM operations and calls."""
    def decorator(func: Callable):
        if not langsmith_config.enabled:
            return func
            
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with trace(
                name=f"llm_operation_{operation_name}",
                metadata={
                    "operation_type": "llm_operation", 
                    "operation_name": operation_name,
                    "project": "Learning-Agent-System"
                }
            ) as run_tree:
                try:
                    # Add input information
                    if len(args) > 1:
                        run_tree.inputs = {
                            "prompt_length": len(str(args[1])) if len(args) > 1 else 0,
                            "function": func.__name__
                        }
                    
                    result = await func(*args, **kwargs)
                    
                    # Add output information
                    if isinstance(result, (list, dict)):
                        run_tree.outputs = {
                            "result_type": type(result).__name__,
                            "result_length": len(result) if hasattr(result, '__len__') else 0
                        }
                    elif isinstance(result, str):
                        run_tree.outputs = {
                            "result_type": "string",
                            "result_length": len(result)
                        }
                    
                    return result
                    
                except Exception as e:
                    run_tree.end(error=str(e))
                    logger.error(f"Error in LLM operation {operation_name}: {e}")
                    raise
        
        return wrapper
    return decorator

def trace_document_retrieval(query: str, documents: list):
    """Trace document search and retrieval operations."""
    if not langsmith_config.enabled:
        return
        
    try:
        with trace(
            name="document_retrieval",
            metadata={
                "operation_type": "document_retrieval",
                "project": "Learning-Agent-System"
            }
        ) as run_tree:
            run_tree.inputs = {
                "search_query": query,
                "query_length": len(query)
            }
            run_tree.outputs = {
                "documents_found": len(documents),
                "total_content_length": sum(len(doc.get("content", "")) for doc in documents if isinstance(doc, dict))
            }
    except Exception as e:
        logger.error(f"Error tracing document retrieval: {e}")

def get_langsmith_callbacks():
    """Get LangSmith callbacks for LangChain operations."""
    if not langsmith_config.enabled:
        return []
    
    tracer = langsmith_config.create_tracer()
    return [tracer] if tracer else []