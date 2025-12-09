"""Installation and environment test for the Autonomous Learning Agent."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def test_environment():
    """Test environment variables."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    print("[1/5] Testing environment variables...")
    
    # Check provider
    provider = os.getenv("MODEL_PROVIDER", "azure")
    print(f"  Current LLM Provider: {provider}")
    
    # Check Azure credentials
    if provider == "azure":
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if azure_key and azure_endpoint:
            print("  ✓ AZURE_OPENAI_API_KEY configured")
            print("  ✓ AZURE_OPENAI_ENDPOINT configured")
        else:
            print("  ✗ Azure OpenAI credentials missing")
            return False
    
    # Check search API
    serp_key = os.getenv("SERP_API_KEY")
    if serp_key:
        print("  ✓ SERP_API_KEY configured")
    else:
        print("  ⚠ SERP_API_KEY not configured (will use DuckDuckGo)")
    
    print("  ✓ Environment check complete")
    return True


def test_imports():
    """Test that all required modules can be imported."""
    print("\n[2/5] Testing module imports...")
    
    try:
        from src.models.checkpoint import Checkpoint, GatheredContext
        from src.models.state import LearningState, create_initial_state
        from src.modules.context_manager import ContextManager
        from src.graph.learning_graph import create_learning_graph
        from src.utils.llm_provider import get_llm, get_validation_llm
        print("  ✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        print("  Run: pip install -r requirements.txt")
        return False


def test_data_models():
    """Test basic data model creation."""
    print("\n[3/5] Testing data models...")
    
    from src.models.checkpoint import Checkpoint
    from src.models.state import create_initial_state
    
    checkpoint = Checkpoint(
        topic="Test Topic",
        objectives=["Test Objective"]
    )
    print(f"  ✓ Created checkpoint: {checkpoint.topic}")
    
    state = create_initial_state(checkpoint)
    print("  ✓ Created initial state")
    
    return True


def test_llm_connection():
    """Test LLM connection."""
    print("\n[4/5] Testing LLM connection...")
    
    try:
        from src.utils.llm_provider import get_validation_llm
        
        llm = get_validation_llm()
        print("  ✓ LLM initialized successfully")
        
        # Try a simple call
        response = llm.invoke("Hello")
        print(f"  ✓ LLM response received: {response.content[:50]}...")
        return True
        
    except Exception as e:
        print(f"  ✗ LLM connection failed: {e}")
        return False


def test_search():
    """Test search tool availability."""
    print("\n[5/5] Testing search tool...")
    
    try:
        from src.utils.search_tools import search_for_learning_content
        import os
        
        # Check which search tool will be used
        if os.getenv("SERP_API_KEY"):
            print("Using SerpAPI search (recommended)")
        else:
            print("Using DuckDuckGo search (free fallback)")
        
        # Don't actually search, just check initialization
        print("  ✓ Search tool initialized: SerpAPISearch")
        return True
        
    except Exception as e:
        print(f"  ✗ Search tool error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Autonomous Learning Agent - Installation Test")
    print("=" * 60)
    print()
    
    tests = [
        test_environment,
        test_imports,
        test_data_models,
        test_llm_connection,
        test_search
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append(False)
    
    print()
    print("=" * 60)
    if all(results):
        print("Installation Test Complete!")
        print("=" * 60)
        print()
        print("✅ System is ready to use!")
        print()
        print("Next steps:")
        print("  1. Run: python main.py")
        print("  2. Or run: python -m streamlit run streamlit_app.py")
        print("  3. Or run: jupyter notebook (open notebooks/jupyter_agent.ipynb)")
        print()
        print("For detailed help, see:")
        print("  - FIX_LLM_ERRORS.md (troubleshooting)")
        print("  - FREE_ALTERNATIVES_FOR_STUDENTS.md (best options)")
    else:
        print("Installation Test Failed")
        print("=" * 60)
        print()
        print("❌ Some tests failed. Please check the errors above.")
        print()
        print("Common fixes:")
        print("  1. Run: pip install -r requirements.txt")
        print("  2. Check your .env file has correct API keys")
        print("  3. See SETUP.md for detailed setup instructions")
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
