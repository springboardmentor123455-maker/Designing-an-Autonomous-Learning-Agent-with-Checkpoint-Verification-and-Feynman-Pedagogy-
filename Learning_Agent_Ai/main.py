from checkpoint_1 import CHECKPOINTS
from graph_workflow import workflow
from langgraph.types import Command, Interrupt
from state import LearningState

# ======================================================
# CONFIG
# ======================================================
THREAD_ID = "cli-thread-1"
config = {"configurable": {"thread_id": THREAD_ID}}

# ======================================================
# SELECT CHECKPOINT
# ======================================================
print("\nAvailable Checkpoints:\n")
for i, cp in enumerate(CHECKPOINTS):
    print(f"{i + 1}. {cp['topic']}")

idx = int(input("\nSelect checkpoint number: ")) - 1
checkpoint = CHECKPOINTS[idx]

print(f"\n📌 Selected: {checkpoint['topic']}\n")

notes = input("Enter your notes (press Enter to skip): ").strip()

# ======================================================
# INITIAL STATE
# ======================================================
state = LearningState(
    checkpoint=checkpoint,
    user_Notes=notes if notes else None,

    answers=[],
    questions=[],

    max_iteration=2,
    context_iteration=0,
    feynman_iteration=0,

    gether_context="",
    context_evalution=None,

    chunks=[],
    vectore_semalirty=[],
    score_percentage=[],

    gaps_list={},
    gaps="",
    feynman_explanation=None,

    passed=False,
)
max_itera = state["max_iteration"]
attempt = state["feynman_iteration"]
# ======================================================
# START GRAPH (STREAM)
# ======================================================
# python Learning_Agent_Ai/main.py
while True :
    print("\n🚀 Starting learning flow...\n")
    
    stream = workflow.stream(state, config=config)

    interrupt_payload = None
    final_state = state
    while True:
        if final_state['feynman_explanation']:
            print("\n🧠 Feynman Explanation:\n")
            print(final_state["feynman_explanation"])
        for event in stream:
            print(event)  # 🔍 DEBUG (safe to keep)

            if "__interrupt__" in event:
                raw_interrupt = event["__interrupt__"]

                # 🔑 FIX: unwrap tuple if needed
                if isinstance(raw_interrupt, tuple):
                    interrupt_payload = raw_interrupt[0]
                else:
                    interrupt_payload = raw_interrupt
                break

        # ======================================================
        # HUMAN-IN-THE-LOOP
        # ======================================================
        if interrupt_payload:
            print("\n⏸ Graph paused for human input\n")

            # IMPORTANT: your interrupt key is "question"
            # questions = interrupt_payload.get("question", [])
            if isinstance(interrupt_payload, Interrupt):
                payload = interrupt_payload.value
            elif isinstance(interrupt_payload, dict):
                payload = interrupt_payload
            else:
                payload = {}

            questions = payload.get("question", [])

            if not questions:
                print("❌ No questions found in interrupt payload")
                exit(1)

            print("❓ Assessment Questions:\n")

            answers = []
            for i, q in enumerate(questions, start=1):
                print(f"Q{i}. {q}")
                ans = input("Your answer: ")
                answers.append(ans)

            # ==================================================
            # RESUME GRAPH WITH ANSWERS
            # ==================================================
            print("\n✅ Submitting answers...\n")

            stream = workflow.stream(
                Command(
                    resume={
                        "approved": "yes",
                        "answers": answers,
                    }
                ),
                config=config,
            )

            for event in stream:
                print(event)  # 🔍 DEBUG

                if "__end__" in event:
                    final_state = event["__end__"]
                    break
                for value in event.values():
                    if isinstance(value, dict):
                        final_state = value

        # ======================================================
        # FINAL RESULT
        # ======================================================
        if final_state is None:
            print("\n❌ Graph did not complete.")
            exit(1)

        print("\n📊 Evaluation Result\n")

        scores = final_state.get("score_percentage", [])
        if scores:
            avg = sum(scores) / len(scores)
            print(f"Average Score: {avg:.2f}%")

        if final_state.get("passed"):
            print("\n🎉 CHECKPOINT PASSED!")
            break
            
        
        print("\n❌ CHECKPOINT NOT PASSED")    
        if state is None:
            raise RuntimeError("STATE BECAME NONE — LOGIC ERROR")  
        print("STATE KEY" , state.keys())

        if final_state.get("feynman_iteration", 0) < state["max_iteration"]:
            # 🔁 Continue Feynman loop
            # state = LearningState(**final_state)
            # state = state.update(final_state)
            # state = LearningState.model_validate(final_state)
            final_state  = state

            continue
        break
    # ================= MAX ITERATION HIT =================

    print("\n⛔ Maximum Feynman iterations reached.")

    choice = input(
        "🔄 Try again from start checkpoint? (y/n): "
    ).strip().lower()
    if choice == "y":
        print("\n♻️ Restarting checkpoint...\n")
        state['feynman_iteration'] = 0
        state['context_iteration'] = 0
        state['answers'] = []
        state['feynman_explanation'] = ""
        continue

    print("\n🛑 Learning stopped.")
    break

print("\n✅ Done.\n")