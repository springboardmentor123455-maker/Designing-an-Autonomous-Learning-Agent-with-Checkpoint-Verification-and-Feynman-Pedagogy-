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
    """Collect learning materials."""
    logger.info("📚 Collecting learning materials...")
    
    try:
        state["workflow_step"] = "collecting_materials"
        
        # If materials are already provided, validate them
        materials = state.get("collected_materials", [])
        
        if not materials:
            # Generate default materials based on checkpoint
            checkpoint = state["current_checkpoint"]
            default_material = {
                "id": f"material_{checkpoint['id']}",
                "title": f"Learning Material for {checkpoint['title']}",
                "content": f"This is learning content for {checkpoint['title']}. {checkpoint['description']}",
                "source": "auto_generated"
            }
            materials = [default_material]
            state["collected_materials"] = materials
        
        # Trace document collection for LangSmith
        search_query = state["current_checkpoint"]["title"]
        trace_document_retrieval(search_query, materials)
        
        logger.info(f"📖 Collected {len(materials)} materials")
        for material in materials:
            logger.info(f"   • {material['title']} ({len(material['content'])} chars)")
        
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
    """Verify understanding through question answering."""
    logger.info("✅ Verifying understanding...")
    
    try:
        state["workflow_step"] = "verifying_understanding"
        
        questions = state["generated_questions"]
        processed_context = state["processed_context"]
        verification_results = []
        
        for question in questions:
            # Simulate learner answer
            # Ensure context_chunks exists
            context_chunks = question.get("context_chunks", [])
            if not context_chunks:
                # Use first few chunks from processed_context as fallback
                context_chunks = processed_context[:3] if processed_context else []
            
            answer = await llm_service.simulate_learner_answer(
                question["question"],
                context_chunks,
                processed_context
            )
            
            # Score the answer
            # Use expected_elements or expected_concepts, whichever exists
            expected_concepts = question.get("expected_concepts") or question.get("expected_elements", [])
            scoring = await llm_service.score_answer(
                question["question"],
                answer,
                expected_concepts
            )
            
            # Create verification result
            question_id = question.get("question_id", f"q_{len(verification_results) + 1}")
            result = {
                "question_id": question_id,
                "learner_answer": answer,
                "score": scoring["score"],
                "feedback": scoring["feedback"],
                "scoring_details": scoring
            }
            
            verification_results.append(result)
            logger.info(f"   Q: {question['question']}")
            logger.info(f"   A: {answer[:100]}...")
            logger.info(f"   Score: {scoring['score']:.2f}")
        
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

async def feynman_placeholder_node(state: LearningAgentState) -> LearningAgentState:
    """Placeholder for Feynman teaching (Milestone 3)."""
    logger.info("📚 Feynman teaching needed...")
    
    try:
        state["workflow_step"] = "feynman_needed"
        
        checkpoint = state["current_checkpoint"]
        score = state["score_percentage"]
        
        # Identify failing areas
        failing_areas = []
        for result in state["verification_results"]:
            if result["score"] < 0.7:
                failing_areas.append({
                    "question_id": result["question_id"],
                    "score": result["score"],
                    "feedback": result["feedback"]
                })
        
        state["feynman_info"] = {
            "trigger_score": score,
            "failing_areas": failing_areas,
            "explanation_needed": True,
            "status": "placeholder_reached"
        }
        
        logger.info(f"📚 Feynman teaching required for '{checkpoint['title']}'")
        logger.info(f"📊 Score: {score:.1f}% (below 70% threshold)")
        logger.info(f"📋 Areas needing improvement: {len(failing_areas)}")
        logger.info("🔮 Milestone 3: Advanced teaching methods coming soon...")
        
        state["workflow_history"].append("feynman_placeholder")
        return state
        
    except Exception as e:
        logger.error(f"Error in feynman_placeholder_node: {e}")
        state["errors"].append(f"Feynman placeholder error: {str(e)}")
        return state