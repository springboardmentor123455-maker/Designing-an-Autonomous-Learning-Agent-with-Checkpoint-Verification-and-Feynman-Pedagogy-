import json  
import random
from typing import List
from models import AgentState, Checkpoint
from data import CHECKPOINTS
from config import llm, web_search  

# Milestone 2 Imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
 
# ---------- NODES (FUNCTIONS) ----------

def define_checkpoint(state: AgentState) -> AgentState:
    selected_checkpoint = state.get("selected_checkpoint", "cp1")
    checkpoint = CHECKPOINTS[selected_checkpoint]
    print(f"\n[define_checkpoint] Selected checkpoint: {checkpoint['id']} - {checkpoint['topic']}")

    attempts = state.get("attempts", 0)

    return {
        "checkpoint": checkpoint,
        "attempts": attempts,
    }


def gather_context(state: AgentState) -> AgentState:
    """
    Gathers context for the current checkpoint.
    """
    checkpoint = state["checkpoint"]
    user_notes = state.get("user_notes", "").strip()

    print("\n[gather_context] Gathering context...")
    context_chunks: List[str] = []

    # 1. Add user notes if provided
    if user_notes:
        print("[gather_context] Using user-provided notes.")
        context_chunks.append("USER NOTES:\n" + user_notes)

    # 2. Always do a small web search to enrich context
    search_query = f"{checkpoint['topic']} - " + "; ".join(checkpoint["objectives"])
    print(f"[gather_context] Web search query: {search_query}")

    try:
        search_result = web_search.run(search_query)
        context_chunks.append("WEB SEARCH RESULT:\n" + str(search_result))
    except Exception as e:
        print(f"[gather_context] Web search failed: {e}")

    combined_context = "\n\n".join(context_chunks)
    attempts = state.get("attempts", 0) + 1

    return {
        "context": combined_context,
        "attempts": attempts,
    }


def _build_relevance_prompt(checkpoint: Checkpoint, context: str) -> str:
    objectives_text = "\n".join(f"- {obj}" for obj in checkpoint["objectives"])
    prompt = f"""
You are evaluating learning materials for a student.

Checkpoint topic:
{checkpoint['topic']}

Learning objectives:
{objectives_text}

Success criteria:
{checkpoint['success_criteria']}

Context to evaluate:
\"\"\"{context[:4000]}\"\"\"

Task:
1. Judge how relevant the context is to the objectives (1 = useless, 5 = highly relevant).
2. Only reply with a single number from 1 to 5.
"""
    return prompt


def validate_context(state: AgentState) -> AgentState:
    checkpoint = state["checkpoint"]
    context = state.get("context", "")

    if not context.strip():
        print("\n[validate_context] No context to evaluate. Setting score = 1.")
        return {"relevance_score": 1.0}

    print("\n[validate_context] Evaluating context relevance with LLM...")
    prompt = _build_relevance_prompt(checkpoint, context)
    response = llm.invoke(prompt)
    raw_text = response.content.strip()

    try:
        score = float(raw_text)
    except Exception:
        print(f"[validate_context] Could not parse score from '{raw_text}', defaulting to 2.")
        score = 2.0

    print(f"[validate_context] Relevance score = {score}/5")
    return {"relevance_score": score}


def needs_refetch(state: AgentState) -> str:
    score = state.get("relevance_score", 0)
    attempts = state.get("attempts", 0)

    if score < 4 and attempts < 3:
        return "refetch"

    return "process"  # Proceed to Milestone 2 steps


# ---------- MILESTONE 2 NODES ----------

def process_context(state: AgentState) -> AgentState:
    """
    Chunk context, embed, and store in ephemeral vector store.
    """
    print("\n[process_context] Chunking and embedding context...")
    context = state.get("context", "")
    
    # Chunking
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = [Document(page_content=chunk) for chunk in splitter.split_text(context)]
    
    # Embedding (Ephemeral Chroma)
    # Note: In a real app we might pass this vector_store object around or re-init it.
    # For this milestone, just proving the step works is enough.
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name="temp_session_context"
    )
    
    # We can't easily pass the complex vector_store object in the serializable state 
    # unless we use a robust persistence layer. 
    # For now, we assume the 'context' string is sufficient for the LLM to generate stats,
    # OR we could query the store here if needed.
    # Since we aren't doing RAG for the quiz yet (we just pass context to LLM), 
    # we simulate the "Availability" of the vector store.
    
    print(f"[process_context] Created {len(docs)} chunks and stored in ephemeral vector store.")
    return {}


def create_study_guide(state: AgentState) -> AgentState:
    """
    Summarizes the context into a study guide for the user.
    """
    print("\n[create_study_guide] Generating study material...")
    checkpoint = state["checkpoint"]
    context = state.get("context", "")
    
    prompt = f"""
You are an expert teacher. Create a concise Study Guide for the student based on the following context.
Topic: {checkpoint['topic']}
Context:
\"\"\"{context[:4000]}\"\"\"

Format:
1. **Key Concepts**: Bullet points of main ideas.
2. **Summary**: A short paragraph explaining the topic.
3. Keep it readable and clear.
"""
    response = llm.invoke(prompt)
    study_material = response.content.strip()
    
    print(f"\n\n=== STUDY GUIDE: {checkpoint['id'].upper()} ===\n")
    print(study_material)
    print("\n" + "="*40 + "\n")
    
    input("Press Enter when you are ready to take the quiz...")
    return {}


