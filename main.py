"""Main entry point for the Autonomous Learning Agent."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.checkpoint import Checkpoint
from src.models.state import create_initial_state
from src.graph.learning_graph import create_learning_graph


def main():
    
    print("AUTONOMOUS LEARNING AGENT ")
    print()
    
    # Create a learning checkpoint
    checkpoint = Checkpoint(
        topic="Python Functions and Parameters",
        objectives=[
            "Understand function definition syntax",
            "Learn how to use function parameters",
            "Master return values and function calls"
        ]
    )
    
    print(f"📚 Learning Topic: {checkpoint.topic}")
    print("🎯 Objectives:")
    for i, obj in enumerate(checkpoint.objectives, 1):
        print(f"   {i}. {obj}")
    print()
    
    # User notes (simulating learner's existing knowledge)
    user_notes = """
    Functions in Python are defined using the 'def' keyword.
    They can take parameters and return values.
    Example: def greet(name): return f"Hello {name}"
    """
    
    print("📝 User Notes Provided:")
    print(user_notes.strip())
    print()
    
    # Initialize state
    print("-" * 70)
    print("INITIALIZING WORKFLOW...")
    print("-" * 70)
    print()
    
    state = create_initial_state(
        checkpoint=checkpoint,
        user_notes=user_notes
    )
    
    # Create workflow graph
    graph = create_learning_graph()
    
    print("✓ Workflow initialized")
    print("✓ Learning graph created")
    print()
    
    # Execute workflow
    print("-" * 70)
    print("EXECUTING LEARNING WORKFLOW...")
    print("-" * 70)
    print()
    
    try:
        result = graph.invoke(state)
        
        print()
        print("-" * 70)
        print("WORKFLOW RESULTS")
        print("-" * 70)
        print()
        
        # Display results
        print(f"Final Stage: {result['current_stage']}")
        print(f"Contexts Gathered: {len(result['gathered_contexts'])}")
        print(f"Context Validation: {'✅ Valid' if result.get('context_valid') else '❌ Invalid'}")
        print(f"Retry Attempts: {result['retry_count']}")
        
        # Show error if any
        if result.get("error"):
            print()
            print(f"  Error: {result['error']}")
            if "API key" in result['error'] or "GITHUB_TOKEN" in result['error']:
                print()
                print(" Note: Configure your .env file with API keys to enable full functionality.")
                print("   See SETUP.md for instructions.")
        
        # Show gathered contexts
        if result["gathered_contexts"]:
            print()
            print(f" Sample Gathered Context ({len(result['gathered_contexts'])} total):")
            print()
            for i, context in enumerate(result["gathered_contexts"][:3], 1):
                print(f"   {i}. Source: {context.source}")
                print(f"      Relevance: {context.relevance_score:.2f}")
                print(f"      Preview: {context.content[:80]}...")
                print()
        
        print("-" * 70)
        
        # Determine success
        if result["current_stage"] == "context_processed":
            print(" WORKFLOW COMPLETED SUCCESSFULLY")
            return 0
        elif result.get("error"):
            print("  WORKFLOW COMPLETED WITH ERRORS")
            return 1
        else:
            print("  WORKFLOW INCOMPLETE")
            return 1
            
    except Exception as e:
        print()
        print("-" * 70)
        print(f" WORKFLOW FAILED: {e}")
        print("-" * 70)
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        print()
        print("=" * 70)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("  Workflow interrupted by user")
        print("=" * 70)
        sys.exit(130)
    except Exception as e:
        print()
        print("=" * 70)
        print(f" FATAL ERROR: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)
