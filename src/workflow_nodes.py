"""
Workflow nodes for the Learning Agent System.

This module contains all the workflow node functions for both Milestone 1 and 
Milestone 2 operations, including initialization, material collection, context 
processing, question generation, and verification.
"""

import asyncio
import logging
from .models import LearningAgentState
from .context_processor import ContextProcessor
from .llm_service import LLMService
from .langsmith_config import trace_workflow_node, trace_document_retrieval

logger = logging.getLogger(__name__)

# Global instances - initialized when imported
context_processor = ContextProcessor()
llm_service = LLMService()

# ================================
# MILESTONE 1 NODES
# ================================

@trace_workflow_node("initialize")
async def initialize_node(state: LearningAgentState) -> LearningAgentState:
    """Initialize the learning session."""
    logger.info("🚀 Initializing learning session...")
    
    try:
        state["workflow_step"] = "initialized"
        state["workflow_history"].append("initialize")
        
        checkpoint = state["current_checkpoint"]
        logger.info(f"📚 Starting checkpoint: {checkpoint['title']}")
        logger.info(f"📝 Description: {checkpoint['description']}")
        logger.info(f"🎯 Requirements: {len(checkpoint['requirements'])} items")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in initialize_node: {e}")
        state["errors"].append(f"Initialization error: {str(e)}")
        return state

@trace_workflow_node("collect_materials")
async def collect_materials_node(state: LearningAgentState) -> LearningAgentState:
    """Collect learning materials with dynamic generation and validation."""
    logger.info("📚 Collecting learning materials...")
    
    try:
        state["workflow_step"] = "collecting_materials"
        
        checkpoint = state["current_checkpoint"]
        materials = []
        
        # PRIORITY 1: Check for user-uploaded notes
        user_notes_path = state.get("user_uploaded_notes_path")
        if user_notes_path:
            logger.info("📎 Processing user-uploaded notes...")
            from .document_processor import get_document_processor
            doc_processor = get_document_processor()
            
            # Process uploaded documents
            if isinstance(user_notes_path, str):
                user_notes_path = [user_notes_path]
            
            results = doc_processor.process_multiple_documents(user_notes_path)
            
            for result in results:
                if result['success']:
                    materials.append({
                        "id": f"user_upload_{result['file_name']}",
                        "title": f"User Notes: {result['file_name']}",
                        "content": result['content'],
                        "source": f"User Upload ({result['file_type'].upper()})",
                        "type": "user_notes"
                    })
                    logger.info(f"   ✅ {result['file_name']} ({result['content_length']} chars)")
        
        # PRIORITY 2: Generate dynamic materials (LLM + Web Search)
        logger.info("🤖 Generating dynamic learning materials...")
        from .dynamic_materials import get_materials_generator
        materials_gen = get_materials_generator()
        
        if materials:
            # Enhance user materials with generated content
            generated_materials = await materials_gen.enhance_user_materials(materials, checkpoint)
            materials = generated_materials
        else:
            # No user materials - generate comprehensive content
            generated_materials = await materials_gen.generate_comprehensive_materials(
                checkpoint, 
                use_web=True, 
                use_llm=True
            )
            materials = generated_materials
        
        logger.info(f"📖 Collected {len(materials)} total materials")
        
        # VALIDATION: Check relevance with retry mechanism
        logger.info("🔍 Validating material relevance...")
        from .context_validation import get_context_validator
        validator = get_context_validator()
        
        async def retry_gather_materials(cp):
            """Callback for validation retry."""
            logger.info("🔄 Gathering additional materials for validation retry...")
            return await materials_gen.generate_materials_from_web(cp)
        
        valid, validation_result, final_materials = await validator.validate_with_retry(
            materials,
            checkpoint,
            retry_callback=retry_gather_materials
        )
        
        # Store validation results
        state["materials_validation"] = validation_result
        state["collected_materials"] = final_materials
        
        # Trace document collection for LangSmith
        search_query = checkpoint["title"]
        trace_document_retrieval(search_query, final_materials)
        
        logger.info(f"📊 Final material count: {len(final_materials)}")
        logger.info(f"📊 Relevance score: {validation_result['average_score']:.2f}/5.0")
        
        for material in final_materials[:3]:  # Show first 3
            logger.info(f"   • {material.get('title', 'N/A')[:60]}...")
        
        state["workflow_history"].append("collect_materials")
        return state
        
    except Exception as e:
        logger.error(f"Error in collect_materials_node: {e}")
        state["errors"].append(f"Material collection error: {str(e)}")
        return state

