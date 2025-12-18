"""
Interactive functions for the Learning Agent System.

This module handles user interactions, checkpoint selection, and 
question answering functionality.
"""

import sys
from typing import Dict, List, Optional, Tuple
from .models import Checkpoint, GeneratedQuestion
from .sample_data import create_multiple_checkpoints

def display_welcome():
    """Display welcome message and system introduction."""
    print("\n" + "="*60)
    print("🎓 INTERACTIVE LEARNING AGENT SYSTEM")
    print("="*60)
    print("\nWelcome to the Learning Agent System!")
    print("This system will guide you through personalized learning checkpoints")
    print("with adaptive questioning and evaluation.")
    print("\nFeatures:")
    print("• Multiple checkpoint selection")
    print("• 3-5 adaptive questions per checkpoint")
    print("• Multiple choice and open-ended questions")
    print("• Real-time scoring and feedback")
    print("• 70% threshold-based progression")
    print("\n" + "-"*60)

def select_checkpoint() -> Optional[Checkpoint]:
    """Allow user to select a learning checkpoint."""
    checkpoints = create_multiple_checkpoints()
    
    print("\n📚 AVAILABLE LEARNING CHECKPOINTS:")
    print("-" * 50)
    
    for i, checkpoint in enumerate(checkpoints, 1):
        print(f"\n{i}. {checkpoint['title']}")
        print(f"   📝 {checkpoint['description']}")
        print(f"   🎯 Requirements: {len(checkpoint['requirements'])} learning objectives")
    
    print("\n" + "-" * 50)
    
    while True:
        try:
            choice = input(f"\nSelect checkpoint (1-{len(checkpoints)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                print("\n👋 Thank you for using the Learning Agent System!")
                return None
                
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(checkpoints):
                selected = checkpoints[choice_idx]
                print(f"\n✅ Selected: {selected['title']}")
                print(f"📋 Learning Objectives:")
                for req in selected['requirements']:
                    print(f"   • {req}")
                
                confirm = input("\nProceed with this checkpoint? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    return selected
                else:
                    continue
            else:
                print("❌ Invalid selection. Please try again.")
                
        except ValueError:
            print("❌ Please enter a valid number or 'q' to quit.")

def display_question(question: GeneratedQuestion, question_num: int, total: int) -> str:
    """Display a question and get user's answer."""
    print(f"\n" + "="*50)
    print(f"❓ QUESTION {question_num}/{total}")
    print("="*50)
    print(f"\n{question['question']}")
    
    if question['type'] == 'multiple_choice':
        print(f"\n📝 Type: Multiple Choice")
        print(f"💡 Difficulty: {question.get('difficulty', 'medium').title()}")
        print("\nOptions:")
        for option in question.get('options', []):
            print(f"   {option}")
        
        while True:
            answer = input("\nYour answer (A, B, C, or D): ").strip().upper()
            if answer in ['A', 'B', 'C', 'D']:
                return answer
            print("❌ Please select A, B, C, or D.")
            
    else:  # open_ended
        print(f"\n📝 Type: Open-Ended")
        print(f"💡 Difficulty: {question.get('difficulty', 'medium').title()}")
        print("\nExpected topics to cover:")
        for element in question.get('expected_elements', [])[:3]:
            print(f"   • {element}")
        
        print("\n💭 Take your time to provide a thoughtful answer...")
        answer = input("\nYour answer: ").strip()
        
        while len(answer) < 10:
            print("❌ Please provide a more detailed answer (at least 10 characters).")
            answer = input("Your answer: ").strip()
            
        return answer

def display_results(results: Dict, checkpoint_title: str):
    """Display comprehensive results and evaluation metrics."""
    print(f"\n" + "="*60)
    print("📊 LEARNING ASSESSMENT RESULTS")
    print("="*60)
    print(f"\n🎯 Checkpoint: {checkpoint_title}")
    print(f"📅 Session completed successfully")
    
    print(f"\n📈 PERFORMANCE SUMMARY:")
    print("-" * 40)
    print(f"📋 Questions Answered: {len(results.get('verification_results', []))}")
    print(f"📊 Overall Score: {results.get('score_percentage', 0):.1f}%")
    print(f"🎯 Threshold Status: {'✅ PASSED' if results.get('meets_threshold', False) else '❌ BELOW THRESHOLD'}")
    print(f"⚡ Minimum Required: 70.0%")
    
    print(f"\n🔍 QUESTION BREAKDOWN:")
    print("-" * 40)
    
    verification_results = results.get('verification_results', [])
    for i, result in enumerate(verification_results, 1):
        question_type = result.get('question', {}).get('type', 'unknown')
        score = result.get('score', 0)
        
        print(f"Question {i}: {score:.1f}% ({'MCQ' if question_type == 'multiple_choice' else 'Open-Ended'})")
        
        if question_type == 'multiple_choice':
            user_answer = result.get('user_answer', 'N/A')
            correct_answer = result.get('question', {}).get('correct_answer', 'N/A')
            is_correct = user_answer == correct_answer
            print(f"   Your Answer: {user_answer} | Correct: {correct_answer} | {'✅' if is_correct else '❌'}")
        else:
            print(f"   Response Quality: {score:.1f}%")
    
    print(f"\n🏆 FINAL OUTCOME:")
    print("-" * 40)
    if results.get('meets_threshold', False):
        print("🎉 Congratulations! You have successfully completed this checkpoint.")
        print("✨ You demonstrate strong understanding of the learning objectives.")
        print("🚀 Ready to proceed to the next checkpoint!")
    else:
        print("📚 Additional study recommended before proceeding.")
        print("💡 Focus on areas where scores were below 70%.")
        print("🔄 Feel free to retry this checkpoint when ready.")
    
    print(f"\n🎓 Thank you for using the Learning Agent System!")
    print("="*60)

def get_user_evaluation() -> Dict[str, any]:
    """Get user feedback on question relevance and system performance."""
    print(f"\n" + "="*50)
    print("🔍 SYSTEM EVALUATION FEEDBACK")
    print("="*50)
    print("\nHelp us improve the Learning Agent System!")
    
    feedback = {}
    
    # Question Relevance
    print(f"\n1. Question Relevance Assessment:")
    print("How relevant were the generated questions to the learning material?")
    print("Scale: 1 (Not relevant) - 5 (Very relevant)")
    
    while True:
        try:
            relevance = int(input("Your rating (1-5): ").strip())
            if 1 <= relevance <= 5:
                feedback['question_relevance'] = relevance
                break
            print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Scoring Accuracy
    print(f"\n2. Scoring Accuracy Assessment:")
    print("How accurately did the system score your answers?")
    print("Scale: 1 (Very inaccurate) - 5 (Very accurate)")
    
    while True:
        try:
            accuracy = int(input("Your rating (1-5): ").strip())
            if 1 <= accuracy <= 5:
                feedback['scoring_accuracy'] = accuracy
                break
            print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Additional Comments
    print(f"\n3. Additional Comments (optional):")
    comments = input("Any suggestions or feedback: ").strip()
    if comments:
        feedback['comments'] = comments
    
    # Calculate metrics
    feedback['question_relevance_percentage'] = (relevance / 5) * 100
    feedback['scoring_accuracy_percentage'] = (accuracy / 5) * 100
    
    print(f"\n✅ Thank you for your feedback!")
    print(f"📊 Question Relevance: {feedback['question_relevance_percentage']:.1f}%")
    print(f"📊 Scoring Accuracy: {feedback['scoring_accuracy_percentage']:.1f}%")
    
    return feedback

def display_system_metrics(feedback: Dict):
    """Display system performance metrics based on feedback."""
    print(f"\n" + "="*50)
    print("📈 SYSTEM PERFORMANCE METRICS")
    print("="*50)
    
    question_relevance = feedback.get('question_relevance_percentage', 0)
    scoring_accuracy = feedback.get('scoring_accuracy_percentage', 0)
    
    print(f"\n🎯 Success Criteria Evaluation:")
    print("-" * 30)
    
    # Question Relevance (Target: >80%)
    relevance_status = "✅ PASSED" if question_relevance > 80 else "❌ NEEDS IMPROVEMENT"
    print(f"Question Relevance: {question_relevance:.1f}% (Target: >80%) {relevance_status}")
    
    # Scoring Accuracy (Target: >90%) 
    accuracy_status = "✅ PASSED" if scoring_accuracy > 90 else "❌ NEEDS IMPROVEMENT"
    print(f"Scoring Accuracy: {scoring_accuracy:.1f}% (Target: >90%) {accuracy_status}")
    
    # Overall System Performance
    overall_score = (question_relevance + scoring_accuracy) / 2
    overall_status = "✅ EXCELLENT" if overall_score > 85 else "⚠️ GOOD" if overall_score > 70 else "❌ NEEDS WORK"
    print(f"Overall Performance: {overall_score:.1f}% {overall_status}")
    
    print(f"\n💡 Recommendations:")
    if question_relevance <= 80:
        print("• Improve question generation algorithms")
        print("• Enhance context analysis for better relevance")
    if scoring_accuracy <= 90:
        print("• Refine answer evaluation criteria")
        print("• Add more sophisticated scoring mechanisms")
    if overall_score > 85:
        print("• System performing well - continue monitoring")
        print("• Consider adding advanced features")