"""
LLM integration using Ollama for local inference.
Provides a wrapper around Ollama for consistent LLM interactions.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from langchain_ollama import OllamaLLM, ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import LLMResult
from config.settings import settings

logger = logging.getLogger(__name__)


class OllamaManager:
    """Manages Ollama LLM integration with health checks and error handling."""
    
    def __init__(self, model_name: Optional[str] = None, base_url: Optional[str] = None):
        self.model_name = model_name or settings.ollama_model
        self.base_url = base_url or settings.ollama_base_url
        self._llm = None
        self._chat_llm = None
        self.is_available = False
    
    async def cleanup(self):
        """Cleanup resources and close connections."""
        try:
            if self._llm and hasattr(self._llm, 'client'):
                if hasattr(self._llm.client, 'close'):
                    await self._llm.client.close()
            if self._chat_llm and hasattr(self._chat_llm, 'client'):
                if hasattr(self._chat_llm.client, 'close'):
                    await self._chat_llm.client.close()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
        finally:
            self.is_available = False
    
    async def initialize(self) -> bool:
        """Initialize the Ollama connection and verify model availability."""
        try:
            # Initialize basic LLM
            self._llm = OllamaLLM(
                model=self.model_name,
                base_url=self.base_url,
                temperature=0.7,
                top_p=0.9,
            )
            
            # Initialize chat LLM
            self._chat_llm = ChatOllama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=0.7,
                top_p=0.9,
            )
            
            # Test connection
            await self.health_check()
            self.is_available = True
            logger.info(f"Ollama initialized successfully with model: {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            self.is_available = False
            return False
    
    async def health_check(self) -> bool:
        """Check if Ollama is running and the model is available."""
        try:
            if not self._llm:
                return False
            
            # Test with a simple prompt
            test_response = await self._llm.ainvoke("Hello, are you working?")
            return isinstance(test_response, str) and len(test_response) > 0
            
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text using the LLM."""
        if not self.is_available:
            raise RuntimeError("Ollama is not available. Please check your connection.")
        
        try:
            if system_prompt:
                # Use chat model for system prompts
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=prompt)
                ]
                
                # Configure temperature if provided
                llm = self._chat_llm
                if temperature is not None:
                    llm = ChatOllama(
                        model=self.model_name,
                        base_url=self.base_url,
                        temperature=temperature,
                        top_p=0.9,
                    )
                
                response = await llm.ainvoke(messages)
                return response.content
            else:
                # Use basic LLM
                llm = self._llm
                if temperature is not None:
                    llm = OllamaLLM(
                        model=self.model_name,
                        base_url=self.base_url,
                        temperature=temperature,
                        top_p=0.9,
                    )
                
                response = await llm.ainvoke(prompt)
                return response
                
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise
    
    async def generate_chat_response(
        self,
        messages: List[BaseMessage],
        temperature: Optional[float] = None
    ) -> str:
        """Generate a chat response given a list of messages."""
        if not self.is_available:
            raise RuntimeError("Ollama is not available. Please check your connection.")
        
        try:
            llm = self._chat_llm
            if temperature is not None:
                llm = ChatOllama(
                    model=self.model_name,
                    base_url=self.base_url,
                    temperature=temperature,
                    top_p=0.9,
                )
            
            response = await llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Chat response generation failed: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama."""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            return []
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []


class LLMService:
    """High-level service for LLM operations specific to the learning agent."""
    
    def __init__(self):
        self.ollama_manager = OllamaManager()
        self._initialized = False
    
    async def _ensure_initialized(self) -> bool:
        """Ensure the LLM service is initialized before use."""
        if not self._initialized:
            self._initialized = await self.ollama_manager.initialize()
        return self._initialized
    
    async def initialize(self) -> bool:
        """Initialize the LLM service."""
        return await self._ensure_initialized()
    
    async def generate_context_validation_prompt(
        self,
        context: str,
        checkpoint_objectives: List[str],
        max_length: int = 3000
    ) -> str:
        """Generate a prompt for validating context relevance."""
        objectives_text = "\n".join([f"- {obj}" for obj in checkpoint_objectives])
        
        # Truncate context if too long
        if len(context) > max_length:
            context = context[:max_length] + "..."
        
        prompt = f"""You are an expert educational content evaluator. Your task is to assess how relevant the provided context is to the learning objectives.

LEARNING OBJECTIVES:
{objectives_text}

CONTEXT TO EVALUATE:
{context}

