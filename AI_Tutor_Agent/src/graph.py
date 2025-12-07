import os
import time
from dotenv import load_dotenv
from openai import AzureOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from langsmith.wrappers import wrap_openai

load_dotenv()

# --- SETUP CLIENT ---
# We wrap the client for LangSmith tracing
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
    
    # Defensive: Pause to respect Student TPM limits
    time.sleep(2) 
    
    # 1. Check User Notes (First run only)
    if retry_count == 0 and state.get("user_notes") and len(state["user_notes"]) > 50:
        logs.append(f"Found user notes for '{topic}'. Using them.")
        current_context = state["user_notes"]
    
    # 2. Web Search
    else:
        # SMART RETRY LOGIC: Don't search for system errors
        if retry_count > 0:
            if "Reduce context" in feedback or "Error" in feedback:
                # If the previous error was technical, just search the original topic again (or simplified)
                query = f"Simple summary of {topic}"
                logs.append(f"Recovering from technical error. Searching for summary: '{query}'")
            else:
                # If feedback is real (content related), use it
                query = f"{topic}: {feedback}"
                logs.append(f"Retry #{retry_count}: Refining search: '{query}'")
        else:
            query = f"Explain {topic} covering: {', '.join(objectives)}"
            logs.append(f"Searching web for: '{query}'")
            
        try:
            raw_result = search_tool.invoke(query)
            
            # Robust Parsing for Tavily
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

    return {
        "gathered_context": current_context,
        "retry_count": retry_count + 1,
        "logs": logs
    }

# --- NODE 2: VALIDATE CONTEXT ---
def validate_context_node(state: AgentState):
    checkpoint = state["active_checkpoint"]
    context = state["gathered_context"]
    
    # Construct prompt
    objectives_str = ", ".join(checkpoint.objectives)
    
    # SOFT PROMPT: Less likely to trigger safety filters
    system_instruction = "Evaluate if the CONTEXT covers the OBJECTIVES."
    
    # TRUNCATION: Cut to 1000 chars to prevent 'Length' errors on Student accounts
    safe_context = context[:1000] 
    
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
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=1000, # Use max_tokens (standard) not max_completion_tokens
            model=deployment
        )
        
        choice = response.choices[0]
        ai_content = choice.message.content
        finish_reason = choice.finish_reason
        
        # --- DEBUGGING EMPTY RESPONSE ---
        if not ai_content:
            print(f"AZURE EMPTY RESPONSE | Reason: {finish_reason}")
            if finish_reason == "length":
                ai_content = "SCORE: 0 REASON: Output limit reached. SEARCH_HINT: Reduce context."
            elif finish_reason == "content_filter":
                ai_content = "SCORE: 1 REASON: Content blocked. SEARCH_HINT: Try safer terms."
            else:
                ai_content = f"SCORE: 0 REASON: Unknown error ({finish_reason})."

        # --- PARSING LOGIC ---
        import re
        
        score = 0
        reason = "Could not parse reason"
        hint = ""
        
        # 1. Score
        score_match = re.search(r'SCORE[:\s*]*(\d)', ai_content, re.IGNORECASE)
        if score_match:
            score = int(score_match.group(1))
        else:
            fallback_match = re.search(r'\b([1-5])\/5', ai_content)
            if fallback_match: score = int(fallback_match.group(1))
        
        # 2. Reason
        reason_match = re.search(r'REASON[:\s*]*(.*)', ai_content, re.IGNORECASE)
        if reason_match: reason = reason_match.group(1).strip()
            
        # 3. Hint
        hint_match = re.search(r'SEARCH_HINT[:\s*]*(.*)', ai_content, re.IGNORECASE)
        if hint_match: hint = hint_match.group(1).strip()

    except Exception as e:
        score = 0
        reason = f"System Error: {str(e)}"
        hint = "Retry with simpler terms"

    log_msg = f" Validation: Score {score}/5. Reason: {reason}"
    
    return {
        "relevance_score": score,
        "feedback": hint,
        "logs": [log_msg]
    }

def decide_next_step(state: AgentState):
    if state["relevance_score"] >= 4 or state["retry_count"] >= 5:
        return "end"
    return "retry"

def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("gather_context", gather_context_node)
    workflow.add_node("validate_context", validate_context_node)
    workflow.add_edge(START, "gather_context")
    workflow.add_edge("gather_context", "validate_context")
    workflow.add_conditional_edges("validate_context", decide_next_step, {"end": END, "retry": "gather_context"})
    return workflow.compile()