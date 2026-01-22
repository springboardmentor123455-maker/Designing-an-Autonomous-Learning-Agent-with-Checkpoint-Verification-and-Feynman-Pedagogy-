import os
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==================== LANGSMITH OBSERVABILITY ====================
# Enable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "learning-agent-groq")

# ==================== STATE DEFINITION ====================
class LearningState(TypedDict):
    """Defines the state that flows through our learning graph"""
    current_checkpoint_index: int
    checkpoint_topic: str
    checkpoint_objectives: List[str]
    context: str
    questions: List[str]
    learner_answers: List[str]
    score: float
    threshold: float
    feynman_explanation: str
    status: str
    user_notes: str
    all_checkpoints: List[dict]
    retry_count: int  # Add retry counter to prevent infinite loops

# ==================== INITIALIZE COMPONENTS ====================
def initialize_components():
    """Initialize LLM, Search Tool, and Embeddings"""
    
    # Initialize Groq LLM
    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
        max_tokens=2048
    )
    
    # Initialize Tavily Search
    search_tool = TavilySearchResults(
        api_key=os.getenv("TAVILY_API_KEY"),
        max_results=3
    )
    
    # Initialize HuggingFace Embeddings 
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    return llm, search_tool, embeddings

# ==================== NODE FUNCTIONS ====================

def define_checkpoint(state: LearningState) -> LearningState:
    """Node 1: Define the current checkpoint"""
    current_checkpoint_index = state.get("current_checkpoint_index", 0)
    all_checkpoints = state.get("all_checkpoints", [])
    
    if current_checkpoint_index < len(all_checkpoints):
        current_checkpoint = all_checkpoints[current_checkpoint_index]
        state["checkpoint_topic"] = current_checkpoint["topic"]
        state["checkpoint_objectives"] = current_checkpoint["objectives"]
        state["status"] = "checkpoint_defined"
        state["retry_count"] = 0  # Reset retry count for new checkpoint
    else:
        state["status"] = "learning_complete"
    
    return state

def gather_context(state: LearningState) -> LearningState:
    """Node 2: Gather learning context from notes or web search"""
    llm, search_tool, _ = initialize_components()
    
    topic = state["checkpoint_topic"]
    user_notes = state.get("user_notes", "")
    
    # Check if user notes contain relevant information
    if user_notes and len(user_notes) > 100:
        # Use LLM to check relevance of notes
        prompt = f"""Check if these notes contain information about '{topic}':
        
Notes: {user_notes[:500]}

Answer with 'YES' or 'NO' only."""
        
        try:
            response = llm.invoke(prompt)
            
            if "YES" in response.content.upper():
                state["context"] = user_notes
                state["status"] = "context_from_notes"
                return state
        except Exception as e:
            print(f"Error checking notes relevance: {e}")
    
    # Fall back to web search
    try:
        search_query = f"Learn {topic} tutorial explanation"
        search_results = search_tool.invoke(search_query)
        
        # Combine search results into context
        context = "\n\n".join([result.get("content", "") for result in search_results])
        state["context"] = context if context else f"Topic: {topic}"
        state["status"] = "context_from_search"
    except Exception as e:
        print(f"Error in web search: {e}")
        # Fallback context
        state["context"] = f"Topic: {topic}. Please provide a comprehensive overview."
        state["status"] = "context_from_search"
    
    return state

def validate_context(state: LearningState) -> LearningState:
    """Node 3: Validate if context covers checkpoint objectives"""
    llm, _, _ = initialize_components()
    
    context = state["context"]
    objectives = state["checkpoint_objectives"]
    retry_count = state.get("retry_count", 0)
    
    # Prevent infinite validation loops
    if retry_count >= 2:
        state["status"] = "context_validated"
        return state
    
    prompt = f"""Evaluate if this context adequately covers these learning objectives:

Objectives:
{chr(10).join(f'- {obj}' for obj in objectives)}

Context:
{context[:1000]}

Rate the coverage from 1-5 and explain. Format: SCORE: X"""
    
    try:
        response = llm.invoke(prompt)
        
        # Extract score
        score_line = [line for line in response.content.split('\n') if 'SCORE:' in line]
        if score_line:
            score = int(score_line[0].split(':')[1].strip())
            
            if score >= 3:  # Lowered threshold from 4 to 3
                state["status"] = "context_validated"
            else:
                state["status"] = "context_insufficient"
                state["retry_count"] = retry_count + 1
        else:
            state["status"] = "context_validated"
    except Exception as e:
        print(f"Error validating context: {e}")
        state["status"] = "context_validated"  # Default to validated if error
    
    return state

