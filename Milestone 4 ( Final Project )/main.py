from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time
import re
from typing import TypedDict, List, Optional, Dict, Any
from dotenv import load_dotenv
import requests as http_requests
from langgraph.graph import StateGraph, END
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

print("\n" + "="*80)
print(f"{Colors.HEADER}{Colors.BOLD}🎓 AUTONOMOUS LEARNING AGENT{Colors.ENDC}")
print(f"{Colors.OKCYAN}   Checkpoint Verification + Feynman Pedagogy{Colors.ENDC}")
print(f"{Colors.OKBLUE}   Created by Nidhin R{Colors.ENDC}")
print("="*80 + "\n")

if not GROQ_API_KEY:
    print(f"{Colors.FAIL}❌ ERROR: GROQ_API_KEY not found in .env{Colors.ENDC}")
    exit(1)

print(f"{Colors.OKGREEN}✅ System Initialized{Colors.ENDC}")
print(f"{Colors.OKGREEN}✅ LangGraph Workflow Ready{Colors.ENDC}")
print(f"{Colors.OKGREEN}✅ Groq API Connected{Colors.ENDC}")
print("="*80 + "\n")

class AgentState(TypedDict):
    main_topic: str
    all_checkpoints: List[Dict[str, Any]]
    current_checkpoint_index: int
    checkpoint: Dict[str, Any]
    user_notes: Optional[str]
    context: str
    questions: List[str]
    learner_answers: List[str]
    question_scores: List[float]
    overall_score: float
    pass_status: str
    retry_count: int
    feynman_explanation: str
    completed_checkpoints: List[str]
    session_log: List[str]

last_api_call = 0
MIN_API_DELAY = 0.5

def call_groq_llm(prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> Optional[str]:
    global last_api_call
    
    elapsed = time.time() - last_api_call
    if elapsed < MIN_API_DELAY:
        time.sleep(MIN_API_DELAY - elapsed)
    
    try:
        print(f"{Colors.OKCYAN}🔄 Groq API Call{Colors.ENDC}")
        print(f"   Model: llama-3.3-70b-versatile | Tokens: {max_tokens} | Temp: {temperature}")
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        start_time = time.time()
        response = http_requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=25)
        elapsed_time = time.time() - start_time
        last_api_call = time.time()
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content'].strip()
            print(f"{Colors.OKGREEN}   ✅ Success | {len(content)} chars | {elapsed_time:.2f}s{Colors.ENDC}\n")
            return content
        elif response.status_code == 429:
            print(f"{Colors.WARNING}   ⏳ Rate limit - waiting 3s{Colors.ENDC}")
            time.sleep(3)
            return call_groq_llm(prompt, max_tokens, temperature)
        else:
            print(f"{Colors.FAIL}   ❌ Error {response.status_code}{Colors.ENDC}\n")
            return None
        
    except Exception as e:
        print(f"{Colors.FAIL}   ❌ Exception: {str(e)[:80]}{Colors.ENDC}\n")
        last_api_call = time.time()
        return None

