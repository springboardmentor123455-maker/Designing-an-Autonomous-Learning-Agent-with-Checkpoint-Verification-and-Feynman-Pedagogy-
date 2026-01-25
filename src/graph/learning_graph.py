"""LangGraph workflow for the autonomous learning agent (Week 1-2 Implementation)."""
import os
from typing import Literal, Any
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from src.models.state import LearningState
from src.modules.context_manager import ContextManager

# Load environment variables
load_dotenv()


class LearningGraph:
    """
    LangGraph-based workflow for autonomous learning.
    
    This implements the Week 1-2 milestone focusing on:
    - Checkpoint definition
    - Context gathering
    - Context validation
    """
    
    def __init__(self):
        """Initialize the learning graph and its components."""
        self.context_manager = ContextManager(
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000"))
        )
        self.understanding_threshold = float(
            os.getenv("UNDERSTANDING_THRESHOLD", "0.70")
        )
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
    
    def build_graph(self) -> Any:
        """Build and compile the learning graph."""
        return self._build_workflow()
    
    def define_checkpoint_node(self, state: LearningState) -> LearningState:
        """
        Node: Define and initialize the current checkpoint.
        
        This is the entry point of the workflow.
        
        Args:
            state: Current learning state
            
        Returns:
            Updated state
        """
        print("\n=== DEFINE CHECKPOINT ===")
        checkpoint = state["checkpoint"]
        
        if checkpoint:
            print(f"Topic: {checkpoint.topic}")
            print(f"Objectives: {', '.join(checkpoint.objectives)}")
            
            state["current_stage"] = "checkpoint_defined"
            state["messages"].append(
                f"Starting checkpoint: {checkpoint.topic}"
            )
        else:
            state["error"] = "No checkpoint provided"
            state["current_stage"] = "error"
        
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
        Node: Process validated context (chunk, summarize).
        
        This prepares the context for later stages (question generation, etc.).
        
        Args:
            state: Current learning state
            
        Returns:
            Updated state
        """
        print("\n=== PROCESS CONTEXT ===")
        contexts = state["gathered_contexts"]
        checkpoint = state["checkpoint"]
        
        if not checkpoint:
            state["error"] = "No checkpoint defined"
            return state
        
        try:
            # Chunk contexts for later processing
            chunks = self.context_manager.chunk_contexts(contexts)
            print(f"Created {len(chunks)} text chunks")
            
            # Create summary
            summary = self.context_manager.summarize_context(contexts, checkpoint)
            print(f"\nContext Summary:\n{summary[:300]}...\n")
            
            state["current_stage"] = "context_processed"
            state["messages"].append(
                f"Processed context into {len(chunks)} chunks"
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
        Node: Generate assessment questions based on context and objectives.
        
        Args:
            state: Current learning state
            
        Returns:
            Updated state with generated questions
        """
        print("\n=== GENERATE QUESTIONS ===")
        checkpoint = state["checkpoint"]
        contexts = state["gathered_contexts"]
        
        try:
            # Generate questions
            questions = self.question_generator.generate_questions(
                checkpoint=checkpoint,
                contexts=contexts
            )
            
            state["questions"] = questions
            state["current_stage"] = "questions_generated"
            state["messages"].append(
                f"Generated {len(questions)} assessment questions"
            )
            
            # Print questions for review
            for i, q in enumerate(questions, 1):
                print(f"\nQ{i}: {q.question_text}")
                print(f"   Objective: {q.objective}")
                print(f"   Difficulty: {q.difficulty}")
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            state["error"] = f"Question generation failed: {str(e)}"
            state["current_stage"] = "error"
        
        return state
    
    def collect_answers_node(self, state: LearningState) -> LearningState:
        """
        Node: Collect answers from learner (simulated or interactive).
        
        In a real implementation, this would pause for user input.
        For testing, we'll mark it as ready for answers.
        
        Args:
            state: Current learning state
            
        Returns:
            Updated state
        """
        print("\n=== COLLECT ANSWERS ===")
        questions = state["questions"]
        
        # Mark that we're ready to collect answers
        state["current_stage"] = "ready_for_answers"
        state["messages"].append(
            f"Ready to collect {len(questions)} answers from learner"
        )
        
        print(f"System is ready to receive {len(questions)} answers")
        print("Note: In interactive mode, learner would provide answers here")
        
        return state
    
    def verify_understanding_node(self, state: LearningState) -> LearningState:
        """
        Node: Evaluate learner answers and calculate understanding score.
        
        Args:
            state: Current learning state
            
        Returns:
            Updated state with scores and pass/fail status
        """
        print("\n=== VERIFY UNDERSTANDING ===")
        answers = state["answers"]
        checkpoint = state["checkpoint"]
        
        if not answers:
            print("No answers provided yet")
            state["current_stage"] = "awaiting_answers"
            return state
        
        try:
            # Evaluate answers
            avg_score, passed, weak_concepts = self.understanding_verifier.evaluate_answers(
                answers=answers,
                checkpoint=checkpoint
            )
            
            state["understanding_score"] = avg_score
            state["passed_checkpoint"] = passed
            state["weak_concepts"] = weak_concepts
            state["current_stage"] = "understanding_verified"
            
            # Generate progress report
            report = self.understanding_verifier.generate_progress_report(
                checkpoint=checkpoint,
                answers=answers,
                average_score=avg_score,
                passed=passed,
                weak_concepts=weak_concepts
            )
            
            print(report)
            
            state["messages"].append(
                f"Assessment complete: {avg_score:.1%} "
                f"({'PASSED' if passed else 'NEEDS IMPROVEMENT'})"
            )
            
        except Exception as e:
            print(f"Error verifying understanding: {e}")
            state["error"] = f"Understanding verification failed: {str(e)}"
            state["current_stage"] = "error"
        
        return state
    
    def feynman_teaching_node(self, state: LearningState) -> LearningState:
        """
        Node: Generate Feynman-style explanations for weak concepts.
        
        Args:
            state: Current learning state
            
        Returns:
            Updated state with Feynman explanations
        """
        print("\n=== FEYNMAN TEACHING ===")
        weak_concepts = state["weak_concepts"]
        checkpoint = state["checkpoint"]
        contexts = state["gathered_contexts"]
        
        if not weak_concepts:
            print("No weak concepts identified - excellent understanding!")
            state["current_stage"] = "teaching_complete"
            state["messages"].append("No additional teaching needed")
            return state
        
        try:
            # Generate context summary for teaching
            context_text = "\n\n".join([
                ctx.content for ctx in contexts[:3]
            ])
            
            # Generate Feynman explanations
            explanations = self.feynman_teacher.teach_weak_concepts(
                weak_concepts=weak_concepts,
                checkpoint=checkpoint,
                context=context_text
            )
            
            state["feynman_explanations"] = explanations
            state["current_stage"] = "teaching_complete"
            
            # Generate teaching session
            teaching_session = self.feynman_teacher.generate_teaching_session(
                weak_concepts=weak_concepts,
                checkpoint=checkpoint,
                context=context_text
            )
            
            print(teaching_session)
            
            state["messages"].append(
                f"Generated {len(explanations)} Feynman explanations"
            )
            
        except Exception as e:
            print(f"Error in Feynman teaching: {e}")
            state["error"] = f"Feynman teaching failed: {str(e)}"
            state["current_stage"] = "error"
        
        return state
    
    def should_teach(self, state: LearningState) -> Literal["feynman_teaching", "end"]:
        """
        Conditional edge: Determine if Feynman teaching is needed.
        
        Args:
            state: Current learning state
            
        Returns:
            Next node name
        """
        if state.get("error"):
            return "end"
        
        # If learner didn't pass, provide teaching
        if not state["passed_checkpoint"] and state["weak_concepts"]:
            return "feynman_teaching"
        
        return "end"
    
    def _build_workflow(self) -> Any:
        """
        Build the LangGraph workflow.
        
        Week 1-2 Implementation:
        1. Define Checkpoint
        2. Gather Context
        3. Validate Context
        4. Process Context (if valid) or Retry (if invalid)
        
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
        
        # Define edges
        workflow.set_entry_point("define_checkpoint")
        
        workflow.add_edge("define_checkpoint", "gather_context")
        workflow.add_edge("gather_context", "validate_context")
        
        # Conditional edge after validation
        workflow.add_conditional_edges(
            "validate_context",
            self.should_retry_context,
            {
                "gather_context": "gather_context",
                "process_context": "process_context",
                "end": END
            }
        )
        
        workflow.add_edge("process_context", END)
        
        return workflow.compile()


def create_learning_graph() -> Any:
    """
    Factory function to create and return a compiled learning graph.
    
    Returns:
        Compiled LangGraph workflow
    """
    graph = LearningGraph()
    return graph.build_graph()