@trace_workflow_node("summarize_materials")
async def summarize_materials_node(state: LearningAgentState) -> LearningAgentState:
    """Summarize collected materials."""
    logger.info("📝 Summarizing materials...")
    
    try:
        state["workflow_step"] = "summarizing"
        
        materials = state["collected_materials"]
        
        # Create comprehensive summary
        all_content = "\n\n".join([f"{mat['title']}: {mat['content']}" for mat in materials])
        
        # Generate summary using LLM
        try:
            summary_prompt = f"""
Summarize the following learning materials in 2-3 paragraphs, focusing on key concepts and main points:

{all_content}

Provide a clear, comprehensive summary that captures the essential information.
"""
            summary = await asyncio.to_thread(llm_service.llm.invoke, summary_prompt)
            state["summary"] = summary.strip()
        except Exception:
            # Fallback summary
            state["summary"] = f"Summary of {len(materials)} materials covering {state['current_checkpoint']['title']}. Key topics include the main concepts and requirements outlined in the learning objectives."
        
        logger.info(f"📄 Generated summary ({len(state['summary'])} characters)")
        
        state["workflow_history"].append("summarize_materials")
        return state
        
    except Exception as e:
        logger.error(f"Error in summarize_materials_node: {e}")
        state["errors"].append(f"Summarization error: {str(e)}")
        return state
@trace_workflow_node("evaluate_milestone1")
async def evaluate_milestone1_node(state: LearningAgentState) -> LearningAgentState:
    """Evaluate Milestone 1 completion."""
    logger.info("⚖️ Evaluating Milestone 1...")
    
    try:
        state["workflow_step"] = "milestone1_evaluation"
        
        # Scoring criteria
        materials_score = min(len(state["collected_materials"]) * 1.0, 2.0)  # Up to 2 points
        summary_score = min(len(state["summary"]) / 100.0, 1.5)  # Up to 1.5 points
        requirements_score = 0.5  # Base score for having requirements
        
        total_score = materials_score + summary_score + requirements_score
        state["milestone1_score"] = min(total_score, 4.0)  # Cap at 4.0
        
        logger.info(f"📊 Milestone 1 Score: {state['milestone1_score']:.2f}/4.0")
        logger.info(f"   • Materials: {materials_score:.1f}/2.0")
        logger.info(f"   • Summary: {summary_score:.1f}/1.5")
        logger.info(f"   • Requirements: {requirements_score:.1f}/0.5")
        
        state["workflow_history"].append("evaluate_milestone1")
        return state
        
    except Exception as e:
        logger.error(f"Error in evaluate_milestone1_node: {e}")
        state["errors"].append(f"Milestone 1 evaluation error: {str(e)}")
        return state

# ================================
# MILESTONE 2 NODES
# ================================

@trace_workflow_node("process_context")
async def process_context_node(state: LearningAgentState) -> LearningAgentState:
    """Process context with chunking and embeddings."""
    logger.info("🔄 Processing context...")
    
    try:
        state["workflow_step"] = "processing_context"
        
        # Combine all material content
        materials = state["collected_materials"]
        combined_content = "\n\n".join([mat["content"] for mat in materials])
        
        # Process context
        processed_context = await context_processor.process_context(
            combined_content, 
            state["current_checkpoint"]["id"]
        )
        
        state["processed_context"] = processed_context
        
        logger.info(f"📄 Processed {len(processed_context)} context chunks")
        for i, chunk in enumerate(processed_context[:3]):  # Show first 3
            logger.info(f"   • Chunk {i+1}: {chunk['text'][:100]}...")
        
        state["workflow_history"].append("process_context")
        return state
        
    except Exception as e:
        logger.error(f"Error in process_context_node: {e}")
        state["errors"].append(f"Context processing error: {str(e)}")
        return state

@trace_workflow_node("generate_questions")
async def generate_questions_node(state: LearningAgentState) -> LearningAgentState:
    """Generate questions from processed context."""
    logger.info("❓ Generating questions...")
    
    try:
        state["workflow_step"] = "generating_questions"
        
        processed_context = state["processed_context"]
        checkpoint = state["current_checkpoint"]
        
        # Generate questions using LLM
        questions = await llm_service.generate_questions(
            processed_context,
            checkpoint["requirements"]
        )
        
        state["generated_questions"] = questions
        
        logger.info(f"❓ Generated {len(questions)} questions")
        for i, question in enumerate(questions):
            logger.info(f"   {i+1}. {question['question']}")
        
        state["workflow_history"].append("generate_questions")
        return state
        
    except Exception as e:
        logger.error(f"Error in generate_questions_node: {e}")
        state["errors"].append(f"Question generation error: {str(e)}")
        return state