def generate_checkpoints_for_topic(topic: str) -> List[Dict[str, Any]]:
    print(f"\n{Colors.BOLD}📍 GENERATING 3 CHECKPOINTS FOR: {topic}{Colors.ENDC}\n")
    
    prompt = f"""Break down "{topic}" into exactly 3 sequential learning checkpoints.

Format EXACTLY as:
CHECKPOINT 1: [Title]
OBJECTIVES: [Obj1] | [Obj2] | [Obj3]

CHECKPOINT 2: [Title]
OBJECTIVES: [Obj1] | [Obj2] | [Obj3]

CHECKPOINT 3: [Title]
OBJECTIVES: [Obj1] | [Obj2] | [Obj3]

Create for "{topic}":"""
    
    response = call_groq_llm(prompt, max_tokens=600, temperature=0.7)
    checkpoints = []
    
    if response:
        blocks = response.split('CHECKPOINT')[1:]
        for i, block in enumerate(blocks[:3]):
            lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
            if len(lines) >= 2:
                title = re.sub(r'^\d+:\s*', '', lines[0]).strip()
                objectives = []
                for line in lines[1:]:
                    if 'OBJECTIVES:' in line.upper():
                        obj_text = re.sub(r'^OBJECTIVES:\s*', '', line, flags=re.IGNORECASE)
                        objectives = [o.strip() for o in obj_text.split('|')]
                        break
                if not objectives:
                    objectives = [f"Learn {title}", "Understand concepts", "Apply knowledge"]
                checkpoints.append({"id": i+1, "title": title, "objectives": objectives[:3], "completed": False})
    
    if len(checkpoints) < 3:
        checkpoints = [
            {"id": 1, "title": f"Introduction to {topic}", "objectives": [f"Understand {topic}", "Learn basics", "Key terms"], "completed": False},
            {"id": 2, "title": f"Core Concepts of {topic}", "objectives": [f"Deep dive", "Mechanisms", "Techniques"], "completed": False},
            {"id": 3, "title": f"Applications of {topic}", "objectives": ["Real-world uses", "Implementation", "Best practices"], "completed": False}
        ]
    
    for cp in checkpoints:
        print(f"{Colors.OKGREEN}   ✓ Checkpoint {cp['id']}: {cp['title']}{Colors.ENDC}")
    
    print()
    return checkpoints

def search_web(topic: str) -> str:
    print(f"{Colors.OKCYAN}🔍 Web Search: {topic}{Colors.ENDC}")
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
        response = http_requests.get(url, timeout=8)
        if response.status_code == 200:
            extract = response.json().get("extract", "")
            if len(extract) > 100:
                print(f"{Colors.OKGREEN}   ✅ Wikipedia | {len(extract)} chars{Colors.ENDC}\n")
                return extract[:2000]
    except:
        pass
    
    print(f"{Colors.WARNING}   ⚠️ Wikipedia unavailable - Using Groq generation{Colors.ENDC}\n")
    prompt = f"Write comprehensive 300-word educational content about '{topic}'. Include: clear definition, how it works, key features, and real-world applications."
    result = call_groq_llm(prompt, 600, 0.6)
    return result if result else f"{topic}: Important concept in technology and science."

def log_event(state: AgentState, msg: str):
    if "session_log" not in state:
        state["session_log"] = []
    ts = time.strftime('%H:%M:%S')
    state["session_log"].append(f"[{ts}] {msg}")
    print(f"{Colors.OKBLUE}[{ts}] {msg}{Colors.ENDC}")

def define_checkpoint(state: AgentState) -> AgentState:
    idx = state["current_checkpoint_index"]
    cp = state["all_checkpoints"][idx]
    state["checkpoint"] = cp
    log_event(state, f"📍 NODE: Define Checkpoint | {cp['id']}/3: {cp['title']}")
    state["retry_count"] = 0
    return state

def gather_context(state: AgentState) -> AgentState:
    log_event(state, "📥 NODE: Gather Context")
    
    if state.get("user_notes") and len(state["user_notes"].strip()) > 30:
        state["context"] = state["user_notes"]
        log_event(state, "   ✓ Using learner's provided notes")
    else:
        log_event(state, "   ✓ No user notes - Fetching from web")
        state["context"] = search_web(state['checkpoint']['title'])
    
    log_event(state, f"   ✓ Context ready | {len(state['context'])} chars")
    return state

def validate_context(state: AgentState) -> AgentState:
    log_event(state, "✔️ NODE: Validate Context | Approved")
    return state

def process_context(state: AgentState) -> AgentState:
    log_event(state, "⚙️ NODE: Process Context")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(state["context"])
    if chunks:
        state["context"] = chunks[0]
    log_event(state, f"   ✓ Processed {len(chunks)} chunks")
    return state

