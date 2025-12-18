"""
Main execution and demo functions for the Learning Agent System.

This module contains the core execution logic, interactive modes, and 
demonstration functions that bring together all components of the system.
"""

import asyncio
import logging
import sys
from typing import Optional, Dict, Any, List
from .models import LearningAgentState, Checkpoint, Material
from .workflow import create_unified_workflow
from .sample_data import create_sample_checkpoint, create_sample_materials
from .interactive import (
    display_welcome, select_checkpoint, display_question, 
    display_results, get_user_evaluation, display_system_metrics
)

logger = logging.getLogger(__name__)

async def run_learning_session(checkpoint: Optional[Checkpoint] = None, 
                              materials: Optional[List[Material]] = None) -> Dict[str, Any]:
    """Run a complete learning session."""
    
    logger.info("🚀 UNIFIED LEARNING AGENT - MILESTONES 1 & 2")
    logger.info("=" * 60)
    
    try:
        # Use provided or create sample data
        if checkpoint is None:
            checkpoint = create_sample_checkpoint()
        if materials is None:
            materials = create_sample_materials()
        
        # Create workflow (already compiled)
        compiled_workflow = create_unified_workflow()
        
        # Initialize state
        initial_state: LearningAgentState = {
            "current_checkpoint": checkpoint,
            "collected_materials": materials,
            "summary": "",
            "milestone1_score": 0.0,
            "processed_context": [],
            "generated_questions": [],
            "verification_results": [],
            "score_percentage": 0.0,
            "meets_threshold": False,
            "workflow_step": "initialized",
            "workflow_history": [],
            "errors": []
        }
        
        logger.info(f"📚 Checkpoint: {checkpoint['title']}")
        logger.info(f"📖 Materials: {len(materials)} items")
        
        # Run the workflow
        logger.info("\n🔄 Executing unified workflow...")
        logger.info("-" * 40)
        
        result = await compiled_workflow.ainvoke(initial_state)
        
        # Display results
        logger.info("\n📊 LEARNING SESSION RESULTS")
        logger.info("=" * 60)
        
        # Workflow progress
        logger.info(f"🛤️  Workflow Path: {' → '.join(result['workflow_history'])}")
        logger.info(f"📍 Final Status: {result['workflow_step']}")
        
        # Milestone 1 results
        logger.info(f"\n📋 MILESTONE 1 RESULTS:")
        logger.info(f"   📚 Materials Collected: {len(result['collected_materials'])}")
        logger.info(f"   📝 Summary Generated: {len(result.get('summary', ''))} characters")
        logger.info(f"   ⭐ Milestone 1 Score: {result.get('milestone1_score', 0):.2f}/4.0")
        
        # Milestone 2 results
        logger.info(f"\n🧠 MILESTONE 2 RESULTS:")
        logger.info(f"   🔄 Context Chunks: {len(result.get('processed_context', []))}")
        logger.info(f"   ❓ Questions Generated: {len(result.get('generated_questions', []))}")
        logger.info(f"   ✅ Verification Results: {len(result.get('verification_results', []))}")
        logger.info(f"   📊 Overall Score: {result.get('score_percentage', 0):.1f}%")
        logger.info(f"   🎯 Meets Threshold: {'✅ YES' if result.get('meets_threshold') else '❌ NO'}")
        
        # Final outcome
        if result.get("meets_threshold"):
            logger.info(f"\n🎉 SUCCESS: Checkpoint completed with {result.get('score_percentage', 0):.1f}%!")
        else:
            logger.info(f"\n📚 NEEDS WORK: Score {result.get('score_percentage', 0):.1f}% < 70%, Feynman teaching recommended")
        
        # Error reporting
        errors = result.get("errors", [])
        if errors:
            logger.info(f"\n⚠️  Issues Encountered: {len(errors)}")
            for error in errors[:3]:  # Show first 3 errors
                logger.info(f"   • {error}")
        
        logger.info(f"\n✨ Learning session completed!")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Learning session failed: {e}")
        logger.exception("Full error details:")
        return {"error": str(e)}

