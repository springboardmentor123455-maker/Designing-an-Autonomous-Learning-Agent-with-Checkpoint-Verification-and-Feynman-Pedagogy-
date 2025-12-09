"""Test the complete learning workflow."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.checkpoint import Checkpoint
from src.models.state import create_initial_state
from src.graph.learning_graph import create_learning_graph


def main():
    """Test the complete workflow."""
    print("=" * 60)
    print("TESTING COMPLETE WORKFLOW")
    print("=" * 60)
    print()
    
    # Create a test checkpoint
    checkpoint = Checkpoint(
        topic="Python Variables",
        objectives=[
            "Understand variable assignment",
            "Learn about variable types"
        ],
        difficulty_level="beginner"
    )
    print(f"✓ Created checkpoint: {checkpoint.topic}")
    
    # Create initial state with user notes
    user_notes = """
    Variables store data in Python. You assign values using the = operator.
    Python has dynamic typing, so variables can hold different types of data.
    """
    state = create_initial_state(checkpoint, user_notes)
    print("✓ Initialized state with user notes")
    
    # Create and execute the learning graph
    graph = create_learning_graph()
    print("✓ Created learning graph")
    
    print()
    print("-" * 60)
    print("EXECUTING WORKFLOW...")
    print("-" * 60)
    
    result = graph.invoke(state)
    
    print()
    print("-" * 60)
    print("WORKFLOW RESULTS")
    print("-" * 60)
    print(f"Current Stage: {result['current_stage']}")
    print(f"Gathered Contexts: {len(result['gathered_contexts'])}")
    print(f"Context Valid: {result['context_valid']}")
    print(f"Retry Count: {result['retry_count']}")
    
    if result["error"]:
        print(f"❌ Error: {result['error']}")
        return False
    
    print()
    print("✅ Workflow completed successfully!")
    
    # Show a sample of gathered context
    if result["gathered_contexts"]:
        print()
        print("Sample gathered context:")
        context = result["gathered_contexts"][0]
        print(f"  Source: {context.source}")
        print(f"  Relevance: {context.relevance_score}")
        print(f"  Content preview: {context.content[:100]}...")
    
    print()
    print("=" * 60)
    print("✅ WORKFLOW TEST PASSED")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
