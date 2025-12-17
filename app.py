"""
Main application entry point for the Autonomous Learning Agent.
Provides CLI interface for testing and running the learning system.
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data.checkpoints.sample_checkpoints import get_checkpoint_titles
from src.tools.llm_integration import llm_service
from config.settings import settings


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('learning_agent.log')
        ]
    )


async def test_llm_connection():
    """Test the LLM connection and display available models."""
    print("Testing LLM connection...")
    
    try:
        success = await llm_service.initialize()
        
        if success:
            print("✅ LLM connection successful!")
            print(f"   Model: {settings.ollama_model}")
            print(f"   Base URL: {settings.ollama_base_url}")
            
            # Test a simple generation
            response = await llm_service.ollama_manager.generate_text(
                "Say 'Hello, I am ready to help with learning!' in a friendly way."
            )
            print(f"   Test response: {response[:100]}...")
            
        else:
            print("❌ LLM connection failed!")
            print("   Please ensure:")
            print("   1. Ollama is installed and running")
            print("   2. The specified model is available")
            print("   3. The base URL is correct")
            
            # Show available models
            available_models = llm_service.ollama_manager.get_available_models()
            if available_models:
                print(f"   Available models: {available_models}")
            
    except Exception as e:
        print(f"❌ LLM test failed: {e}")


def list_sample_checkpoints():
    """List all available sample checkpoints."""
    print("\nAvailable Sample Checkpoints:")
    print("-" * 40)
    
    titles = get_checkpoint_titles()
    for i, title in enumerate(titles, 1):
        print(f"{i:2d}. {title}")


async def main():
    """Main CLI entry point."""
    
    parser = argparse.ArgumentParser(
        description="Autonomous Learning Agent - Milestone 1 Implementation"
    )
    
    parser.add_argument(
        "--action",
        choices=["test-llm", "list-checkpoints", "evaluate", "quick-test", "demo"],
        default="demo",
        help="Action to perform (default: demo - quick single checkpoint test)"
    )
    
    parser.add_argument(
        "--checkpoint",
        type=str,
        help="Checkpoint title for quick-test action"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    print("🎓 Autonomous Learning Agent - Milestone 1")
    print("=" * 50)
    
    if args.action == "test-llm":
        await test_llm_connection()
        
    elif args.action == "list-checkpoints":
        list_sample_checkpoints()
        
    elif args.action == "evaluate":
        print("\nRunning full Milestone 1 evaluation (8 checkpoints)...")
        print("⏱️  This will take 5-10 minutes (tests all checkpoints with web search)...")
        print("💡 For quick testing, use: python app.py --action demo\n")
        
        # Ask for confirmation
        response = input("Continue with full evaluation? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Evaluation cancelled. Use --action demo for quick testing.")
            return
        
        print("\n🎯 For complete Milestone 1 evaluation, use:")
        print("   python milestone1.py")
        print("\nThis provides:")
        print("- System verification")
        print("- Component testing") 
        print("- Workflow demonstration")
        print("- Multi-checkpoint evaluation")
            
    elif args.action == "quick-test":
        if not args.checkpoint:
            print("❌ Please specify a checkpoint title with --checkpoint")
            list_sample_checkpoints()
            return
        
        print(f"\nRunning quick test for: {args.checkpoint}")
        
        print(f"\n🎯 For testing checkpoint '{args.checkpoint}', use:")
        print("   python milestone1.py")
        print("\nThis provides comprehensive checkpoint testing.")
    
    elif args.action == "demo":
        print("\n🚀 Running quick demo (single checkpoint test)...")
        print("This will test the basic functionality quickly.\n")
        
        print("\n🎯 For quick demo, use:")
        print("   python milestone1.py")
        print("\nThis provides:")
        print("- System verification")
        print("- Quick component testing")
        print("- Workflow demonstration")
        print("- Results in ~10 minutes")


async def cleanup_and_exit():
    """Cleanup resources before exit."""
    try:
        from src.tools.llm_integration import llm_service_manager
        await llm_service_manager.cleanup()
    except Exception as e:
        logging.warning(f"Cleanup error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        logging.error(f"Application error: {e}", exc_info=True)
    finally:
        # Cleanup resources
        try:
            asyncio.run(cleanup_and_exit())
        except Exception:
            pass  # Ignore cleanup errors during shutdown