async def interactive_mode():
    """Run the system in interactive mode with user questions."""
    display_welcome()
    
    # Checkpoint selection
    selected_checkpoint = select_checkpoint()
    if not selected_checkpoint:
        return
    
    # Run the learning session with user interaction
    print(f"\n🚀 Starting learning session for: {selected_checkpoint['title']}")
    print("⏳ Processing learning materials...")
    
    # Initialize state for interactive session
    initial_state = {
        "current_checkpoint": selected_checkpoint,
        "collected_materials": create_sample_materials(),
        "workflow_history": [],
        "errors": [],
        "workflow_step": "starting",
        "milestone1_score": 0.0,
        "score_percentage": 0.0,
        "meets_threshold": False,
        "user_mode": "interactive"
    }
    
    try:
        # Create and run workflow
        workflow = create_unified_workflow()
        result = await workflow.ainvoke(initial_state)
        
        # Interactive question answering if questions were generated
        if result.get('generated_questions'):
            print(f"\n🎯 Time for your assessment!")
            print(f"You will answer {len(result['generated_questions'])} questions.")
            input("\nPress Enter when ready to begin...")
            
            # Collect user answers
            user_answers = []
            for i, question in enumerate(result['generated_questions'], 1):
                answer = display_question(question, i, len(result['generated_questions']))
                user_answers.append({
                    "question": question,
                    "user_answer": answer,
                    "timestamp": "interactive_mode"
                })
            
            # Process answers and update results
            result['user_answers'] = user_answers
            result = await process_user_answers(result)
        
        # Display comprehensive results
        display_results(result, selected_checkpoint['title'])
        
        # Get user evaluation feedback
        feedback = get_user_evaluation()
        
        # Display system performance metrics
        display_system_metrics(feedback)
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error during interactive session: {e}")
        logger.error(f"Interactive mode error: {e}")

async def process_user_answers(result: Dict) -> Dict:
    """Process user answers and calculate scores."""
    if not result.get('user_answers'):
        return result
    
    from .llm_service import LLMService
    llm_service = LLMService()
    
    verification_results = []
    total_score = 0
    
    for answer_data in result['user_answers']:
        question = answer_data['question']
        user_answer = answer_data['user_answer']
        
        if question['type'] == 'multiple_choice':
            # Simple MCQ scoring
            correct_answer = question.get('correct_answer', 'A')
            is_correct = user_answer.upper() == correct_answer
            score = 1.0 if is_correct else 0.0
            
            verification_results.append({
                "question": question,
                "user_answer": user_answer,
                "score": score * 100,  # Convert to percentage
                "is_correct": is_correct
            })
        else:
            # Use LLM for open-ended scoring
            try:
                score_result = await llm_service.score_answer(
                    question['question'],
                    user_answer,
                    question.get('expected_elements', [])
                )
                # Extract numeric score from result dictionary
                score = score_result.get('score', 0.0) if isinstance(score_result, dict) else score_result
                verification_results.append({
                    "question": question,
                    "user_answer": user_answer,
                    "score": score * 100  # Convert to percentage
                })
            except Exception as e:
                logger.error(f"Error scoring answer: {e}")
                # Default scoring
                verification_results.append({
                    "question": question,
                    "user_answer": user_answer,
                    "score": 75.0  # Default score
                })
        
        total_score += verification_results[-1]['score']
    
    # Calculate final metrics
    avg_score = total_score / len(verification_results) if verification_results else 0
    meets_threshold = avg_score >= 70.0
    
    # Update result
    result['verification_results'] = verification_results
    result['score_percentage'] = avg_score
    result['meets_threshold'] = meets_threshold
    result['workflow_step'] = 'checkpoint_completed' if meets_threshold else 'needs_improvement'
    
    return result

def main():
    """Main entry point."""
    
    print("🎯 UNIFIED LEARNING AGENT SYSTEM")
    print("Combining Milestone 1 (Material Collection) + Milestone 2 (Understanding Verification)")
    print("=" * 80)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Run non-interactive demo mode
        asyncio.run(run_learning_session())
    else:
        # Run interactive mode by default
        asyncio.run(interactive_mode())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n👋 Session interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        logger.exception("Main execution error")