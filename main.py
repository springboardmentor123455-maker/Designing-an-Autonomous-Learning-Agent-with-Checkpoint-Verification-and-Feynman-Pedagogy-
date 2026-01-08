import sys
import os
from pathlib import Path


if sys.platform == 'win32':
    import codecs
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.checkpoint import Checkpoint
from src.models.state import create_initial_state
from src.graph.learning_graph import create_learning_graph


def main():
    
    print("=" * 70)
    print("AUTONOMOUS LEARNING AGENT - MILESTONE 4")
    print("=" * 70)
    print()
    
    # Create learning checkpoints (Milestone 4: Multiple checkpoints)
    checkpoints = [
        Checkpoint(
            topic="Python Functions and Parameters",
            objectives=[
                "Understand function definition syntax",
                "Learn how to use function parameters",
                "Master return values and function calls"
            ]
        ),
        Checkpoint(
            topic="Python Lists and Iteration",
            objectives=[
                "Understand list data structure",
                "Learn list methods and operations",
                "Master list iteration with loops"
            ]
        )
    ]
    
    print(f"Learning Path: {len(checkpoints)} Checkpoints")
    for i, cp in enumerate(checkpoints, 1):
        print(f"\n{i}. {cp.topic}")
        print("   Objectives:")
        for j, obj in enumerate(cp.objectives, 1):
            print(f"      {j}. {obj}")
    print()
    
    
    user_notes = """
    Functions in Python are defined using the 'def' keyword.
    They can take parameters and return values.
    Example: def greet(name): return f"Hello {name}"
    
    Lists in Python are ordered, mutable collections.
    They are created using square brackets: [1, 2, 3]
    Common methods include append(), remove(), pop(), and sort().
    You can iterate over lists using for loops: for item in my_list:
    """
    
    print("User Notes Provided:")
    print(user_notes.strip())
    print()
    
    # Initialize state (Milestone 4: Multiple checkpoints)
    print("-" * 70)
    print("INITIALIZING WORKFLOW...")
    print("-" * 70)
    print()
    
    state = create_initial_state(
        checkpoints=checkpoints,
        user_notes=user_notes
    )
    
    # Create workflow graph
    graph = create_learning_graph()
    
    print("Workflow initialized")
    print("Learning graph created")
    print()
    
    # Execute workflow
    print("-" * 70)
    print("EXECUTING LEARNING WORKFLOW")
    print("-" * 70)
    print()
    
    try:
        result = graph.invoke(state)
        
        print()
        print("-" * 70)
        print("WORKFLOW RESULTS")
        print("-" * 70)
        print()
        
        
        print(f"Final Stage: {result['current_stage']}")
        print(f"Total Checkpoints: {len(result['all_checkpoints'])}")
        print(f"Completed Checkpoints: {len(result['completed_checkpoints'])}")
        print(f"Contexts Gathered: {len(result['gathered_contexts'])}")
        print(f"Context Validation: {'Valid' if result.get('context_valid') else 'Invalid'}")
        
        
        if result.get("context_chunks"):
            print(f"Context Chunks Created: {len(result['context_chunks'])}")
        if result.get("vector_store"):
            print(f"Vector Store: Created")
        if result.get("questions"):
            print(f"Questions Generated: {len(result['questions'])}")
        if result.get("understanding_score") is not None:
            score = result["understanding_score"]
            passed = result.get("passed_checkpoint", False)
            status = "PASSED" if passed else "NEEDS IMPROVEMENT"
            print(f"Understanding Score: {score:.1%} - {status}")
            print(f"Passed Checkpoint: {'Yes (>= 70%)' if passed else 'No (< 70%)'}")
        
        # Milestone 3: Display Feynman Teaching results
        if result.get("feynman_explanations"):
            print()
            print("="*70)
            print("FEYNMAN TEACHING APPLIED")
            print("="*70)
            print(f"Number of Feynman Attempts: {result.get('feynman_attempts', 0)}")
            print(f"Explanations Generated: {len(result['feynman_explanations'])}")
            print()
            for i, exp in enumerate(result['feynman_explanations'], 1):
                print(f"\n[Explanation {i}] Concept: {exp['concept']}")
                print("-" * 60)
                print(exp['explanation'])
                print("-" * 60)
            print()
        
        print(f"Retry Attempts: {result['retry_count']}")
        
        # Show error if any
        if result.get("error"):
            print()
            print(f"Error: {result['error']}")
            if "API key" in result['error'] or "GITHUB_TOKEN" in result['error']:
                print()
                print("Note: Configure your .env file with API keys to enable full functionality.")
        
        
        if result.get("questions"):
            print()
            print(f"Generated Questions:")
            for q in result["questions"][:2]:  # Show first 2
                print(f"\n   Q{q['id']}: {q['question']}")
                print(f"Testing: {q['objective']}")
        
        print()
        print("-" * 70)
        
        # Determine success (Milestone 4)
        if result["current_stage"] in ["all_checkpoints_completed", "understanding_verified", "feynman_completed"]:
            print("WORKFLOW COMPLETED SUCCESSFULLY")
            print()
            
            # Milestone 4: Show completion stats
            completed = len(result.get('completed_checkpoints', []))
            total = len(result.get('all_checkpoints', []))
            
            if result["current_stage"] == "all_checkpoints_completed":
                print(f"✓ All checkpoints completed! ({completed}/{total})")
            elif result.get("passed_checkpoint"):
                print("✓ Current checkpoint passed with >= 70% score!")
            else:
                print("⚠ Current checkpoint did not pass after maximum Feynman attempts")
                print(f"  Final Score: {result.get('understanding_score', 0):.1%}")
                print(f"  Feynman Attempts Used: {result.get('feynman_attempts', 0)}")
            return 0
        elif result.get("error"):
            print("WORKFLOW COMPLETED WITH ERRORS")
            return 1
        else:
            print("WORKFLOW INCOMPLETE")
            return 1
            
    except Exception as e:
        print()
        print("-" * 70)
        print(f"WORKFLOW FAILED: {e}")
        print("-" * 70)
        import traceback
        traceback.print_exc()
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
        print("Workflow interrupted by user")
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
