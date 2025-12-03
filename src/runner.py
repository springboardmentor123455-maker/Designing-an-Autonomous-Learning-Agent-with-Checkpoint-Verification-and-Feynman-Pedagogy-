# src/runner.py
from pathlib import Path
from src.nodes import start_checkpoint

CHECKS = ["ckpt_001", "ckpt_002"]
OUT = Path(__file__).parent / "results.csv"

def main():
    rows = []
    for ck in CHECKS:
        print(f"\n=== Running {ck} ===")
        res = start_checkpoint(ck, user_notes="Newton's second law states that force equals mass times acceleration (F = m a). Example: a 2 kg mass with 4 N force has acceleration 2 m/s^2.")  # empty notes -> web fallback
        cp = res.get("checkpoint")
        ctx = res.get("context", {})             
        val = res.get("validation", {})

        print("Topic:", cp.get("topic") if cp else "MISSING")
        print("Source:", ctx.get("source", "unknown"))
        print("Context snippet:\n", (ctx.get("context") or "")[:800])
        print("Validation:\n", val)

        rows.append({
            "checkpoint_id": ck,
            "topic": cp.get("topic") if cp else "",
            "gather_source": ctx.get("source", ""),
            "combined_score": val.get("combined_score"),
            "scale_1_5": val.get("scale_1_5"),
            "relevant": val.get("relevant"),
            "llm_note": val.get("note", "")
        })
    if rows:
        import csv
        with open(OUT, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print("\nResults saved to", OUT)
    else:
        print("No rows to save.")

if __name__ == "__main__":
    main()
