import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"

from graph import build_graph
from checkpoints import CHECKPOINTS


def run_single_checkpoint():
    print("\n" + "=" * 30)
    print(" AUTONOMOUS LEARNING AGENT ")
    print("=" * 30)

    print("\nAvailable Learning Checkpoints:\n")
    for cid, cp in CHECKPOINTS.items():
        print(f"  {cid}. {cp['topic']}")

    checkpoint_id = input("\nSelect a checkpoint ID (1–5):\n> ").strip()

    user_notes = input(
        "\n(Optional) Paste your notes for this topic.\n"
        "Press Enter to skip:\n> "
    )

    print("\n--- Running Learning Pipeline ---\n")

    app = build_graph()

    initial_state = {
        "selected_cp_id": checkpoint_id,
        "user_notes": user_notes,
    }

    final_state = app.invoke(initial_state)

    checkpoint = final_state.get("checkpoint", {})
    questions = final_state.get("questions", [])
    understanding = final_state.get("score_percent", 0.0)
    relevance = final_state.get("relevance_score", 0.0)
    attempts = final_state.get("attempts", 0)

    status = "PASSED (Proceed)" if understanding >= 70 else "FAILED (Halt)"

    print("\n" + "=" * 30)
    print(" LEARNING EVALUATION SUMMARY ")
    print("=" * 30)

    print(f"Checkpoint      : {checkpoint.get('topic', 'N/A')}")
    print(f"Context Score   : {relevance}/5")
    print(f"Attempts Used   : {attempts}")
    print(f"Understanding   : {understanding:.2f}%")
    print(f"Status          : {'✅ ' if understanding >= 70 else '❌ '} {status}")

    print("\nGenerated Verification Questions:")
    for i, q in enumerate(questions, 1):
        print(f"  Q{i}. {q}")

    print("\nSession complete.\n")


if __name__ == "__main__":
    run_single_checkpoint()
