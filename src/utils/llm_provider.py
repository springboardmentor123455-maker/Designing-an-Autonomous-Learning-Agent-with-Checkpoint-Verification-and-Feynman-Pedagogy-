"""LLM provider initialization and configuration."""
import os
from typing import Optional
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


def get_llm(
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    provider: Optional[str] = None
) -> ChatOpenAI:
    """
    Initialize and return an LLM instance.
    
    Supports both GitHub Models (recommended for free tier) and OpenAI.
    
    Args:
        model_name: Name of the model to use. If None, uses MODEL_NAME from .env
        temperature: Temperature for response generation (0-1)
        max_tokens: Maximum tokens in response
        provider: 'github' or 'openai'. If None, uses MODEL_PROVIDER from .env
        
    Returns:
        ChatOpenAI instance configured with the specified provider
        
    Example:
        # Using GitHub Models (free tier)
        llm = get_llm(model_name="openai/gpt-4.1-mini", provider="github")
        
        # Using OpenAI
        llm = get_llm(model_name="gpt-4o-mini", provider="openai")
    """
    # Get configuration from environment or use defaults
    if model_name is None:
        model_name = os.getenv("MODEL_NAME", "openai/gpt-4.1-mini")
    
    if provider is None:
        provider = os.getenv("MODEL_PROVIDER", "github").lower()
    
    # Configure based on provider
    if provider == "github":
        # GitHub Models configuration
        api_key = os.getenv("GITHUB_TOKEN")
        if not api_key:
            raise ValueError(
                "GITHUB_TOKEN not found in environment variables. "
                "Please add it to your .env file. "
                "Get your token from: https://github.com/settings/tokens"
            )
        
        # GitHub Models use OpenAI-compatible API
        base_url = "https://models.inference.ai.azure.com"
        
        # Clean model name - remove provider prefix if present
        if "/" in model_name:
            model_name = model_name.split("/")[1]
        
        # Map common model names to GitHub Models naming
        model_mapping = {
            "gpt-4.1-mini": "gpt-4o-mini",
            "o4-mini": "gpt-4o-mini",
            "o1-mini": "gpt-4o-mini"
        }
        model_name = model_mapping.get(model_name, model_name)
        
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    elif provider == "openai":
        # OpenAI configuration
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please add it to your .env file."
            )
        
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    elif provider == "groq":
        # Groq configuration (FREE and FAST for students!)
        if not GROQ_AVAILABLE:
            raise ImportError(
                "langchain-groq not installed. Install it with: pip install langchain-groq"
            )
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables. "
                "Get FREE API key from: https://console.groq.com/"
            )
        
        # Map to Groq models
        groq_models = {
            "gpt-4o-mini": "llama-3.3-70b-versatile",
            "gpt-4o": "llama-3.3-70b-versatile",
            "llama-3.3-70b-versatile": "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768": "mixtral-8x7b-32768"
        }
        groq_model = groq_models.get(model_name, "llama-3.3-70b-versatile")
        
        return ChatGroq(
            model=groq_model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    elif provider == "azure":
        # Azure OpenAI configuration (BEST for production and students with Azure access)
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", model_name)
        
        if not api_key:
            raise ValueError(
                "AZURE_OPENAI_API_KEY not found in environment variables. "
                "Add it to your .env file."
            )
        
        if not azure_endpoint:
            raise ValueError(
                "AZURE_OPENAI_ENDPOINT not found in environment variables. "
                "Add it to your .env file (e.g., https://your-resource.openai.azure.com/)"
            )
        
        # Check if this is an o1/o3 series model (they don't support temperature/max_tokens)
        is_reasoning_model = any(x in deployment_name.lower() for x in ['o1', 'o3', 'gpt-5'])
        
        if is_reasoning_model:
            # o1/o3/gpt-5 series models only support temperature=1 (default)
            return AzureChatOpenAI(
                azure_deployment=deployment_name,
                api_key=api_key,
                azure_endpoint=azure_endpoint,
                api_version=api_version
                # No temperature or max_tokens for reasoning models
            )
        else:
            return AzureChatOpenAI(
                azure_deployment=deployment_name,
                api_key=api_key,
                azure_endpoint=azure_endpoint,
                api_version=api_version,
                temperature=temperature,
                max_tokens=max_tokens
            )
    
    else:
        raise ValueError(f"Unsupported provider: {provider}. Use 'github', 'openai', 'groq', or 'azure'")


def get_validation_llm(
    model_name: Optional[str] = None,
    provider: Optional[str] = None
) -> ChatOpenAI:
    """
    Get an LLM optimized for fast validation and scoring tasks.
    
    Uses gpt-4o-mini by default for cost-effective, fast scoring.
    Lower temperature for deterministic numeric outputs.
    
    Args:
        model_name: Name of the model to use
        provider: Provider to use
        
    Returns:
        ChatOpenAI instance optimized for validation
    """
    if provider is None:
        provider = os.getenv("MODEL_PROVIDER", "azure").lower()
    
    if model_name is None:
        # Try to use a separate validation model if configured
        model_name = os.getenv("VALIDATION_MODEL", "gpt-4o-mini")
    
    return get_llm(
        model_name=model_name,
        temperature=0.1,  # Very low temperature for consistent scoring
        provider=provider
    )


def get_reasoning_llm(
    model_name: Optional[str] = None,
    provider: Optional[str] = None
) -> ChatOpenAI:
    """
    Get an LLM optimized for reasoning tasks (lower temperature).
    
    Args:
        model_name: Name of the model to use
        provider: 'github' or 'openai'
        
    Returns:
        ChatOpenAI instance with reasoning-optimized settings
    """
    if provider is None:
        provider = os.getenv("MODEL_PROVIDER", "github").lower()
    
    if model_name is None:
        # Use standard model for reasoning (o1-mini requires special API version)
        model_name = "gpt-4o-mini"
    
    return get_llm(
        model_name=model_name,
        temperature=0.3,  # Lower temperature for more focused reasoning
        provider=provider
    )


def get_creative_llm(
    model_name: Optional[str] = None,
    provider: Optional[str] = None
) -> ChatOpenAI:
    """
    Get an LLM optimized for creative tasks (higher temperature).
    Useful for generating analogies and Feynman-style explanations.
    
    Args:
        model_name: Name of the model to use
        provider: 'github' or 'openai'
        
    Returns:
        ChatOpenAI instance with creative-optimized settings
    """
    return get_llm(
        model_name=model_name,
        temperature=0.9,  # Higher temperature for more creative outputs
        provider=provider
    )