@trace_workflow_node("verify_understanding")
async def verify_understanding_node(state: LearningAgentState) -> LearningAgentState:
    """Verify understanding through interactive user question answering."""
    logger.info("✅ Verifying understanding...")
    
    try:
        state["workflow_step"] = "verifying_understanding"
        
        questions = state["generated_questions"]
        processed_context = state["processed_context"]
        
        if not questions:
            logger.warning("No questions available for verification")
            state["verification_results"] = []
            return state
        
        # Check if answers are already provided (from Streamlit UI)
        # If verification_results already exist, skip collection
        if state.get("verification_results"):
            logger.info("✓ Using pre-collected answers from UI")
            return state
        
        # Only collect answers interactively if running in CLI mode
        # In Streamlit, answers are collected by the UI and passed in state
        user_mode = state.get("user_mode", "cli")
        
        if user_mode == "streamlit":
            # Streamlit mode - questions are displayed in UI, don't collect here
            logger.info("📊 Questions ready for UI display (Streamlit mode)")
            # Return state with questions, let Streamlit handle answer collection
            return state
        
        # CLI mode - collect answers interactively
        from .user_interaction import collect_user_answers
        user_answers = collect_user_answers(questions)
        
        # Evaluate each answer
        verification_results = []
        
        for answer_data in user_answers:
            question_text = answer_data["question"]
            user_answer = answer_data["user_answer"]
            question_type = answer_data["question_type"]
            
            # For MCQ, check if answer matches correct answer
            if question_type == 'mcq':
                correct_answer = answer_data.get("correct_answer", "")
                
                # Direct match check
                if user_answer.upper() == correct_answer.upper():
                    score = 1.0
                    feedback = "Correct!"
                elif not user_answer:
                    score = 0.0
                    feedback = "No answer provided"
                else:
                    score = 0.0
                    feedback = f"Incorrect. The correct answer is {correct_answer}"
                
                scoring = {
                    "score": score,
                    "feedback": feedback,
                    "reasoning": feedback
                }
            else:
                # For open-ended, use LLM to evaluate
                if not user_answer:
                    scoring = {
                        "score": 0.0,
                        "feedback": "No answer provided",
                        "reasoning": "Empty answer"
                    }
                else:
                    # Use expected_concepts from question
                    question_obj = next((q for q in questions if q["question"] == question_text), {})
                    expected_concepts = question_obj.get("expected_concepts", [])
                    
                    scoring = await llm_service.score_answer(
                        question=question_text,
                        learner_answer=user_answer,
                        expected_concepts=expected_concepts
                    )
            
            # Create verification result
            question_id = answer_data.get("question_id", f"q_{len(verification_results) + 1}")
            result = {
                "question_id": question_id,
                "question": question_text,
                "learner_answer": user_answer,
                "score": scoring["score"],
                "feedback": scoring["feedback"],
                "scoring_details": scoring
            }
            
            verification_results.append(result)
        
        state["verification_results"] = verification_results
        
        state["workflow_history"].append("verify_understanding")
        return state
        
    except Exception as e:
        logger.error(f"Error in verify_understanding_node: {e}")
        state["errors"].append(f"Understanding verification error: {str(e)}")
        return state

@trace_workflow_node("check_threshold")
async def check_threshold_node(state: LearningAgentState) -> LearningAgentState:
    """Check if understanding meets 70% threshold."""
    logger.info("🎯 Checking threshold...")
    
    try:
        state["workflow_step"] = "checking_threshold"
        
        verification_results = state["verification_results"]
        
        if not verification_results:
            state["score_percentage"] = 0.0
            state["meets_threshold"] = False
        else:
            # Calculate overall score
            total_score = sum(result["score"] for result in verification_results)
            avg_score = total_score / len(verification_results)
            score_percentage = avg_score * 100
            
            state["score_percentage"] = score_percentage
            state["meets_threshold"] = score_percentage >= 70.0
        
        # Display feedback to user
        from .user_interaction import display_score_feedback
        display_score_feedback(
            state["score_percentage"],
            state["meets_threshold"],
            verification_results
        )
        
        logger.info(f"📊 Overall Score: {state['score_percentage']:.1f}%")
        logger.info(f"🎯 Meets 70% Threshold: {'✅ YES' if state['meets_threshold'] else '❌ NO'}")
        
        state["workflow_history"].append("check_threshold")
        return state
        
    except Exception as e:
        logger.error(f"Error in check_threshold_node: {e}")
        state["errors"].append(f"Threshold checking error: {str(e)}")
        return state

