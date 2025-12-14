import os
import time
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from langsmith.wrappers import wrap_openai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings

load_dotenv()

# --- SETUP CLIENT ---
client = wrap_openai(AzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
))
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

search_tool = TavilySearchResults(max_results=1)

# --- NODE 1: GATHER CONTEXT ---
def gather_context_node(state: AgentState):
    checkpoint = state["active_checkpoint"]
    topic = checkpoint.topic
    objectives = checkpoint.objectives
    
    retry_count = state.get("retry_count", 0)
    feedback = state.get("feedback", "")
    logs = []
    current_context = ""
    
    time.sleep(2) # Safe for student account
    
    if retry_count == 0 and state.get("user_notes") and len(state["user_notes"]) > 50:
        logs.append(f"Found user notes for '{topic}'. Using them.")
        current_context = state["user_notes"]
    else:
        if retry_count > 0:
            if "Reduce context" in feedback or "Error" in feedback:
                query = f"Simple summary of {topic}"
                logs.append(f"Recovering from technical error. Searching for summary: '{query}'")
            else:
                query = f"{topic}: {feedback}"
                logs.append(f"Retry #{retry_count}: Refining search: '{query}'")
        else:
            query = f"Explain {topic} covering: {', '.join(objectives)}"
            logs.append(f"Searching web for: '{query}'")
            
        try:
            raw_result = search_tool.invoke(query)
            if isinstance(raw_result, dict) and "results" in raw_result:
                current_context = "\n".join([r.get('content', '') for r in raw_result["results"]])
            elif isinstance(raw_result, list):
                current_context = "\n".join([r.get('content', '') for r in raw_result if isinstance(r, dict)])
            elif isinstance(raw_result, str):
                current_context = raw_result
            else:
                current_context = "Error: Search returned no text."
        except Exception as e:
            current_context = f"Search Failed: {str(e)}"
            logs.append(f" Search Error: {str(e)}")

    return {"gathered_context": current_context, "retry_count": retry_count + 1, "logs": logs}