def process_context(state: LearningState) -> LearningState:
    """Node 4: Process context (chunk and embed for efficient retrieval)"""
    _, _, embeddings = initialize_components()
    
    context = state["context"]
    
    try:
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_text(context)
        
        # Create vector store (stored in session for this checkpoint)
        vectorstore = FAISS.from_texts(chunks, embeddings)
        
        # Store in Streamlit session state for later retrieval
        if 'st' in dir():  # Check if streamlit is available
            st.session_state['vectorstore'] = vectorstore
    except Exception as e:
        print(f"Error processing context: {e}")
    
    state["status"] = "context_processed"
    return state

def generate_questions(state: LearningState) -> LearningState:
    """Node 5: Generate assessment questions"""
    llm, _, _ = initialize_components()
    
    topic = state["checkpoint_topic"]
    objectives = state["checkpoint_objectives"]
    context = state["context"][:2000]  # Use first 2000 chars
    
    prompt = f"""Based on this learning material about '{topic}', generate 3 specific questions to test understanding.

Objectives to cover:
{chr(10).join(f'- {obj}' for obj in objectives)}

Material:
{context}

Generate exactly 3 questions, numbered 1-3. Make them clear and specific."""
    
    try:
        response = llm.invoke(prompt)
        
        # Parse questions
        questions = []
        for line in response.content.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering
                question = line.lstrip('0123456789.-) ').strip()
                if question:
                    questions.append(question)
        
        state["questions"] = questions[:3] if questions else [
            f"Explain the main concept of {topic}",
            f"What are the key objectives in {topic}?",
            f"How would you apply {topic} in practice?"
        ]
    except Exception as e:
        print(f"Error generating questions: {e}")
        state["questions"] = [
            f"Explain the main concept of {topic}",
            f"What are the key objectives in {topic}?",
            f"How would you apply {topic} in practice?"
        ]
    
    state["status"] = "questions_generated"
    return state

def assess_learner(state: LearningState) -> LearningState:
    """Node 6: Assess learner's answers and calculate score"""
    llm, _, _ = initialize_components()
    
    questions = state["questions"]
    answers = state.get("learner_answers", [])
    context = state["context"][:2000]
    
    if not answers or len(answers) != len(questions):
        state["score"] = 0.0
        state["status"] = "awaiting_answers"
        return state
    
    # Evaluate each answer
    scores = []
    for q, a in zip(questions, answers):
        prompt = f"""Based on this context, evaluate the answer to the question.

Context: {context}

Question: {q}
Answer: {a}

Rate the answer's correctness from 0-100. Consider:
- Accuracy
- Completeness
- Understanding of concept

Respond with only a number between 0-100."""
        
        try:
            response = llm.invoke(prompt)
            
            # Extract number from response
            score_text = ''.join(filter(str.isdigit, response.content))
            score = float(score_text) if score_text else 50
            score = min(100, max(0, score))  # Clamp between 0-100
        except Exception as e:
            print(f"Error assessing answer: {e}")
            score = 50  # Default middle score
        
        scores.append(score)
    
    # Calculate average score
    avg_score = sum(scores) / len(scores) if scores else 0
    state["score"] = avg_score
    state["status"] = "assessed"
    
    return state

def evaluate_score(state: LearningState) -> LearningState:
    """Node 7: Evaluate if score meets threshold"""
    score = state.get("score", 0)
    threshold = state.get("threshold", 70.0)
    retry_count = state.get("retry_count", 0)
    
    # Prevent infinite Feynman loops - after 1 retry, pass anyway
    if retry_count >= 1:
        state["status"] = "passed"
    elif score >= threshold:
        state["status"] = "passed"
    else:
        state["status"] = "needs_feynman"
        state["retry_count"] = retry_count + 1
    
    return state

def apply_feynman_teaching(state: LearningState) -> LearningState:
    """Node 8: Generate simplified Feynman-style explanation"""
    llm, _, _ = initialize_components()
    
    topic = state["checkpoint_topic"]
    questions = state["questions"]
    answers = state.get("learner_answers", [])
    context = state["context"][:2000]
    
    # Identify weak areas
    weak_areas = []
    for i, (q, a) in enumerate(zip(questions, answers)):
        if len(a.strip()) < 10 or "don't know" in a.lower():
            weak_areas.append(q)
    
    if not weak_areas:
        weak_areas = questions  # If unclear, reteach everything
    
    prompt = f"""Using the Feynman Technique, explain these concepts in the simplest possible way.
Use analogies, avoid jargon, and explain like you're teaching a beginner.

Topic: {topic}

Areas needing clarification:
{chr(10).join(f'- {area}' for area in weak_areas)}

Reference material:
{context}

Provide a clear, simple explanation with helpful analogies."""
    
    try:
        response = llm.invoke(prompt)
        state["feynman_explanation"] = response.content
    except Exception as e:
        print(f"Error generating Feynman explanation: {e}")
        state["feynman_explanation"] = f"Let's review {topic} in simpler terms. Focus on understanding the basic concepts first."
    
    state["status"] = "feynman_applied"
    
    return state

