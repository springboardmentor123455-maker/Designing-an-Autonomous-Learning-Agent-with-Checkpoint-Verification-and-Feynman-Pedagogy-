"""
Multi-checkpoint learning session implementation.
"""

import asyncio
import logging
from typing import Dict, Any
from .sample_data import create_learning_paths
from .models import LearningAgentState, LearningPath
from .workflow import create_unified_workflow

logger = logging.getLogger(__name__)

async def run_multi_checkpoint_session(learning_path: LearningPath) -> Dict[str, Any]:
    """Run a complete learning session across multiple checkpoints."""
    
    logger.info("🚀 MULTI-CHECKPOINT LEARNING SESSION")
    logger.info("=" * 60)
    logger.info(f"📚 Learning Path: {learning_path['title']}")
    logger.info(f"📝 Description: {learning_path['description']}")
    logger.info(f"🎯 Total Checkpoints: {len(learning_path['checkpoints'])}")
    logger.info("=" * 60)
    
    # Initialize state with learning path
    initial_state: LearningAgentState = {
        # Learning Path Management
        "learning_path": learning_path,
        "current_checkpoint_index": 0,
        "completed_checkpoints": [],
        "total_checkpoints": len(learning_path['checkpoints']),
        "has_next_checkpoint": True,
        "learning_path_completed": False,
        
        # Current Checkpoint (start with first checkpoint)
        "current_checkpoint": learning_path['checkpoints'][0],
        "collected_materials": [],
        "summary": "",
        "milestone1_score": 0.0,
        
        # Milestone 2 extensions
        "processed_context": [],
        "generated_questions": [],
        "verification_results": [],
        "score_percentage": 0.0,
        "meets_threshold": False,
        
        # Feynman Teaching (Milestone 3)
        "feynman_retry_count": 0,
        "feynman_retry_requested": False,
        "feynman_explanations": [],
        
        # User Materials & Validation
        "user_uploaded_notes_path": None,
        "materials_validation": None,
        
        # Workflow management
        "workflow_step": "initialized",
        "workflow_history": [],
        "errors": []
    }
    
    completed_checkpoints = 0
    total_score = 0.0
    
    # Prompt for file upload (PRIORITY: User materials first)
    logger.info("\n📎 Optional: Upload your own learning materials")
    from .file_upload import get_upload_handler
    upload_handler = get_upload_handler()
    
    uploaded_paths = upload_handler.prompt_for_file_upload()
    if uploaded_paths:
        initial_state["user_uploaded_notes_path"] = uploaded_paths
        logger.info(f"✅ Will use {len(uploaded_paths)} user-provided files")
    else:
        initial_state["user_uploaded_notes_path"] = None
        logger.info("ℹ️ Will generate materials dynamically (LLM + Web Search)")
    
    # Create workflow (will be updated to handle progression)
    compiled_workflow = create_unified_workflow()
    
    # Process each checkpoint
    while True:
        current_checkpoint = initial_state["current_checkpoint"]
        checkpoint_num = initial_state["current_checkpoint_index"] + 1
        total_checkpoints = initial_state["total_checkpoints"]
        
        logger.info(f"\n🎯 CHECKPOINT {checkpoint_num}/{total_checkpoints}: {current_checkpoint['title']}")
        logger.info("-" * 50)
        
        # Run workflow for current checkpoint
        result = await compiled_workflow.ainvoke(initial_state)
        
        # Log checkpoint results
        score = result.get("score_percentage", 0.0)
        meets_threshold = result.get("meets_threshold", False)
        
        logger.info(f"✅ Checkpoint Results:")
        logger.info(f"   Score: {score:.1f}%")
        logger.info(f"   Threshold Met: {meets_threshold}")
        
        if meets_threshold:
            completed_checkpoints += 1
            total_score += score
            logger.info(f"🎉 Checkpoint {checkpoint_num} PASSED!")
        else:
            logger.info(f"❌ Checkpoint {checkpoint_num} needs improvement (Feynman teaching would be triggered)")
        
        # Check if there are more checkpoints
        if result.get("has_next_checkpoint", False) and meets_threshold:
            # Move to next checkpoint
            initial_state["current_checkpoint_index"] += 1
            if initial_state["current_checkpoint_index"] < len(learning_path['checkpoints']):
                initial_state["current_checkpoint"] = learning_path['checkpoints'][initial_state["current_checkpoint_index"]]
                
                # Reset for next checkpoint
                initial_state["collected_materials"] = []
                initial_state["summary"] = ""
                initial_state["processed_context"] = []
                initial_state["generated_questions"] = []
                initial_state["verification_results"] = []
                initial_state["score_percentage"] = 0.0
                initial_state["meets_threshold"] = False
                initial_state["workflow_step"] = "initialized"
                initial_state["workflow_history"] = []
                
                logger.info(f"\n➡️ Progressing to next checkpoint...")
                continue
            else:
                logger.info(f"\n🏆 All checkpoints completed!")
                break
        else:
            if not meets_threshold:
                logger.info(f"\n🔄 Need to retry checkpoint (Feynman teaching would be implemented)")
                # In full implementation, would retry with Feynman teaching
                break
            else:
                logger.info(f"\n🏆 Learning path completed!")
                break
    
    # Final results
    avg_score = total_score / max(1, completed_checkpoints)
    
    logger.info("\n" + "=" * 60)
    logger.info("🏆 LEARNING PATH RESULTS")
    logger.info("=" * 60)
    logger.info(f"📊 Completed Checkpoints: {completed_checkpoints}/{len(learning_path['checkpoints'])}")
    logger.info(f"📈 Average Score: {avg_score:.1f}%")
    logger.info(f"🎯 Learning Path: {learning_path['title']}")
    
    return {
        "learning_path": learning_path,
        "completed_checkpoints": completed_checkpoints,
        "total_checkpoints": len(learning_path['checkpoints']),
        "average_score": avg_score,
        "final_state": result
    }

def select_learning_path() -> LearningPath:
    """Allow user to select a learning path."""
    learning_paths = create_learning_paths()
    
    print("\n📚 AVAILABLE LEARNING PATHS:")
    print("-" * 50)
    
    for i, path in enumerate(learning_paths, 1):
        print(f"\n{i}. {path['title']}")
        print(f"   📝 {path['description']}")
        print(f"   🎯 Checkpoints: {len(path['checkpoints'])}")
        for j, checkpoint in enumerate(path['checkpoints'], 1):
            print(f"      {j}. {checkpoint['title']}")
    
    print("\n" + "-" * 50)
    
    while True:
        try:
            choice = input(f"\nSelect learning path (1-{len(learning_paths)}): ").strip()
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(learning_paths):
                    selected_path = learning_paths[idx]
                    print(f"\n✅ Selected: {selected_path['title']}")
                    return selected_path
            
            print(f"❌ Please enter a number between 1 and {len(learning_paths)}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Session cancelled by user")
            return None