async def complete_checkpoint_node(state: LearningAgentState) -> LearningAgentState:
    """Complete the checkpoint (≥70% score)."""
    logger.info("🎉 Completing checkpoint...")
    
    try:
        state["workflow_step"] = "checkpoint_completed"
        
        checkpoint = state["current_checkpoint"]
        score = state["score_percentage"]
        
        logger.info(f"✅ Checkpoint '{checkpoint['title']}' completed!")
        logger.info(f"📊 Final Score: {score:.1f}% (≥70% required)")
        logger.info(f"🎊 Congratulations! Ready to proceed to next checkpoint.")
        
        state["workflow_history"].append("complete_checkpoint")
        return state
        
    except Exception as e:
        logger.error(f"Error in complete_checkpoint_node: {e}")
        state["errors"].append(f"Checkpoint completion error: {str(e)}")
        return state
        
@trace_workflow_node("progress_to_next_checkpoint")
async def progress_to_next_checkpoint_node(state: LearningAgentState) -> LearningAgentState:
    """Progress to the next checkpoint in the learning path."""
    logger.info("🚀 Progressing to next checkpoint...")
    
    try:
        learning_path = state["learning_path"]
        current_index = state["current_checkpoint_index"]
        
        # Set the next checkpoint as current
        next_checkpoint = learning_path["checkpoints"][current_index]
        state["current_checkpoint"] = next_checkpoint
        
        # Reset state for new checkpoint
        state["collected_materials"] = []
        state["summary"] = ""
        state["processed_context"] = []
        state["generated_questions"] = []
        state["verification_results"] = []
        state["score_percentage"] = 0.0
        state["meets_threshold"] = False
        state["workflow_step"] = "checkpoint_initialized"
        
        logger.info(f"📚 Starting checkpoint {current_index + 1}/{state['total_checkpoints']}: {next_checkpoint['title']}")
        logger.info(f"📝 Description: {next_checkpoint['description']}")
        logger.info(f"🎯 Requirements: {len(next_checkpoint['requirements'])} objectives")
        
        state["workflow_history"].append("progress_to_next_checkpoint")
        return state
        
    except Exception as e:
        logger.error(f"Error in progress_to_next_checkpoint_node: {e}")
        state["errors"].append(f"Checkpoint progression error: {str(e)}")
        return state

@trace_workflow_node("feynman_teaching")
async def feynman_teaching_node(state: LearningAgentState) -> LearningAgentState:
    """Apply Feynman Technique for adaptive teaching and re-assessment."""
    logger.info("📚 Applying Feynman Teaching...")
    
    try:
        state["workflow_step"] = "feynman_teaching"
        
        from .feynman_teaching import get_feynman_teacher
        feynman_teacher = get_feynman_teacher()
        
        # Apply Feynman technique
        should_retry, state = await feynman_teacher.apply_feynman_technique(state)
        
        # Mark if retry is needed
        state["feynman_retry_requested"] = should_retry
        
        checkpoint = state.get("current_checkpoint", {})
        logger.info(f"📚 Feynman teaching completed for '{checkpoint.get('title', 'Unknown')}'")
        logger.info(f"🔄 Retry requested: {should_retry}")
        
        state["workflow_history"].append("feynman_teaching")
        return state
        
    except Exception as e:
        logger.error(f"Error in feynman_teaching_node: {e}")
        state["errors"].append(f"Feynman teaching error: {str(e)}")
        state["feynman_retry_requested"] = False
        return state

@trace_workflow_node('progress_to_next_checkpoint')
async def progress_to_next_checkpoint_node(state):
    '''Progress to the next checkpoint in the learning path.'''
    logger.info('��� Progressing to next checkpoint...')
    
    try:
        learning_path = state['learning_path']
        current_index = state['current_checkpoint_index']
        
        # Set the next checkpoint as current
        next_checkpoint = learning_path['checkpoints'][current_index]
        state['current_checkpoint'] = next_checkpoint
        
        # Reset state for new checkpoint
        state['collected_materials'] = []
        state['summary'] = ''
        state['processed_context'] = []
        state['generated_questions'] = []
        state['verification_results'] = []
        state['score_percentage'] = 0.0
        state['meets_threshold'] = False
        state['workflow_step'] = 'checkpoint_initialized'
        
        logger.info(f'��� Starting checkpoint {current_index + 1}/{state["total_checkpoints"]}: {next_checkpoint["title"]}')
        logger.info(f'��� Description: {next_checkpoint["description"]}')
        logger.info(f'��� Requirements: {len(next_checkpoint["requirements"])} objectives')
        
        state['workflow_history'].append('progress_to_next_checkpoint')
        return state
        
    except Exception as e:
        logger.error(f'Error in progress_to_next_checkpoint_node: {e}')
        state['errors'].append(f'Checkpoint progression error: {str(e)}')
        return state