def mark_complete_and_progress(state: LearningState) -> LearningState:
    """Node 9: Mark checkpoint complete and move to next"""
    current_index = state.get("current_checkpoint_index", 0)
    state["current_checkpoint_index"] = current_index + 1
    state["status"] = "checkpoint_complete"
    
    # Clear previous checkpoint data
    state["questions"] = []
    state["learner_answers"] = []
    state["score"] = 0.0
    state["feynman_explanation"] = ""
    state["retry_count"] = 0
    
    return state

# ==================== ROUTING FUNCTIONS ====================

def route_after_validation(state: LearningState) -> str:
    """Route based on context validation"""
    retry_count = state.get("retry_count", 0)
    
    # Prevent infinite loops
    if retry_count >= 2:
        return "process_context"
    
    if state["status"] == "context_insufficient":
        return "gather_context"
    return "process_context"

def route_after_assessment(state: LearningState) -> str:
    """Route based on assessment score"""
    if state["status"] == "awaiting_answers":
        return END  # Wait for user input
    return "evaluate_score"

def route_after_evaluation(state: LearningState) -> str:
    """Route based on score evaluation"""
    if state["status"] == "passed":
        return "mark_complete"
    return "apply_feynman"

def route_after_feynman(state: LearningState) -> str:
    """After Feynman explanation, generate new questions"""
    return "generate_questions"

def route_after_checkpoint_complete(state: LearningState) -> str:
    """Check if more checkpoints exist"""
    current_index = state.get("current_checkpoint_index", 0)
    all_checkpoints = state.get("all_checkpoints", [])
    
    if current_index < len(all_checkpoints):
        return "define_checkpoint"
    return END

# ==================== BUILD GRAPH ====================

def build_learning_graph():
    """Build the LangGraph workflow"""
    
    workflow = StateGraph(LearningState)
    
    # Add nodes
    workflow.add_node("define_checkpoint", define_checkpoint)
    workflow.add_node("gather_context", gather_context)
    workflow.add_node("validate_context", validate_context)
    workflow.add_node("process_context", process_context)
    workflow.add_node("generate_questions", generate_questions)
    workflow.add_node("assess_learner", assess_learner)
    workflow.add_node("evaluate_score", evaluate_score)
    workflow.add_node("apply_feynman", apply_feynman_teaching)
    workflow.add_node("mark_complete", mark_complete_and_progress)
    
    # Set entry point
    workflow.set_entry_point("define_checkpoint")
    
    # Add edges
    workflow.add_edge("define_checkpoint", "gather_context")
    workflow.add_edge("gather_context", "validate_context")
    workflow.add_conditional_edges(
        "validate_context",
        route_after_validation,
        {
            "gather_context": "gather_context",
            "process_context": "process_context"
        }
    )
    workflow.add_edge("process_context", "generate_questions")
    workflow.add_edge("generate_questions", "assess_learner")
    workflow.add_conditional_edges(
        "assess_learner",
        route_after_assessment,
        {
            "evaluate_score": "evaluate_score",
            END: END
        }
    )
    workflow.add_conditional_edges(
        "evaluate_score",
        route_after_evaluation,
        {
            "mark_complete": "mark_complete",
            "apply_feynman": "apply_feynman"
        }
    )
    workflow.add_conditional_edges(
        "apply_feynman",
        route_after_feynman,
        {
            "generate_questions": "generate_questions"
        }
    )
    workflow.add_conditional_edges(
        "mark_complete",
        route_after_checkpoint_complete,
        {
            "define_checkpoint": "define_checkpoint",
            END: END
        }
    )
    
    # Set recursion limit to prevent infinite loops
    return workflow.compile()

# ==================== EXPORT ====================
if __name__ == "__main__":
    print("Learning Agent Graph Built Successfully!")
    print("Using Groq API with LangSmith Observability")
    graph = build_learning_graph()
    print("Graph compiled successfully!")