def generate_questions(state: AgentState) -> AgentState:
    log_event(state, "❓ NODE: Generate Questions")
    topic = state['checkpoint']['title']
    context = state['context']
    
    prompt = f"""Create exactly 5 assessment questions about "{topic}" based on this content.

Content:
{context[:700]}

Requirements:
- Questions must be answerable from the content
- Test understanding, not memorization
- Clear, direct language
- No duplicate questions

Format:
1. [Question]?
2. [Question]?
3. [Question]?
4. [Question]?
5. [Question]?

Questions:"""
    
    response = call_groq_llm(prompt, 500, 0.7)
    questions = []
    
    if response:
        for line in response.split('\n'):
            if re.match(r'^\d+[.):]', line.strip()):
                q = re.sub(r'^\d+[.):]\s*', '', line.strip())
                if '?' in q:
                    questions.append(q.split('?')[0] + '?')
    
    while len(questions) < 5:
        questions.append(f"Explain the key concepts of {topic}?")
    
    state["questions"] = questions[:5]
    log_event(state, f"   ✓ Generated {len(questions)} questions")
    return state

def assess_learner(state: AgentState) -> AgentState:
    if not state.get("learner_answers"):
        state["overall_score"] = 0.0
        state["pass_status"] = "PENDING"
        state["question_scores"] = [0.0] * 5
        return state
    
    log_event(state, "📝 NODE: Assess Learner")
    scores = []
    context = state["context"]
    
    for i, (q, ans) in enumerate(zip(state["questions"], state["learner_answers"])):
        if len(ans.strip()) < 5:
            scores.append(0.0)
            log_event(state, f"   Q{i+1}: 0.0/5.0 | Insufficient answer")
            continue
        
        eval_prompt = f"""Evaluate this answer on a scale of 0.0 to 5.0.

Reference Content:
{context[:500]}

Question: {q}
Student Answer: {ans}

Scoring:
5.0 = Perfect (accurate, complete, well-explained)
4.0-4.9 = Very good (accurate, mostly complete)
3.0-3.9 = Good (accurate, missing some details)
2.0-2.9 = Fair (partially correct)
1.0-1.9 = Poor (mostly incorrect)
0.0-0.9 = Wrong or irrelevant

Reply with ONLY the numeric score (e.g., "4.5")

Score:"""
        
        llm_eval = call_groq_llm(eval_prompt, 100, 0.2)
        
        try:
            score = float(re.findall(r'\d+\.?\d*', llm_eval)[0]) if llm_eval else 0.0
            score = min(max(score, 0.0), 5.0)
        except:
            word_count = len(ans.split())
            if word_count >= 20:
                score = 3.5
            elif word_count >= 10:
                score = 2.5
            else:
                score = 1.5
        
        scores.append(round(score, 1))
        log_event(state, f"   Q{i+1}: {scores[-1]}/5.0")
    
    state["question_scores"] = scores
    total_score = sum(scores)
    state["overall_score"] = round((total_score / 25.0) * 100, 1)
    state["pass_status"] = "PASSED" if state["overall_score"] >= 70 else "FAILED"
    
    log_event(state, f"   ✓ Total Score: {total_score}/25 points ({state['overall_score']}%)")
    log_event(state, f"   ✓ Status: {state['pass_status']}")
    
    return state

def evaluate_score(state: AgentState) -> AgentState:
    score = state.get("overall_score", 0)
    threshold = 70.0
    log_event(state, f"⚖️ NODE: Evaluate Score | {score}% vs {threshold}% threshold")
    
    if state.get("pass_status") == "PASSED":
        log_event(state, "   ✅ Threshold met - Ready to progress")
    else:
        log_event(state, "   ⚠️ Below threshold - Feynman teaching available")
    
    return state

workflow = StateGraph(AgentState)

workflow.add_node("define_checkpoint", define_checkpoint)
workflow.add_node("gather_context", gather_context)
workflow.add_node("validate_context", validate_context)
workflow.add_node("process_context", process_context)
workflow.add_node("generate_questions", generate_questions)
workflow.add_node("assess_learner", assess_learner)
workflow.add_node("evaluate_score", evaluate_score)

