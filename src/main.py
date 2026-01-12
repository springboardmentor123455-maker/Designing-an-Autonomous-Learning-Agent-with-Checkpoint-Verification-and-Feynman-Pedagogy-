from checkpoint import Checkpoint
import time

def demo_workflow(cp: Checkpoint):
    print(f"\n=== Starting Checkpoint {cp.id}: {cp.title} ===")
    print("1) Gathering context...")
    time.sleep(0.3)
    print("2) Processing context (chunking + embeddings) ... [simulated]")
    time.sleep(0.3)
    print("3) Generating questions...")
    time.sleep(0.3)
    print("4) Verifying answers...")
    time.sleep(0.3)
    print(f"Checkpoint '{cp.title}' complete (demo).")

if __name__ == "__main__":
    cp = Checkpoint(1, "Intro to Checkpoints", "Learn workflow basics", 0.7)
    demo_workflow(cp)