# --- NODE 2: VALIDATE CONTEXT ---
def validate_context_node(state: AgentState):
    checkpoint = state["active_checkpoint"]
    context = state["gathered_context"]
    objectives_str = ", ".join(checkpoint.objectives)
    
    safe_context = context[:3000] 
    
    system_instruction = "Evaluate if the CONTEXT covers the OBJECTIVES."
    user_prompt = f"""
    TOPIC: {checkpoint.topic}
    OBJECTIVES: {objectives_str}
    SUCCESS CRITERIA: {checkpoint.success_criteria}
    CONTEXT: {safe_context}
    
    Return evaluation in this format:
    SCORE: [1-5]
    REASON: [1 sentence explanation]
    SEARCH_HINT: [Short phrase]
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": user_prompt}],
            max_completion_tokens=5000, 
            model=deployment
        )
        choice = response.choices[0]
        ai_content = choice.message.content
        finish_reason = choice.finish_reason
        
        if not ai_content:
            if finish_reason == "length": ai_content = "SCORE: 0 REASON: Output limit. SEARCH_HINT: Reduce context."
            else: ai_content = f"SCORE: 0 REASON: Error ({finish_reason})."

        import re
        score = 0
        reason = "Parse Error"
        hint = ""
        
        score_match = re.search(r'SCORE[:\s*]*(\d)', ai_content, re.IGNORECASE)
        if score_match: score = int(score_match.group(1))
        else:
            fb = re.search(r'\b([1-5])\/5', ai_content)
            if fb: score = int(fb.group(1))
        
        reason_match = re.search(r'REASON[:\s*]*(.*)', ai_content, re.IGNORECASE)
        if reason_match: reason = reason_match.group(1).strip()
            
        hint_match = re.search(r'SEARCH_HINT[:\s*]*(.*)', ai_content, re.IGNORECASE)
        if hint_match: hint = hint_match.group(1).strip()

    except Exception as e:
        score = 0
        reason = str(e)
        hint = "Retry"

    return {"relevance_score": score, "feedback": hint, "logs": [f" Validation: Score {score}/5. Reason: {reason}"]}

# --- NODE 3: PROCESS CONTEXT ---
def process_context_node(state: AgentState):
    context = state["gathered_context"]
    logs = ["Processing context for quiz generation..."]
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(context)
    logs.append(f"Split context into {len(chunks)} chunks.")
    
    try:
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment="text-embedding-ada-002",
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
        vector_store = FAISS.from_texts(chunks, embeddings)
        logs.append("Context successfully embedded into FAISS vector store.")
    except Exception as e:
        logs.append(f"Vector Store Warning: {str(e)} (Continuing with raw text)")
    
    return {"processed_context": chunks, "logs": logs}

# --- NODE 4: GENERATE QUIZ (ROBUST & SELF-HEALING) ---
def generate_quiz_node(state: AgentState):
    chunks = state.get("processed_context", [])
    if not chunks:
        return {"logs": ["⚠️ Error: No processed text found for quiz generation."]}
        
    # Use just the first chunk
    quiz_context = chunks[0]
    
    logs = ["Generating quiz questions..."]
    quiz_questions = []
    
    # --- INTERNAL RETRY LOOP (Max 2 Attempts) ---
    max_retries = 2
    for attempt in range(max_retries):
        try:
            # Sleep slightly to respect rate limits, especially on retry
            time.sleep(2) 
            
            system_instruction = "You are a quiz generator. Output valid JSON with a 'questions' key."
            user_prompt = f"""
            Generate 5 multiple-choice questions based on this text.
            TEXT: {quiz_context[:2000]}
            
            REQUIRED JSON FORMAT:
            {{
                "questions": [
                    {{
                        "question": "Question text?",
                        "options": ["A) Opt1", "B) Opt2", "C) Opt3", "D) Opt4"],
                        "answer": "A) Opt1"
                    }}
                ]
            }}
            """
            
            response = client.chat.completions.create(
                messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": user_prompt}],
                max_completion_tokens=5000,
                model=deployment,
                response_format={"type": "json_object"} # We now explicitly ask for an Object in the prompt too
            )
            
            raw_json = response.choices[0].message.content
            # Debug log to see exactly what we got (helpful if it fails)
            logs.append(f"DEBUG (Attempt {attempt+1}): {raw_json[:50]}...") 
            
            data = json.loads(raw_json)
            
            # Strict extraction
            if isinstance(data, dict) and "questions" in data:
                quiz_questions = data["questions"]
            
            # VALIDATION: Did we actually get questions?
            if quiz_questions and len(quiz_questions) > 0:
                logs.append(f"✅ Generated {len(quiz_questions)} quiz questions on attempt {attempt+1}.")
                break # Success! Exit the loop.
            else:
                logs.append(f"⚠️ Attempt {attempt+1} returned valid JSON but no questions. Retrying...")
                
        except Exception as e:
            logs.append(f"❌ Attempt {attempt+1} Error: {str(e)}")
    
    # Final check
    if not quiz_questions:
        logs.append("❌ Failed to generate quiz after retries.")

    return {"quiz_questions": quiz_questions, "logs": logs}

# --- EDGE LOGIC ---
def decide_next_step(state: AgentState):
    if state["relevance_score"] >= 4 or state["retry_count"] >= 5:
        return "process"
    return "retry"

# --- GRAPH ---
def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("gather_context", gather_context_node)
    workflow.add_node("validate_context", validate_context_node)
    workflow.add_node("process_context", process_context_node)
    workflow.add_node("generate_quiz", generate_quiz_node)
    
    workflow.add_edge(START, "gather_context")
    workflow.add_edge("gather_context", "validate_context")
    
    workflow.add_conditional_edges("validate_context", decide_next_step, 
        {"process": "process_context", "retry": "gather_context"}
    )
    
    workflow.add_edge("process_context", "generate_quiz")
    workflow.add_edge("generate_quiz", END)
    
    return workflow.compile()