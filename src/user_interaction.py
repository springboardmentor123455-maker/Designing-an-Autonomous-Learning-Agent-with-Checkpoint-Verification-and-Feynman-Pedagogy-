"""
User Interaction Module for Learning Agent System

This module handles interactive user question answering, collecting user responses,
and managing the question-answer session.
"""

import logging
from typing import Dict, List, Optional, Tuple
from .models import GeneratedQuestion

logger = logging.getLogger(__name__)

def display_question(question: GeneratedQuestion, question_num: int, total_questions: int) -> None:
    """Display a question to the user in a formatted manner."""
    print("\n" + "="*70)
    print(f"📝 QUESTION {question_num}/{total_questions}")
    print("="*70)
    print(f"\n{question['question']}\n")
    
    # Display options for MCQ
    if question['type'] == 'mcq' and question.get('options'):
        print("OPTIONS:")
        for option in question['options']:
            print(f"  {option}")
        print()

def get_user_answer(question: GeneratedQuestion) -> str:
    """
    Get answer from user for a question.
    
    Args:
        question: The question to answer
        
    Returns:
        User's answer as string
    """
    try:
        if question['type'] == 'mcq':
            while True:
                answer = input("Your answer (A/B/C/D or full text): ").strip()
                if answer:
                    # Accept single letter or full text
                    if len(answer) == 1 and answer.upper() in ['A', 'B', 'C', 'D']:
                        return answer.upper()
                    elif answer:
                        return answer
                print("❌ Please provide a valid answer")
        else:
            # Open-ended question
            print("💭 Your answer (press Enter twice when done):")
            lines = []
            empty_count = 0
            
            while True:
                line = input()
                if not line:
                    empty_count += 1
                    if empty_count >= 2:  # Two empty lines to finish
                        break
                else:
                    empty_count = 0
                    lines.append(line)
            
            answer = "\n".join(lines).strip()
            
            if not answer:
                print("⚠️ Empty answer submitted. This will receive a low score.")
                confirm = input("Submit empty answer? (y/n): ").strip().lower()
                if confirm != 'y':
                    return get_user_answer(question)  # Retry
            
            return answer
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Question skipped by user")
        return ""
    except Exception as e:
        logger.error(f"Error getting user answer: {e}")
        return ""

def collect_user_answers(questions: List[GeneratedQuestion]) -> List[Dict[str, str]]:
    """
    Collect answers from user for all questions.
    
    Args:
        questions: List of questions to answer
        
    Returns:
        List of question-answer pairs
    """
    print("\n" + "🎓"*35)
    print("UNDERSTANDING VERIFICATION - ANSWER THE QUESTIONS")
    print("🎓"*35)
    print(f"\nYou will be asked {len(questions)} questions.")
    print("• For multiple choice: Enter A, B, C, or D")
    print("• For open-ended: Type your answer and press Enter twice when done")
    print("• Press Ctrl+C to skip a question (will receive 0 score)")
    print("\nLet's begin!\n")
    
    answers = []
    
    for i, question in enumerate(questions, 1):
        display_question(question, i, len(questions))
        
        answer = get_user_answer(question)
        
        answers.append({
            "question_id": question.get("question_id", f"q_{i}"),
            "question": question["question"],
            "question_type": question["type"],
            "user_answer": answer,
            "correct_answer": question.get("correct_answer", ""),
            "options": question.get("options", [])
        })
        
        if answer:
            print(f"\n✅ Answer recorded: {answer[:100]}{'...' if len(answer) > 100 else ''}")
        else:
            print(f"\n⚠️ No answer provided (will score 0)")
    
    print("\n" + "="*70)
    print(f"✅ All {len(questions)} questions answered!")
    print("="*70)
    
    return answers

def display_score_feedback(score_percentage: float, meets_threshold: bool, 
                          verification_results: List[Dict]) -> None:
    """
    Display score and feedback to the user.
    
    Args:
        score_percentage: Overall percentage score
        meets_threshold: Whether 70% threshold was met
        verification_results: Detailed results for each question
    """
    print("\n" + "📊"*35)
    print("ASSESSMENT RESULTS")
    print("📊"*35)
    
    print(f"\n🎯 OVERALL SCORE: {score_percentage:.1f}%")
    print(f"🎯 THRESHOLD: 70%")
    
    if meets_threshold:
        print(f"\n✅ PASSED! You scored {score_percentage:.1f}% (≥70% required)")
        print("🎉 Excellent work! Ready to progress to the next checkpoint.")
    else:
        print(f"\n❌ NEEDS IMPROVEMENT: You scored {score_percentage:.1f}% (<70% required)")
        print("📚 Don't worry! We'll help you understand the concepts better.")
    
    print("\n" + "-"*70)
    print("DETAILED BREAKDOWN:")
    print("-"*70)
    
    for i, result in enumerate(verification_results, 1):
        score = result["score"]
        emoji = "✅" if score >= 0.7 else "❌"
        
        print(f"\n{emoji} Question {i}: {score*100:.0f}%")
        print(f"   Q: {result.get('question', 'N/A')[:80]}...")
        print(f"   Your Answer: {result.get('learner_answer', 'N/A')[:80]}...")
        
        if result.get('feedback'):
            print(f"   💬 Feedback: {result['feedback']}")
    
    print("\n" + "="*70)

def ask_retry_confirmation() -> bool:
    """
    Ask user if they want to retry after Feynman teaching.
    
    Returns:
        True if user wants to retry, False otherwise
    """
    print("\n" + "-"*70)
    print("Would you like to retry the questions after reviewing the explanations?")
    print("-"*70)
    
    while True:
        choice = input("\nRetry questions? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False
        else:
            print("❌ Please enter 'y' for yes or 'n' for no")
