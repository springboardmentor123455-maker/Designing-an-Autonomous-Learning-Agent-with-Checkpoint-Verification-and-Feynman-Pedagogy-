# main.py

from checkpoints import checkpoints
from context_gathering import gather_context


def validate_context(context, objectives):
    for obj in objectives:
        keyword = obj.split()[0].lower()
        if keyword not in context.lower():
            return False
    return True


def run_checkpoint(checkpoint, user_notes=None):
    print(f"\nStarting Checkpoint: {checkpoint['topic']}")

    gathered = gather_context(checkpoint["topic"], user_notes)
    print("Context Source:", gathered["source"])
    print("Context:", gathered["context"])

    is_valid = validate_context(
        gathered["context"],
        checkpoint["objectives"]
    )

    if is_valid:
        print("✅ Context is relevant to objectives")
    else:
        print("❌ Context is NOT relevant, re-fetch needed")

    return is_valid


if __name__ == "__main__":
    run_checkpoint(checkpoints[0])
