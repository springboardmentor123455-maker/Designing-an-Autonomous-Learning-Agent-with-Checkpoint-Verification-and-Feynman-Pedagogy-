"""LangGraph workflow for the autonomous learning agent (Milestones 1-2 Implementation)."""
import os
from typing import Literal, Any
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from src.models.state import LearningState
from src.modules.context_manager import ContextManager
from src.modules.vector_store_manager import VectorStoreManager
from src.modules.question_generator import QuestionGenerator
from src.modules.understanding_verifier import UnderstandingVerifier
from src.modules.feynman_teacher import FeynmanTeacher

# Load environment variables
load_dotenv()


class LearningGraph:
    """
    LangGraph-based workflow for autonomous learning.
    
    This implements Milestones 1-4 focusing on:
    Milestone 1:
    - Checkpoint definition
    - Context gathering
    - Context validation
    
    Milestone 2:
    - Context processing with embeddings
    - Question generation
    - Understanding verification
    - 70% threshold conditional logic
    
    Milestone 3:
    - Feynman teaching implementation
    - Loop-back mechanism for reassessment
    
    Milestone 4:
    - Multiple sequential checkpoint progression
    - End-to-end testing support
    """
    
    def __init__(self, force_poor_answers: bool = False):
        """
        Initialize the learning graph and its components.
        
        Args:
            force_poor_answers: If True, generate poor answers to test Feynman path
        """
        self.context_manager = ContextManager(
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000"))
        )
        self.vector_store_manager = VectorStoreManager()
        self.question_generator = QuestionGenerator()
        self.understanding_verifier = UnderstandingVerifier(
            passing_threshold=float(os.getenv("UNDERSTANDING_THRESHOLD", "0.70"))
        )
        self.feynman_teacher = FeynmanTeacher()
        self.understanding_threshold = float(
            os.getenv("UNDERSTANDING_THRESHOLD", "0.70")
        )
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.force_poor_answers = force_poor_answers
    
    def build_graph(self) -> Any:
        """Build and compile the learning graph."""
        return self._build_workflow()
    
    def define_checkpoint_node(self, state: LearningState) -> LearningState:
        """
        Node: Define and initialize the current checkpoint.
        
        Milestone 4: Supports multiple sequential checkpoints.
        This is the entry point of the workflow and is called for each checkpoint.
        
        Args:
            state: Current learning state
            
        Returns:
            Updated state
        """
        print("\n" + "=" * 70)
        print("=== DEFINE CHECKPOINT ===")
        print("=" * 70)
        
        all_checkpoints = state.get("all_checkpoints", [])
        current_index = state.get("current_checkpoint_index", 0)
        
        if not all_checkpoints:
            state["error"] = "No checkpoints provided"
            state["current_stage"] = "error"
            return state
        
        if current_index >= len(all_checkpoints):
            # All checkpoints completed
            state["current_stage"] = "all_checkpoints_completed"
            state["messages"].append("All checkpoints completed successfully!")
            return state
        
        # Get current checkpoint
        checkpoint = all_checkpoints[current_index]
        state["checkpoint"] = checkpoint
        
        print(f"\nCheckpoint {current_index + 1} of {len(all_checkpoints)}")
        print(f"Topic: {checkpoint.topic}")
        print(f"Objectives:")
        for i, obj in enumerate(checkpoint.objectives, 1):
            print(f"  {i}. {obj}")
        print()
        
        state["current_stage"] = "checkpoint_defined"
        state["messages"].append(
            f"Starting checkpoint {current_index + 1}/{len(all_checkpoints)}: {checkpoint.topic}"
        )
        
        # Reset checkpoint-specific state
        state["gathered_contexts"] = []
        state["context_valid"] = False
        state["validation_message"] = None
        state["retry_count"] = 0
        state["context_chunks"] = []
        state["vector_store"] = None
        state["questions"] = []
        state["answers"] = []
        state["understanding_score"] = None
        state["passed_checkpoint"] = False
        state["weak_concepts"] = []
        state["feynman_explanations"] = []
        state["feynman_attempts"] = 0
        
        return state
    
    def gather_context_node(self, state: LearningState) -> LearningState:
        """
        Node: Gather learning context from user notes and web search.
        
        Args:
            state: Current learning state
            
        Returns:
            Updated state with gathered contexts
        """
        print("\n=== GATHER CONTEXT ===")
        checkpoint = state["checkpoint"]
        user_notes = state.get("user_notes")
        
        if not checkpoint:
            state["error"] = "No checkpoint defined"
            return state
        
        try:
            # Gather context (increased from 2 to 5)
            contexts = self.context_manager.gather_context(
                checkpoint=checkpoint,
                user_notes=user_notes,
                max_web_results=5
            )
            
            state["gathered_contexts"] = contexts
            state["current_stage"] = "context_gathered"
            state["messages"].append(
                f"Gathered {len(contexts)} context sources"
            )
            
        except Exception as e:
            print(f"Error gathering context: {e}")
            state["error"] = f"Context gathering failed: {str(e)}"
            state["current_stage"] = "error"
        
        return state
    
    def validate_context_node(self, state: LearningState) -> LearningState:
        """
        Node: Validate that gathered context is relevant and sufficient.
        
        Args:
            state: Current learning state
            
        Returns:
            Updated state with validation results
        """
        print("\n=== VALIDATE CONTEXT ===")
        checkpoint = state["checkpoint"]
        contexts = state["gathered_contexts"]
        retry_count = state["retry_count"]
        
        if not checkpoint:
            state["error"] = "No checkpoint defined"
            return state
        
        try:
            # Validate context
            is_valid, message, scored_contexts = self.context_manager.validate_context(
                checkpoint=checkpoint,
                contexts=contexts
            )
            
            # Update contexts with scores
            state["gathered_contexts"] = scored_contexts
            state["context_valid"] = is_valid
            state["validation_message"] = message
            
            print(f"Validation result: {message}")
            
            if is_valid:
                state["current_stage"] = "context_validated"
                state["messages"].append("Context validated successfully")
            else:
                state["current_stage"] = "validation_failed"
                state["messages"].append(f"Validation failed: {message}")
                state["retry_count"] = retry_count + 1
            
        except Exception as e:
            print(f"Error validating context: {e}")
            state["error"] = f"Context validation failed: {str(e)}"
            state["current_stage"] = "error"
        
        return state
    
    def process_context_node(self, state: LearningState) -> LearningState:
        """
        Node: Process validated context (chunk, embed, store in vector store).
        
        This is the core Milestone 2 context processing implementation:
        - Chunks text into manageable pieces
        - Creates embeddings using sentence transformers
        - Stores in FAISS vector store for similarity search
        
        Args:
            state: Current learning state
            
        Returns:
            Updated state with vector store
        """
        print("\n=== PROCESS CONTEXT (MILESTONE 2) ===")
        contexts = state["gathered_contexts"]
        checkpoint = state["checkpoint"]
        
        if not checkpoint:
            state["error"] = "No checkpoint defined"
            return state
        
        try:
            # Step 1: Chunk contexts
            chunks = self.context_manager.chunk_contexts(contexts)
            print(f"Created {len(chunks)} text chunks")
            
            if not chunks:
                state["error"] = "No content chunks created"
                state["current_stage"] = "error"
                return state
            
            state["context_chunks"] = chunks
            
            # Step 2: Create embeddings and vector store
            vector_store = self.vector_store_manager.create_vector_store(chunks)
            state["vector_store"] = vector_store
            
            # Step 3: Create summary for display
            summary = self.context_manager.summarize_context(contexts, checkpoint)
            print(f"\nContext Summary:\n{summary[:300]}...\n")
            
            state["current_stage"] = "context_processed"
            state["messages"].append(
                f"Processed context: {len(chunks)} chunks embedded in vector store"
            )
            
        except Exception as e:
            print(f"Error processing context: {e}")
            state["error"] = f"Context processing failed: {str(e)}"
            state["current_stage"] = "error"
        
        return state
    
    def should_retry_context(self, state: LearningState) -> Literal["gather_context", "process_context", "end"]:
        """
        Conditional edge: Determine if context gathering should be retried.
        
        Args:
            state: Current learning state
            
        Returns:
            Next node name
        """
        if state.get("error"):
            return "end"
        
        if state["context_valid"]:
            return "process_context"
        
        # Check if we should retry
        if state["retry_count"] < self.max_retries:
            print(f"Retrying context gathering (attempt {state['retry_count'] + 1}/{self.max_retries})")
            return "gather_context"
        
        # Max retries reached
        print("Max retries reached for context gathering")
        state["error"] = "Could not gather sufficient context after maximum retries"
        return "end"
    
    def generate_questions_node(self, state: LearningState) -> LearningState:
        """
        Node: Generate 3-5 assessment questions based on processed context.
        
        Milestone 2 implementation:
        - Uses vector store to retrieve relevant context
        - Generates questions aligned with checkpoint objectives
        
        Args:
            state: Current learning state
            
        Returns:
            Updated state with generated questions
        """
        print("\n=== GENERATE QUESTIONS (MILESTONE 2) ===")
        checkpoint = state["checkpoint"]
        vector_store = state.get("vector_store")
        
        if not vector_store:
            state["error"] = "No vector store available"
            state["current_stage"] = "error"
            return state
        
        try:
            # Get relevant context from vector store
            relevant_context = self.vector_store_manager.get_relevant_context(
                vector_store=vector_store,
                objectives=checkpoint.objectives,
                k_per_objective=2
            )
            
            # Generate questions
            questions = self.question_generator.generate_questions(
                checkpoint=checkpoint,
                context=relevant_context,
                num_questions=4  # Generate 4 questions (in 3-5 range)
            )
            
            state["questions"] = questions
            state["current_stage"] = "questions_generated"
            state["messages"].append(
                f"Generated {len(questions)} assessment questions"
            )
            
            # Display questions
            print(f"\nGenerated Questions:")
            for q in questions:
                print(f"\nQ{q['id']}: {q['question']}")
                print(f"   Objective: {q['objective']}")
                print(f"   Difficulty: {q['difficulty']}")
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            state["error"] = f"Question generation failed: {str(e)}"
            state["current_stage"] = "error"
        
        return state
    
    def verify_understanding_node(self, state: LearningState) -> LearningState:
        """
        Node: Evaluate learner answers and calculate understanding score.
        
        Milestone 2 implementation:
        - Evaluates answers against context
        - Calculates percentage score
        - Determines pass/fail based on 70% threshold
        
        Args:
            state: Current learning state
            
        Returns:
            Updated state with scores and pass/fail status
        """
        print("\n=== VERIFY UNDERSTANDING (MILESTONE 2) ===")
        questions = state.get("questions", [])
        answers = state.get("answers", [])
        vector_store = state.get("vector_store")
        checkpoint = state["checkpoint"]
        
        if not questions:
            state["error"] = "No questions available"
            state["current_stage"] = "error"
            return state
        
        # If no answers provided, generate simulated ones for testing
        if not answers:
            # Determine quality based on force_poor_answers flag
            if self.force_poor_answers:
                print("\n⚠️  FORCING POOR ANSWERS for Feynman testing...")
                quality = "poor"
            else:
                print("\nNo answers provided. Generating simulated 'good' answers for testing...")
                quality = "good"
            
            answers = self.understanding_verifier.generate_simulated_answers(
                questions=questions,
                quality=quality
            )
            state["answers"] = answers
        
        try:
            # Get relevant context for evaluation
            relevant_context = self.vector_store_manager.get_relevant_context(
                vector_store=vector_store,
                objectives=checkpoint.objectives,
                k_per_objective=3
            )
            
            # Evaluate answers
            avg_score, passed, weak_concepts = self.understanding_verifier.evaluate_answers(
                questions=questions,
                answers=answers,
                context=relevant_context
            )
            
            state["understanding_score"] = avg_score
            state["passed_checkpoint"] = passed
            state["weak_concepts"] = weak_concepts  # Store for Feynman teaching
            state["current_stage"] = "understanding_verified"
            
            result_status = "PASSED" if passed else "NEEDS IMPROVEMENT"
            state["messages"].append(
                f"Assessment complete: {avg_score:.1%} - {result_status}"
            )
            
            # Track weak concepts if failed
            if not passed and weak_concepts:
                state["messages"].append(
                    f"Weak concepts identified: {', '.join(set(weak_concepts))}"
                )
            
        except Exception as e:
            print(f"Error verifying understanding: {e}")
            state["error"] = f"Understanding verification failed: {str(e)}"
            state["current_stage"] = "error"
        
        return state
    
    def feynman_teaching_node(self, state: LearningState) -> LearningState:
        """
        Node: Provide Feynman-style teaching for weak concepts.
        
        Milestone 3 Implementation:
        - Identifies knowledge gaps from incorrect answers
        - Generates simplified explanations with analogies
        - Prepares for loop-back to question generation
        
        Args:
            state: Current learning state
            
        Returns:
            Updated state with Feynman explanations
        """
        print("\n=== FEYNMAN TEACHING (MILESTONE 3) ===")
        
        weak_concepts = state.get("weak_concepts", [])
        questions = state.get("questions", [])
        answers = state.get("answers", [])
        vector_store = state.get("vector_store")
        feynman_attempts = state.get("feynman_attempts", 0)
        
        print(f"Feynman Teaching Attempt #{feynman_attempts + 1}")
        print(f"Learner needs improvement (score < 70%)")
        print(f"Weak concepts: {len(set(weak_concepts))}")
        
        if not weak_concepts:
            print("No weak concepts identified")
            state["current_stage"] = "feynman_completed"
            return state
        
        try:
            # Get relevant context for weak concepts
            relevant_context = self.vector_store_manager.get_relevant_context(
                vector_store=vector_store,
                objectives=list(set(weak_concepts)),
                k_per_objective=3
            )
            
            # Generate Feynman explanations
            explanations = self.feynman_teacher.generate_explanations(
                questions=questions,
                answers=answers,
                context=relevant_context,
                weak_concepts=weak_concepts
            )
            
            # Store explanations
            state["feynman_explanations"] = explanations
            state["feynman_attempts"] = feynman_attempts + 1
            state["current_stage"] = "feynman_completed"
            
            # Display explanations
            print(f"\n{'='*60}")
            print("FEYNMAN EXPLANATIONS GENERATED")
            print(f"{'='*60}")
            for i, exp in enumerate(explanations, 1):
                print(f"\n[{i}] Concept: {exp['concept']}")
                print(f"\nExplanation:\n{exp['explanation'][:300]}...")
                print()
            print(f"{'='*60}\n")
            
            state["messages"].append(
                f"Feynman teaching applied (attempt {feynman_attempts + 1}): {len(explanations)} explanations generated"
            )
            
        except Exception as e:
            print(f"Error in Feynman teaching: {e}")
            state["error"] = f"Feynman teaching failed: {str(e)}"
            state["current_stage"] = "error"
        
        return state
    
    def should_teach(self, state: LearningState) -> Literal["feynman_teaching", "checkpoint_complete"]:
        """
        Conditional edge: Determine if Feynman teaching is needed.
        
        Implements Milestone 2-4 threshold logic:
        - If score >= 70%: proceed to checkpoint_complete (passed)
        - If score < 70%: go to Feynman teaching (needs improvement)
        
        Args:
            state: Current learning state
            
        Returns:
            Next node name
        """
        if state.get("error"):
            return "checkpoint_complete"
        
        # Check if learner passed the 70% threshold
        passed = state.get("passed_checkpoint", False)
        score = state.get("understanding_score", 0.0)
        
        if passed:
            print(f"\n✓ Checkpoint PASSED ({score:.1%} >= 70%)")
            return "checkpoint_complete"
        else:
            print(f"\n✗ Checkpoint needs improvement ({score:.1%} < 70%)")
            print("Routing to Feynman teaching...")
            return "feynman_teaching"
    
    def should_retry_after_feynman(self, state: LearningState) -> Literal["generate_questions", "checkpoint_complete"]:
        """
        Conditional edge: Determine if we should loop back for reassessment.
        
        Milestone 3-4 Loop-back Logic:
        - After Feynman teaching, generate new questions and verify again
        - Limit to max_feynman_attempts to prevent infinite loops
        - If max attempts reached, mark checkpoint complete (even if not passed)
        
        Args:
            state: Current learning state
            
        Returns:
            Next node name
        """
        if state.get("error"):
            return "checkpoint_complete"
        
        feynman_attempts = state.get("feynman_attempts", 0)
        max_attempts = state.get("max_feynman_attempts", 3)
        
        if feynman_attempts < max_attempts:
            print(f"\nLooping back to generate new questions (attempt {feynman_attempts}/{max_attempts})")
            print("Will reassess understanding after Feynman teaching...\n")
            return "generate_questions"
        else:
            print(f"\nMax Feynman attempts reached ({max_attempts})")
            print("Moving to checkpoint completion - learner may need additional support\n")
            state["messages"].append(
                f"Max Feynman attempts ({max_attempts}) reached without passing"
            )
            return "checkpoint_complete"
    
    def checkpoint_complete_node(self, state: LearningState) -> LearningState:
        """
        Node: Mark current checkpoint as complete and prepare for next checkpoint.
        
        Milestone 4 Implementation:
        - Mark current checkpoint as completed
        - Increment checkpoint index
        - Prepare state for next checkpoint or end workflow
        
        Args:
            state: Current learning state
            
        Returns:
            Updated state
        """
        print("\n" + "=" * 70)
        print("=== CHECKPOINT COMPLETE ===")
        print("=" * 70)
        
        current_index = state.get("current_checkpoint_index", 0)
        all_checkpoints = state.get("all_checkpoints", [])
        passed = state.get("passed_checkpoint", False)
        score = state.get("understanding_score", 0.0)
        
        # Mark checkpoint as completed
        state["completed_checkpoints"].append(current_index)
        
        checkpoint_status = "PASSED" if passed else "COMPLETED (needs review)"
        print(f"\nCheckpoint {current_index + 1}: {checkpoint_status}")
        print(f"Final Score: {score:.1%}")
        print(f"Feynman Attempts Used: {state.get('feynman_attempts', 0)}")
        
        state["messages"].append(
            f"Checkpoint {current_index + 1} completed with score {score:.1%}"
        )
        
        # Check if more checkpoints remain
        if current_index + 1 < len(all_checkpoints):
            print(f"\nProgressing to checkpoint {current_index + 2} of {len(all_checkpoints)}...")
            state["current_checkpoint_index"] = current_index + 1
            state["current_stage"] = "ready_for_next_checkpoint"
        else:
            print(f"\n🎉 All {len(all_checkpoints)} checkpoints completed!")
            print(f"   Passed: {sum(1 for i in state.get('completed_checkpoints', []) if state.get('passed_checkpoint', False))}/{len(all_checkpoints)}")
            state["current_stage"] = "all_checkpoints_completed"
        
        print("=" * 70 + "\n")
        
        return state
    
    def should_continue_to_next_checkpoint(self, state: LearningState) -> Literal["define_checkpoint", "end"]:
        """
        Conditional edge: Determine if there are more checkpoints to process.
        
        Milestone 4 Logic:
        - If more checkpoints exist, loop back to define_checkpoint
        - If all checkpoints completed, end the workflow
        
        Args:
            state: Current learning state
            
        Returns:
            Next node name
        """
        if state.get("error"):
            return "end"
        
        # Check if we've completed all checkpoints
        if state.get("current_stage") == "all_checkpoints_completed":
            print("→ All checkpoints completed. Ending workflow.\n")
            return "end"
        
        current_index = state.get("current_checkpoint_index", 0)
        all_checkpoints = state.get("all_checkpoints", [])
        
        if current_index < len(all_checkpoints):
            print(f"→ Continuing to next checkpoint ({current_index + 1}/{len(all_checkpoints)})\n")
            return "define_checkpoint"
        else:
            print("→ All checkpoints completed. Ending workflow.\n")
            return "end"
    
    def _build_workflow(self) -> Any:
        """
        Build the LangGraph workflow.
        
        Milestones 1-4 Implementation:
        1. Define Checkpoint
        2. Gather Context
        3. Validate Context
        4. Process Context (with embeddings)
        5. Generate Questions
        6. Verify Understanding
        7. Conditional: If >= 70% → Checkpoint Complete, If < 70% → Feynman Teaching
        8. After Feynman → Loop back to Generate Questions (with retry limit)
        9. Checkpoint Complete → Check if more checkpoints exist
        10. If more checkpoints → Loop back to Define Checkpoint, else End
        
        Returns:
            Compiled StateGraph
        """
        # Create graph
        workflow = StateGraph(LearningState)
        
        # Add nodes
        workflow.add_node("define_checkpoint", self.define_checkpoint_node)
        workflow.add_node("gather_context", self.gather_context_node)
        workflow.add_node("validate_context", self.validate_context_node)
        workflow.add_node("process_context", self.process_context_node)
        workflow.add_node("generate_questions", self.generate_questions_node)
        workflow.add_node("verify_understanding", self.verify_understanding_node)
        workflow.add_node("feynman_teaching", self.feynman_teaching_node)
        workflow.add_node("checkpoint_complete", self.checkpoint_complete_node)  # Milestone 4
        
        # Define edges
        workflow.set_entry_point("define_checkpoint")
        
        # Milestone 1 flow
        workflow.add_edge("define_checkpoint", "gather_context")
        workflow.add_edge("gather_context", "validate_context")
        
        # Conditional edge after validation (with retry logic)
        workflow.add_conditional_edges(
            "validate_context",
            self.should_retry_context,
            {
                "gather_context": "gather_context",
                "process_context": "process_context",
                "end": END
            }
        )
        
        # Milestone 2 flow
        workflow.add_edge("process_context", "generate_questions")
        workflow.add_edge("generate_questions", "verify_understanding")
        
        # Conditional edge after understanding verification (70% threshold)
        workflow.add_conditional_edges(
            "verify_understanding",
            self.should_teach,
            {
                "feynman_teaching": "feynman_teaching",
                "checkpoint_complete": "checkpoint_complete"  # Milestone 4
            }
        )
        
        # Milestone 3: Loop-back mechanism after Feynman teaching
        workflow.add_conditional_edges(
            "feynman_teaching",
            self.should_retry_after_feynman,
            {
                "generate_questions": "generate_questions",
                "checkpoint_complete": "checkpoint_complete"  # Milestone 4
            }
        )
        
        # Milestone 4: Multiple checkpoint progression
        workflow.add_conditional_edges(
            "checkpoint_complete",
            self.should_continue_to_next_checkpoint,
            {
                "define_checkpoint": "define_checkpoint",
                "end": END
            }
        )
        
        return workflow.compile()


def create_learning_graph(force_poor_answers: bool = False) -> Any:
    """
    Factory function to create and return a compiled learning graph.
    
    Args:
        force_poor_answers: If True, generate poor answers to test Feynman path
    
    Returns:
        Compiled LangGraph workflow
    """
    graph = LearningGraph(force_poor_answers=force_poor_answers)
    return graph.build_graph()
