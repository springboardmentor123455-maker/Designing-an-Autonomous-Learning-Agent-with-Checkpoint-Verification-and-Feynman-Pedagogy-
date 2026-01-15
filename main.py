from data import CHECKPOINTS
from graph import build_graph
from models import AgentState
import time
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_next_checkpoint(current_cp_id: str):
    """
    Simulate a linear progression logic (cp1 -> cp2 -> cp3 -> cp4).
    """
    if current_cp_id == "cp1": return "cp2"
    if current_cp_id == "cp2": return "cp3"       
    if current_cp_id == "cp3": return "cp4"
    return None

def get_previous_checkpoint(current_cp_id: str):
    """
    Reverse linear progression logic (cp2 -> cp1).
    """
    if current_cp_id == "cp2": return "cp1"
    if current_cp_id == "cp3": return "cp2"
    if current_cp_id == "cp4": return "cp3"
    return None

 
def run_session():
    clear_screen()
    print("\n=== AUTONOMOUS LEARNING AGENT ===")
    print("Welcome to your adaptive learning session.")
    
    # Initial Checkpoint Selection
    print("Available checkpoints:", ", ".join(CHECKPOINTS.keys()))
    current_cp_id = input("\nWhich checkpoint do you want to start with? (Default: cp1)\n> ").strip() or "cp1"
    
    while True:
        clear_screen()
        print(f"\n=== MODULE: {current_cp_id.upper()} ===")
        
        # User Notes Input
        user_notes = input(
            f"\n[Optional] Paste notes for {current_cp_id} (or Press Enter to skip):\n> "
        )

        app = build_graph()

        initial_state: AgentState = {
            "selected_checkpoint": current_cp_id,
            "user_notes": user_notes,
            "attempts": 0,
            "relevance_score": 0.0,
            "loop_count": 0, # Reset loop count for new checkpoint
        }

        # Run the Graph
        print(f"\n--- Starting Module: {current_cp_id} ---")
        final_state = app.invoke(initial_state)

        # Print Final Status
        quiz_questions = final_state.get("quiz_questions", [])
        score = final_state.get("quiz_score", 0.0)
        result = final_state.get("quiz_result", "UNKNOWN")
        
        print("\n\n=== FINAL RESULTS ===")
        print(f"Total Questions: {len(quiz_questions)}")
        print(f"Quiz Score: {score:.1f}%")
        print(f"Status: {result}")

        # Detailed Review Logic
        answers = final_state.get("quiz_answers", {})
        if quiz_questions and answers:
            print("\n=== QUIZ REVIEW ===")
            for i, q in enumerate(quiz_questions):
                user_ans = answers.get(i, "N/A")
                correct_ans = q.get("correct_option", "A")
                explanation = q.get("explanation", "No explanation provided.")
                
                print(f"\nQ{i+1}: {q['question']}")
                print(f"Your Answer: {user_ans}")
                
                if user_ans == correct_ans:
                    print(f"✅ Correct!")
                else:
                    print(f"❌ Incorrect. Correct Answer: {correct_ans}")
                
                print(f"Explanation: {explanation}")
                print("-" * 40)
        
        input("\n[Press Enter to continue checking progression...]")

        # Navigation Logic
        print("\n[Navigation]")
        next_cp = get_next_checkpoint(current_cp_id)
        prev_cp = get_previous_checkpoint(current_cp_id)
        
        options = []
        valid_keys = []
        
        # Options available based on Pass/Fail and position
        if result == "PASSED":
             if next_cp:
                 options.append(f"[N]ext ({next_cp})")
                 valid_keys.append('n')
        else:
            options.append("[R]etry")
            valid_keys.append('r')
            
        if prev_cp:
            options.append(f"[P]revious ({prev_cp})")
            valid_keys.append('p')
            
        options.append("[Q]uit")
        valid_keys.append('q')
        
        prompt_str = ", ".join(options)
        
        while True:
            choice = input(f"Choose action: {prompt_str}\n> ").strip().lower()
            
            if choice == 'n' and 'n' in valid_keys:
                current_cp_id = next_cp
                break
            elif choice == 'r' and 'r' in valid_keys:
                # Retry: just break to loop again with same current_cp_id
                break
            elif choice == 'p' and 'p' in valid_keys:
                current_cp_id = prev_cp
                break
            elif choice == 'q':
                print("Session Ended. Good job!")
                return # Exit function
            else:
                print("Invalid choice. Try again.")
            

if __name__ == "__main__":
    run_session()
