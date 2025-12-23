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

client = wrap_openai(AzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
))
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

search_tool = TavilySearchResults(max_results=1)

def gather_context_node(state: AgentState):
    checkpoint = state["active_checkpoint"]
    topic = checkpoint.topic
    objectives = checkpoint.objectives
    
    retry_count = state.get("retry_count", 0)
    feedback = state.get("feedback", "")
    logs = []
    current_context = ""
    
    time.sleep(2)
    
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
            logs.append(f"⚠️ Search Error: {str(e)}")

    return {"gathered_context": current_context, "retry_count": retry_count + 1, "logs": logs}

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

    return {"relevance_score": score, "feedback": hint, "logs": [f"✅ Validation: Score {score}/5. Reason: {reason}"]}

# NEW: Format content for presentation
def format_content_node(state: AgentState):
    checkpoint = state["active_checkpoint"]
    raw_context = state["gathered_context"]
    objectives = checkpoint.objectives
    logs = ["Formatting content for better readability..."]
    
    system_instruction = """You are an expert content formatter and educator.
    Transform raw text into clean, well-structured study material with:
    - Clear headings and subheadings
    - Bullet points for key concepts
    - Proper paragraph breaks
    - Highlight important terms
    - Remove duplicates and broken text
    Make it professional and easy to study."""
    
    user_prompt = f"""
    TOPIC: {checkpoint.topic}
    OBJECTIVES TO COVER: {', '.join(objectives)}
    
    RAW CONTENT:
    {raw_context[:4000]}
    
    Format this into clean, presentable study material suitable for learning.
    Use markdown formatting (headers, bullets, bold for key terms).
    """
    
    try:
        time.sleep(2)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=6000,
            model=deployment
        )
        
        formatted_content = response.choices[0].message.content
        logs.append("Content formatted successfully!")
        
    except Exception as e:
        formatted_content = raw_context  # Fallback to raw
        logs.append(f"⚠️ Formatting error, using raw content: {str(e)}")
    
    return {"formatted_content": formatted_content, "logs": logs}

def process_context_node(state: AgentState):
    # Use formatted content for chunking
    context = state.get("formatted_content", state["gathered_context"])
    logs = ["Processing context for question generation..."]
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(context)
    logs.append(f"Split into {len(chunks)} chunks.")
    
    try:
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment="text-embedding-ada-002",
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
        vector_store = FAISS.from_texts(chunks, embeddings)
        logs.append("Context embedded into vector store.")
    except Exception as e:
        logs.append(f"⚠️ Vector Store Warning: {str(e)}")
    
    return {"processed_context": chunks, "logs": logs}

def generate_quiz_from_context(chunks):
    if not chunks:
        return {"quiz_questions": []}
        
    quiz_context = chunks[0]
    quiz_questions = []
    
    max_retries = 2
    for attempt in range(max_retries):
        try:
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
                response_format={"type": "json_object"}
            )
            
            raw_json = response.choices[0].message.content
            data = json.loads(raw_json)
            
            if isinstance(data, dict) and "questions" in data:
                quiz_questions = data["questions"]
            
            if quiz_questions and len(quiz_questions) > 0:
                break
                
        except Exception as e:
            continue
    
    return {"quiz_questions": quiz_questions}

def generate_subjective_questions(chunks, topic):
    if not chunks:
        return {"subjective_questions": []}
    
    context = chunks[0][:2000]
    questions = []
    
    max_retries = 2
    for attempt in range(max_retries):
        try:
            time.sleep(2)
            
            system_instruction = "Generate open-ended, short answer type(expecting brief responses), subjective questions that test basic understanding."
            user_prompt = f"""
            Generate 3 subjective questions about '{topic}' based on this context asking simple short questions(1-2 lines answers).:
            {context}
            
            Return as JSON:
            {{
                "questions": ["Question 1?", "Question 2?", "Question 3?"]
            }}
            """
            
            response = client.chat.completions.create(
                messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": user_prompt}],
                max_completion_tokens=3000,
                model=deployment,
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response.choices[0].message.content)
            if "questions" in data:
                questions = data["questions"]
                break
        except:
            continue
    
    return {"subjective_questions": questions}

def decide_next_step(state: AgentState):
    if state["relevance_score"] >= 4 or state["retry_count"] >= 5:
        return "format"  # Go to formatting instead of direct processing
    return "retry"

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("gather_context", gather_context_node)
    workflow.add_node("validate_context", validate_context_node)
    workflow.add_node("format_content", format_content_node)  # NEW NODE
    workflow.add_node("process_context", process_context_node)
    
    workflow.add_edge(START, "gather_context")
    workflow.add_edge("gather_context", "validate_context")
    
    workflow.add_conditional_edges("validate_context", decide_next_step, 
        {"format": "format_content", "retry": "gather_context"}
    )
    
    workflow.add_edge("format_content", "process_context")  # Format before processing
    workflow.add_edge("process_context", END)
    
    return workflow.compile()