def generate_quiz(state: AgentState) -> AgentState:
    """
    Generate 3-5 MCQs based on gathered context.
    """
    print("\n[generate_quiz] Generating MCQs...")
    checkpoint = state["checkpoint"]
    context = state["context"]
    
    objectives_text = "\n".join(f"- {obj}" for obj in checkpoint["objectives"])
    
    prompt = f"""
You are an expert teacher. Generate EXACTLY 4 multiple-choice questions (MCQs) to test a student's understanding 
of the following material, based strictly on the provided context.

Topic: {checkpoint['topic']}
Objectives:
{objectives_text}

Context:
\"\"\"{context[:4000]}\"\"\"

Output Format: A pure JSON list of objects. No markdown, no pre-text.
[
  {{
    "question": "Question text here",
    "options": {{
        "A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"
    }},
    "correct_option": "B",
    "explanation": "Brief explanation of why B is correct."
  }}
]
"""
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        # Clean potential markdown wrapping
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        elif content.startswith("```"):
            content = content.replace("```", "")
            
        quiz_questions = json.loads(content)
        print(f"[generate_quiz] Generated {len(quiz_questions)} questions.")
    except Exception as e:
        print(f"[generate_quiz] Failed to generate valid JSON: {e}")
        # Fallback dummy question for stability
        quiz_questions = [{
            "question": "Which of the following describes an AI Agent? (Fallback)",
            "options": {"A": "A Rock", "B": "An actuator", "C": "An entity that perceives and acts", "D": "A database"},
            "correct_option": "C",
            "explanation": "AI Agents are defined by their ability to perceive their environment and take actions."
        }]

    return {"quiz_questions": quiz_questions}


def take_quiz(state: AgentState) -> AgentState:
    """
    Presents the quiz to the user and collects answers interactively.
    """
    checkpoint = state.get("checkpoint", {})
    cp_id = checkpoint.get("id", "UNKNOWN")
    cp_topic = checkpoint.get("topic", "Quiz")
    print(f"\n\n=== {cp_id.upper()} QUIZ: {cp_topic} ===")
    questions = state.get("quiz_questions", [])
    answers = {}
    
    if not questions:
        print("No questions generated.")
        return {"quiz_answers": {}}

    for i, q in enumerate(questions):
        print(f"\nQuestion {i+1}: {q['question']}")
        
        # Determine strict option order for consistency, though dictionary is usually fine
        # q["options"] is expected to be {"A": "...", "B": "..."}
        options = q.get("options", {})
        sorted_keys = sorted(options.keys())
        
        for key in sorted_keys:
            print(f"  {key}) {options[key]}")
            
        while True:
            user_input = input(f"Your answer (A/B/C/D): ").strip().upper()
            if user_input in sorted_keys:
                answers[i] = user_input
                break
            print("Invalid input. Please enter A, B, C, or D.")

    return {"quiz_answers": answers}


def evaluate_quiz(state: AgentState) -> AgentState:
    print("\n[evaluate_quiz] Scoring quiz...")
    questions = state.get("quiz_questions", [])
    answers = state.get("quiz_answers", {})
    
    correct_count = 0
    total = len(questions)
    
    if total == 0:
        return {"quiz_score": 0.0, "quiz_result": "FAILED"}
        
    for i, q in enumerate(questions):
        if answers.get(i) == q["correct_option"]:
            correct_count += 1
            
    score_pct = (correct_count / total) * 100
    result = "PASSED" if score_pct >= 70 else "FAILED"
    
    print(f"[evaluate_quiz] Score: {score_pct:.1f}% ({result})")
    
    # Identify gaps
    knowledge_gaps = []
    if result == "FAILED":
        for i, q in enumerate(questions):
            if answers.get(i) != q["correct_option"]:
                # Simply use the question text as the "gap" for now, or extract keywords
                gap = q.get("question", "Unknown Concept")
                knowledge_gaps.append(gap)
                
    return {
        "quiz_score": score_pct,
        "quiz_result": result,
        "knowledge_gaps": knowledge_gaps
    }

def check_progression(state: AgentState) -> str:
    result = state.get("quiz_result", "FAILED")
    loop_count = state.get("loop_count", 0)
    
    if result == "PASSED":
        return "pass"
        
    if loop_count < 3:
        return "remediate"
        
    return "fail"


# Milestone 3: Feynman Remediation Node
def feynman_remediation(state: AgentState) -> AgentState:
    print("\n[feynman_remediation] Analyzing knowledge gaps...")
    gaps = state.get("knowledge_gaps", [])
    context = state.get("context", "")
    loop_count = state.get("loop_count", 0) + 1
    
    if not gaps:
        print("[feynman_remediation] No specific gaps identified. Reviewing general topic.")
        gaps_text = "General overview of the topic."
    else:
        gaps_text = "\n".join(f"- {gap}" for gap in gaps)
        
    print(f"[feynman_remediation] Gaps to explain:\n{gaps_text}")
    
    prompt = f"""
You are an expert tutor using the Feynman Technique. 
The student failed a quiz on these specific concepts/questions:
{gaps_text}

Context:
\"\"\"{context[:3000]}\"\"\"

Task:
1. Explain these concepts in simple, plain English.
2. Use an analogy if possible.
3. Keep it concise (max 200 words).
"""
    response = llm.invoke(prompt)
    explanation = response.content.strip()
    
    print("\n=== FEYNMAN EXPLANATION ===")
    print(explanation)
    print("===========================\n")
    
    return {
        "feynman_explanation": explanation,
        "loop_count": loop_count
    }
