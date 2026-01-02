from graph import build_graph, LearningState
from checkpoints import CHECKPOINTS


def main():
    app = build_graph()

    results = [] 
    checkpoint_indices = [0, 1, 2, 3, 4]

    print("============================================================")
    print("        AUTONOMOUS LEARNING AGENT – MILESTONE 1")
    print("============================================================\n")

    for idx in checkpoint_indices:
        cp = CHECKPOINTS[idx]
        print("\n------------------------------------------------------------")
        print(f">>> EVALUATING CHECKPOINT: {cp.topic}")
        print("------------------------------------------------------------")

        initial_state: LearningState = {"checkpoint_index": idx}

        final_state = app.invoke(initial_state)
        results.append({
            "topic": cp.topic,
            "data_source": final_state.get("data_source", "Unknown"),
            "retrieval_mode": final_state.get("retrieval_mode", "Unknown"),
            "score": final_state.get("relevance_score", 0),
            "status": final_state.get("status", "UNKNOWN"),
        })
    print("\n\n============================================================")
    print("                 FINAL SYSTEM PERFORMANCE REPORT")
    print("============================================================")
    print(f"{'Checkpoint Module':25} | {'Data Source':18} | {'Retrieval':12} | {'Rel. Score':10} | {'Status':10}")
    print("-" * 100)
    for r in results:
        print(
            f"{r['topic'][:25]:25} | "
            f"{r['data_source'][:18]:18} | "
            f"{r['retrieval_mode'][:12]:12} | "
            f"{str(r['score']) + '/5':10} | "
            f"{r['status']:10}"
        )
    print("============================================================")
    print("\n(Note: Final scores are calibrated to 5/5 when the raw model score ≥ 4.)")


if __name__ == "__main__":
    main()
