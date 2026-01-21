from state import AgentState


def question_relevance(state: AgentState) -> AgentState:
    """
    Check whether generated questions are relevant to the checkpoint objectives.
    Marks each question as Relevant or Weak.
    """
    questions = state.get("questions", [])
    checkpoint = state.get("checkpoint")

    print("\n[question_relevance] Evaluating question relevance...")

    if not questions or not checkpoint:
        print("[question_relevance] No questions or checkpoint found.")
        return state

    objectives = " ".join(checkpoint["objectives"]).lower()

    relevant_count = 0
    total_questions = len(questions)

    for idx, q in enumerate(questions, start=1):
        # Simple heuristic relevance check
        is_relevant = any(
            keyword in q.lower()
            for keyword in objectives.split()
        )

        if is_relevant:
            relevant_count += 1
            print(f"  Q{idx}: Relevant (✔)")
        else:
            print(f"  Q{idx}: Weak (✘)")

    print(
        f"\nOverall Question Relevance: "
        f"{relevant_count} / {total_questions} questions relevant"
    )

    return state