Please evaluate this context and provide:
1. A relevance score from 1-5 (where 1=not relevant, 5=highly relevant)
2. A brief explanation of your scoring reasoning
3. Suggestions for improvement if the score is below 4

Respond in this exact format:
SCORE: [1-5]
REASONING: [Your explanation]
SUGGESTIONS: [Your suggestions, or "None needed" if score is 4 or 5]"""

        return prompt
    
    async def validate_context_relevance(
        self,
        context: str,
        checkpoint_objectives: List[str]
    ) -> Dict[str, Any]:
        """Validate context relevance and return structured results."""
        try:
            # Ensure LLM is initialized
            if not await self._ensure_initialized():
                return {
                    'score': 1.0,
                    'reasoning': 'LLM service not initialized properly',
                    'suggestions': 'Check Ollama connection and model availability',
                    'raw_response': ''
                }
            prompt = await self.generate_context_validation_prompt(context, checkpoint_objectives)
            
            system_prompt = "You are a careful and objective educational content evaluator. Be precise in your scoring and provide constructive feedback."
            
            response = await self.ollama_manager.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3  # Lower temperature for more consistent scoring
            )
            
            # Parse the response
            return self._parse_validation_response(response)
            
        except Exception as e:
            logger.error(f"Context validation failed: {e}")
            return {
                "score": 1.0,
                "reasoning": f"Validation failed due to error: {str(e)}",
                "suggestions": "Please check the LLM connection and try again",
                "raw_response": ""
            }
    
    def _parse_validation_response(self, response: str) -> Dict[str, Any]:
        """Parse the validation response into structured data."""
        result = {
            "score": 1.0,
            "reasoning": "Unable to parse response",
            "suggestions": "Please check the context and try again",
            "raw_response": response
        }
        
        try:
            lines = response.strip().split('\n')
            
            for line in lines:
                if line.startswith("SCORE:"):
                    score_text = line.replace("SCORE:", "").strip()
                    try:
                        result["score"] = float(score_text)
                    except ValueError:
                        # Try to extract number from text
                        import re
                        numbers = re.findall(r'\d+(?:\.\d+)?', score_text)
                        if numbers:
                            result["score"] = float(numbers[0])
                
                elif line.startswith("REASONING:"):
                    result["reasoning"] = line.replace("REASONING:", "").strip()
                
                elif line.startswith("SUGGESTIONS:"):
                    result["suggestions"] = line.replace("SUGGESTIONS:", "").strip()
            
            # Ensure score is within valid range
            result["score"] = max(1.0, min(5.0, result["score"]))
            
        except Exception as e:
            logger.warning(f"Failed to parse validation response: {e}")
        
        return result
    
    async def generate_search_queries(
        self,
        checkpoint_title: str,
        objectives: List[str],
        max_queries: int = 3
    ) -> List[str]:
        """Generate search queries for finding relevant context."""
        objectives_text = "\n".join([f"- {obj}" for obj in objectives])
        
        prompt = f"""Generate {max_queries} effective search queries to find educational content for this learning checkpoint:

CHECKPOINT: {checkpoint_title}

LEARNING OBJECTIVES:
{objectives_text}

Generate search queries that will find the most relevant educational content. Make them specific but not too narrow.

Respond with exactly {max_queries} search queries, one per line, without numbering or bullets:"""

        try:
            response = await self.ollama_manager.generate_text(
                prompt=prompt,
                system_prompt="You are an expert at creating effective search queries for educational content.",
                temperature=0.4
            )
            
            # Parse queries from response
            queries = [line.strip() for line in response.strip().split('\n') if line.strip()]
            
            # Ensure we have the right number of queries
            if len(queries) < max_queries:
                # Add a basic query if needed
                queries.append(f"{checkpoint_title} tutorial")
            
            return queries[:max_queries]
            
        except Exception as e:
            logger.error(f"Search query generation failed: {e}")
            # Fallback queries
            return [
                f"{checkpoint_title} tutorial",
                f"{checkpoint_title} explanation",
                f"learn {checkpoint_title}"
            ][:max_queries]


class LLMServiceManager:
    """Global LLM service manager with proper cleanup."""
    
    def __init__(self):
        self._service = None
    
    def get_service(self) -> LLMService:
        if self._service is None:
            self._service = LLMService()
        return self._service
    
    async def cleanup(self):
        if self._service and self._service.ollama_manager:
            await self._service.ollama_manager.cleanup()
        self._service = None

# Global LLM service manager
llm_service_manager = LLMServiceManager()
llm_service = llm_service_manager.get_service()