# app/main.py
from pprint import pprint

from app.core.checkpoints import list_checkpoint_ids, get_checkpoint_by_id
from app.core.state import LearningState
from app.core.graph import build_graph


def select_checkpoint_cli() -> str:
    ids = list_checkpoint_ids()
    print("Available checkpoints:")
    for idx, cp_id in enumerate(ids, start=1):
        print(f"  {idx}. {cp_id}")

    while True:
        choice = input("Select a checkpoint by number: ").strip()
        if not choice.isdigit():
            print("Please enter a number.")
            continue
        i = int(choice)
        if 1 <= i <= len(ids):
            return ids[i - 1]
        print("Invalid choice. Try again.")


def run_checkpoint(cp_id: str):
    cp = get_checkpoint_by_id(cp_id)
    print(f"\n=== Running checkpoint {cp['id']} - {cp['title']} ===\n")

    # NOTE: cp_key is used instead of checkpoint_id
    initial_state: LearningState = {
        "cp_key": cp["id"],
        "checkpoint": cp,
        "trace": [],
    }

    app = build_graph()
    final_state = app.invoke(initial_state)

    print("\n=== FINAL STATE ===")
    print(f"Checkpoint: {final_state.get('cp_key')}")
    print(f"Context source: {final_state.get('context_source', 'unknown')}")
    print(f"Relevance score: {final_state.get('context_relevance_score', 0.0)} / 5")
    print(f"Validator feedback: {final_state.get('context_validation_feedback', '')}")
    print("\nTrace:")
    for line in final_state.get("trace", []):
        print(" -", line)


if __name__ == "__main__":
    cp_id = select_checkpoint_cli()
    run_checkpoint(cp_id)