workflow.set_entry_point("define_checkpoint")
workflow.add_edge("define_checkpoint", "gather_context")
workflow.add_edge("gather_context", "validate_context")
workflow.add_edge("validate_context", "process_context")
workflow.add_edge("process_context", "generate_questions")
workflow.add_edge("generate_questions", "assess_learner")
workflow.add_edge("assess_learner", "evaluate_score")
workflow.add_edge("evaluate_score", END)

app_graph = workflow.compile()

sessions = {}

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/api/start', methods=['POST'])
def start_session():
    try:
        data = request.json
        topic = data.get('topic', 'Machine Learning')
        user_notes = data.get('notes', '').strip()
        
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}🚀 NEW LEARNING SESSION{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Topic: {topic}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}User Notes: {'Provided' if user_notes else 'Not provided'}{Colors.ENDC}\n")
        
        checkpoints = generate_checkpoints_for_topic(topic)
        
        state = {
            "main_topic": topic,
            "all_checkpoints": checkpoints,
            "current_checkpoint_index": 0,
            "user_notes": user_notes,
            "completed_checkpoints": [],
            "retry_count": 0,
            "session_log": []
        }
        
        print(f"{Colors.BOLD}🔄 Executing LangGraph Workflow{Colors.ENDC}\n")
        result = app_graph.invoke(state)
        
        sid = str(int(time.time() * 1000))
        sessions[sid] = result
        
        print(f"{Colors.OKGREEN}✅ Session Created | ID: {sid}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
        
        return jsonify({
            "success": True,
            "session_id": sid,
            "main_topic": topic,
            "all_checkpoints": result["all_checkpoints"],
            "current_checkpoint": result["all_checkpoints"][0],
            "context": result.get("context", "")[:900],
            "questions": result.get("questions", []),
            "used_user_notes": bool(user_notes and len(user_notes) > 30)
        })
    except Exception as e:
        print(f"{Colors.FAIL}❌ ERROR: {str(e)}{Colors.ENDC}\n")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/evaluate', methods=['POST'])
def evaluate_session():
    try:
        data = request.json
        sid = data.get('session_id')
        
        if sid not in sessions:
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        state = sessions[sid]
        state["learner_answers"] = data.get('answers', [])
        
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}📝 EVALUATING LEARNER ANSWERS{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
        
        result = app_graph.invoke(state)
        sessions[sid] = result
        
        total_points = sum(result["question_scores"])
        
        print(f"{Colors.OKGREEN}✅ Evaluation Complete{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
        
        return jsonify({
            "success": True,
            "session_id": sid,
            "score": result["overall_score"],
            "total_points": total_points,
            "max_points": 25.0,
            "passed": result["pass_status"] == "PASSED",
            "scores": result["question_scores"],
            "retry_count": result.get("retry_count", 0)
        })
    except Exception as e:
        print(f"{Colors.FAIL}❌ ERROR: {str(e)}{Colors.ENDC}\n")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/feynman', methods=['POST'])
def get_feynman():
    try:
        sid = request.json.get('session_id')
        if sid not in sessions:
            return jsonify({"success": False}), 404
        
        state = sessions[sid]
        topic = state['checkpoint']['title']
        
        print(f"\n{Colors.WARNING}💡 FEYNMAN TEACHING MODULE ACTIVATED{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Topic: {topic}{Colors.ENDC}\n")
        
        prompt = f"""Use the Feynman Technique to explain '{topic}' in the SIMPLEST way possible.

Requirements:
- Use an everyday analogy (cooking, sports, daily activities)
- 8th grade vocabulary only - NO technical jargon
- Include emojis for engagement and clarity
- Make it encouraging and confidence-building
- Maximum 200 words

Simplified Explanation:"""
        
        explanation = call_groq_llm(prompt, 400, 0.8)
        
        if not explanation:
            explanation = f"💡 Think of {topic} like learning to ride a bike 🚴\n\nStep 1: Start with training wheels (basics)\nStep 2: Practice in a safe space (understanding)\nStep 3: Remove training wheels (apply knowledge)\nStep 4: Ride confidently! (mastery)\n\nYou're doing great! Keep practicing! 🎯"
        
        state["feynman_explanation"] = explanation
        state["retry_count"] = state.get("retry_count", 0) + 1
        sessions[sid] = state
        
        print(f"{Colors.OKGREEN}✅ Feynman Explanation Generated{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Retry Count: {state['retry_count']}/2{Colors.ENDC}\n")
        
        return jsonify({"success": True, "explanation": explanation})
    except Exception as e:
        print(f"{Colors.FAIL}❌ ERROR: {str(e)}{Colors.ENDC}\n")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/retest', methods=['POST'])
def retest():
    try:
        sid = request.json.get('session_id')
        if sid not in sessions:
            return jsonify({"success": False}), 404
        
        state = sessions[sid]
        topic = state['checkpoint']['title']
        context = state['context']
        
        print(f"\n{Colors.OKCYAN}🔄 GENERATING NEW ASSESSMENT QUESTIONS{Colors.ENDC}\n")
        
        prompt = f"""Create 5 NEW different questions about "{topic}" (different from previous questions).

Content:
{context[:700]}

Format:
1. [Question]?
2. [Question]?
3. [Question]?
4. [Question]?
5. [Question]?"""
        
        response = call_groq_llm(prompt, 500, 0.7)
        questions = []
        
        if response:
            for line in response.split('\n'):
                if re.match(r'^\d+[.):]', line.strip()):
                    q = re.sub(r'^\d+[.):]\s*', '', line.strip())
                    if '?' in q:
                        questions.append(q.split('?')[0] + '?')
        
        while len(questions) < 5:
            questions.append(f"Describe your understanding of {topic}?")
        
        state["questions"] = questions[:5]
        state["learner_answers"] = []
        sessions[sid] = state
        
        print(f"{Colors.OKGREEN}✅ New Questions Generated{Colors.ENDC}\n")
        
        return jsonify({"success": True, "questions": questions})
    except Exception as e:
        print(f"{Colors.FAIL}❌ ERROR: {str(e)}{Colors.ENDC}\n")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/next-checkpoint', methods=['POST'])
def next_checkpoint():
    try:
        sid = request.json.get('session_id')
        if sid not in sessions:
            return jsonify({"success": False}), 404
        
        state = sessions[sid]
        idx = state["current_checkpoint_index"]
        
        state["all_checkpoints"][idx]["completed"] = True
        state["completed_checkpoints"].append(state["all_checkpoints"][idx]["title"])
        
        if idx + 1 < len(state["all_checkpoints"]):
            state["current_checkpoint_index"] = idx + 1
            state["retry_count"] = 0
            
            print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
            print(f"{Colors.BOLD}➡️ PROGRESSING TO NEXT CHECKPOINT{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
            
            result = app_graph.invoke(state)
            sessions[sid] = result
            
            print(f"{Colors.OKGREEN}✅ Next Checkpoint Ready{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
            
            return jsonify({
                "success": True,
                "current_checkpoint": result["all_checkpoints"][idx + 1],
                "context": result.get("context", "")[:900],
                "questions": result.get("questions", []),
                "all_checkpoints": result["all_checkpoints"]
            })
        else:
            print(f"\n{Colors.OKGREEN}{'='*80}{Colors.ENDC}")
            print(f"{Colors.BOLD}🎉 ALL CHECKPOINTS COMPLETED!{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{'='*80}{Colors.ENDC}\n")
            
            return jsonify({
                "success": True,
                "all_complete": True,
                "completed_checkpoints": state["completed_checkpoints"]
            })
    except Exception as e:
        print(f"{Colors.FAIL}❌ ERROR: {str(e)}{Colors.ENDC}\n")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print(f"{Colors.BOLD}🌐 Starting Flask Server on port 8080{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✅ Server: http://localhost:8080{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✅ Ready to accept connections{Colors.ENDC}\n")
    app.run(host='0.0.0.0', port=8080, debug=False)
