import streamlit as st
import os
import json
import re
import time
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage

# 1. CONFIGURATION & UI SETUP
st.set_page_config(page_title="AI Tutor Pro", layout="wide")

# Enhanced Custom CSS for UI
st.markdown("""
    <style>
    /* Global Styles */
    .main .block-container {padding-top: 2rem;}
    
    /* Input Fields */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        padding: 10px;
    }
    
    /* Cards */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-value {font-size: 24px; font-weight: 800; color: #4f46e5;}
    .metric-label {font-size: 14px; color: #6b7280; font-weight: 500;}
    
    /* Study Plan Timeline */
    .step-card {
        background: linear-gradient(135deg, #f3f4f6 0%, #ffffff 100%);
        border-left: 5px solid #6366f1;
        border-radius: 8px;
        padding: 15px 20px;
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    .step-card:hover {transform: translateX(5px); border-left-color: #4338ca;}
    .step-title {font-weight: 700; color: #1f2937; font-size: 1.1rem;}
    .step-obj {color: #4b5563; font-size: 0.9rem; margin-top: 5px;}
    
    /* Success/Fail Alerts */
    .status-box {padding: 1rem; border-radius: 8px; margin-bottom: 1rem;}
    .success-mode {background-color: #dcfce7; color: #166534; border: 1px solid #bbf7d0;}
    .fail-mode {background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca;}
    
    /* Button Styling */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        height: 3rem;
        transition: all 0.3s ease;
    }
    </style>
""", unsafe_allow_html=True)

# 2. SESSION STATE
default_state = {
    "step": "setup",
    "main_topic": "",
    "study_plan": [],
    "current_checkpoint": {},
    "doc_text": "",
    "final_essay": "",
    "quiz_questions": [],
    "user_answers": [],
    "grading_results": [],
    "failed_concepts": [],
    "attempt_count": 0,
    "max_attempts": 2,
    "total_score": 0,
    "modules_completed": 0
}

for key, val in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = val

# 3. LOGIC & MODEL LOADING

def configure_langsmith(api_key):
    """Sets up LangSmith tracing if key is provided."""
    if api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "AI-Tutor-Pro"
        os.environ["LANGCHAIN_API_KEY"] = api_key
        return True
    return False

@st.cache_resource
def load_core_components(groq_key):
    if not groq_key: return None, None, None
    
    llm = ChatGroq(
        api_key=groq_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.3
    )
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    search = DuckDuckGoSearchRun()
    return llm, embeddings, search

def parse_pdf(uploaded_file):
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        os.remove(tmp_path)
        return "\n\n".join([p.page_content for p in pages])
    except Exception as e:
        st.error(f"Error parsing PDF: {e}")
        return ""

# CORE NODES
def generate_study_plan(llm, topic, doc_context):
    """
    Generates a 5-step curriculum. 
    Smart Logic: Checks if uploaded file matches the topic. 
    If irrelevant, it falls back to General Knowledge/Web logic.
    """
    
    source_instruction = ""
    
    # 1. RELEVANCE CHECK
    if doc_context and len(doc_context) > 200:
        check_prompt = f"""
        User Topic: "{topic}"
        Document Intro: "{doc_context[:1000]}..."
        
        TASK:
        Determine if this document is RELEVANT to the User Topic.
        - If the document covers the topic, return "YES".
        - If the document is about something completely different (e.g., Topic is 'Cooking' but Doc is 'Deep Learning'), return "NO".
        
        OUTPUT STRICTLY: "YES" or "NO"
        """
        try:
            relevance = llm.invoke([HumanMessage(content=check_prompt)]).content.strip().upper()
        except Exception as e:
            print(f"Relevance check failed: {e}")
            relevance = "NO"

        if "YES" in relevance:
            source_instruction = f"""
            CONTEXT_SOURCE: UPLOADED DOCUMENT
            The user's topic matches the uploaded document.
            Analyze the text below. Extract the 5 most distinct chapters or logical sections found in it.
            
            DOCUMENT TEXT:
            {doc_context[:15000]}
            """
        else:
            print(f"Document judged irrelevant for {topic}. Using General Knowledge.")
            source_instruction = f"""
            CONTEXT_SOURCE: GENERAL KNOWLEDGE (Ignore irrelevant document)
            Create a comprehensive 5-step study plan for "{topic}" from scratch using your internal knowledge.
            Ensure the steps progress logically from beginner to advanced.
            """
    else:
        source_instruction = f"""
        CONTEXT_SOURCE: GENERAL KNOWLEDGE
        Create a comprehensive 5-step study plan for "{topic}" from scratch.
        """

    # 2. GENERATE PLAN
    prompt = f"""
    You are an expert Curriculum Designer.
    
    {source_instruction}
    
    TASK:
    Generate a structured 5-part study plan.
    
    STRICT OUTPUT RULES:
    1. Return ONLY a valid JSON List.
    2. Do not add explanations, markdown, or text before/after the JSON.
    3. The keys must be exactly: "id", "topic", "objective".
    
    JSON EXAMPLE:
    [
        {{"id": 1, "topic": "Introduction", "objective": "Define core concepts..."}},
        {{"id": 2, "topic": "Key Mechanisms", "objective": "Analyze how X works..."}}
    ]
    """
    
    # 3. EXECUTE & PARSE
    try:
        res = llm.invoke([HumanMessage(content=prompt)]).content
        
        # Clean response
        cleaned_json = res.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        return json.loads(cleaned_json)

    except Exception as e:
        print(f"Plan Gen Error: {e}")
        # Failsafe
        return [{"id": i+1, "topic": f"{topic} Part {i+1}", "objective": "Core concepts"} for i in range(5)]
        
def generate_lesson_content(llm, search_tool, topic, objective, doc_text):
    """
    Generates the lesson content.
    CRITICAL CHANGE: Strictly discards doc_text if it's irrelevant to the topic.
    """
    
    # 1. SOURCE VALIDATION
    use_doc = False
    use_web = True
    
    if doc_text and len(doc_text) > 200:
        validation_prompt = f"""
        TOPIC: "{topic}"
        OBJECTIVE: "{objective}"
        DOCUMENT SNIPPET:
        {doc_text[:1000]}...
        
        TASK:
        Classify the document's utility for teaching this specific topic.
        
        OPTIONS:
        - "SUFFICIENT": The doc covers the topic well. (Use Doc Only)
        - "USEFUL_BUT_INCOMPLETE": The doc is relevant but needs web info. (Use Doc + Web)
        - "IRRELEVANT": The doc is about a completely different subject (e.g. topic is DSA, doc is Deep Learning). (Use Web Only)
        
        OUTPUT STRICTLY ONE WORD: SUFFICIENT, USEFUL_BUT_INCOMPLETE, or IRRELEVANT
        """
        try:
            status = llm.invoke([HumanMessage(content=validation_prompt)]).content.strip().upper()
        except:
            status = "USEFUL_BUT_INCOMPLETE" # Default safe mode

        print(f"Validation Status for '{topic}': {status}") # Debug print

        if "IRRELEVANT" in status:
            use_doc = False 
            use_web = True
        elif "SUFFICIENT" in status:
            use_doc = True
            use_web = False
        else:
            use_doc = True
            use_web = True
    
    # 2. GATHER CONTEXT
    context_data = ""
    
    if use_web:
        try:
            with st.spinner("Searching for strict topic info..."):
                web_results = search_tool.invoke(f"{topic} {objective} explanation tutorial")
                context_data += f"\n[WEB SOURCE]:\n{web_results}\n"
        except Exception as e:
            context_data += "\n[WEB SOURCE]: Search failed.\n"

    if use_doc:
        context_data += f"\n[USER NOTES]:\n{doc_text[:15000]}\n"

    # 3. GENERATE ESSAY
    prompt = f"""
    You are an expert Computer Science Tutor.
    
    TOPIC: {topic}
    OBJECTIVE: {objective}
    
    CONTEXT MATERIALS:
    {context_data}
    
    INSTRUCTIONS:
    1. Write a clear, 500-word educational guide strictly on "{topic}".
    2. Give a neat and professional essay.
    3. IF the Context Materials contain information about unrelated topics (like Deep Learning when the topic is DSA), IGNORE THEM COMPLETELY.
    4. Focus ONLY on meeting the OBJECTIVE.
    """
    
    try:
        return llm.invoke([HumanMessage(content=prompt)]).content
    except Exception as e:
        return f"Error generating lesson: {e}"

def generate_quiz(llm, context, topic):
    """
    Generates 5 open-ended conceptual questions (No MCQs).
    """
    prompt = f"""
    You are an expert Examiner.
    CONTEXT: {context[:5000]}
    TOPIC: {topic}
    
    TASK:
    Generate 5 thought-provoking, short-answer conceptual questions to test the user's understanding.
    
    STRICT RULES:
    1. **NO Multiple Choice Questions (MCQs).** Do not provide options.
    2. Questions should ask "How", "Why", "Explain", or "Compare".
    3. Do not include the answer in the output.
    4. Do not prefix the string with "Q1:" or "Question 1:", just provide the question text.
    
    OUTPUT FORMAT:
    Strictly a JSON List of strings.
    Example: ["Explain the difference between X and Y.", "How does mechanism Z work?"]
    """
    
    try:
        res = llm.invoke([HumanMessage(content=prompt)]).content
        
        # Clean potential Markdown wrapper
        cleaned_res = res.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        questions = json.loads(cleaned_res)
        
        # Double check it's a list
        if isinstance(questions, list):
            return questions
        else:
            return [f"Explain the core concept of {topic}."]
            
    except Exception as e:
        print(f"Quiz Gen Error: {e}")
        return [f"Explain {topic} in your own words.", f"What are the key components of {topic}?"]

def grade_answers(llm, topic, questions, answers):
    """
    Strictly grades answers. 
    Fixes the 'Empty Submission' bug by detecting blank answers 
    and forcing the AI to mark them as 0.
    """
    
    # 1. PRE-PROCESS: fill empty answers so the AI sees them clearly
    cleaned_qa_pairs = []
    for i, (q, a) in enumerate(zip(questions, answers)):
        # Check if answer is empty or just whitespace
        clean_a = a.strip() if a else ""
        if not clean_a:
            clean_a = "[STUDENT SUBMITTED NO ANSWER]"
        
        cleaned_qa_pairs.append(f"Q{i+1}: {q}\nA{i+1}: {clean_a}")
    
    qa_text = "\n".join(cleaned_qa_pairs)
    
    # 2. STRICT PROMPT
    prompt = f"""
    You are a Strict Academic Professor.
    TOPIC: {topic}
    
    Evaluate the student's answers below.
    
    GRADING RULES:
    1. **If the Answer says "[STUDENT SUBMITTED NO ANSWER]", Score = 0. FEEDBACK = "No answer provided."**
    2. **Score 0** for factually incorrect or irrelevent information.
    3. **Score 20** only for perfect, technical definitions.
    4. **Score 10-14** for partially correct answers.
    5. **Score 15-18** for correct but still requires details.
    6. **Score 5-9** for below average answers.
    
    INPUT:
    {qa_text}
    
    OUTPUT JSON ONLY:
    {{
        "reviews": [
            {{"q_index": 1, "score": 0, "feedback": "...", "concept": "..."}},
            ...
        ]
    }}
    """
    
    try:
        res = llm.invoke([HumanMessage(content=prompt)]).content
        cleaned_res = res.replace("```json", "").replace("```", "").strip()
        data = json.loads(re.search(r"\{.*\}", cleaned_res, re.DOTALL).group(0))
        return data["reviews"]
    except Exception as e:
        print(f"Grading Error: {e}")
        return []

def generate_remedial(llm, topic, failed_concepts):
    prompt = f"Act as Feynman. Explain {failed_concepts} about {topic} using simple analogies."
    return llm.invoke([HumanMessage(content=prompt)]).content

# 4. MAIN APPLICATION

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # 1. API Keys
    groq_input = st.text_input("Groq API Key", type="password", help="Required for reasoning")
    langsmith_input = st.text_input("LangSmith API Key", type="password", help="Optional: For Tracing")
    
    # Configure LangSmith immediately if key provided
    if langsmith_input:
        configure_langsmith(langsmith_input)
        st.caption("Tracing Enabled")

    st.divider()

    # 2. File Upload
    uploaded_file = st.file_uploader("Upload Notes (PDF)", type=["pdf"])
    if uploaded_file and not st.session_state.doc_text:
        with st.spinner("Processing PDF..."):
            st.session_state.doc_text = parse_pdf(uploaded_file)
            st.success("PDF Context Loaded")

    st.divider()
    
    # 3. Reset
    if st.button("🔄 Reset Tutor", use_container_width=True):
        st.session_state.clear()
        st.rerun()

if not groq_input:
    st.info("Welcome! Please enter your API Key in the sidebar to begin.")
    st.stop()

# Initialize Models
llm, embeddings, search = load_core_components(groq_input)

# Top Dashboard Metrics
if st.session_state.step != "setup":
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{st.session_state.main_topic}</div><div class="metric-label">Current Topic</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{st.session_state.modules_completed}/5</div><div class="metric-label">Modules Completed</div></div>""", unsafe_allow_html=True)
    with c3:
        avg = 0 if st.session_state.modules_completed == 0 else int(st.session_state.total_score / st.session_state.modules_completed)
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{avg}%</div><div class="metric-label">Average Score</div></div>""", unsafe_allow_html=True)
    st.markdown("---")

# VIEW: SETUP
if st.session_state.step == "setup":
    st.title("🎓 AI Tutor Pro")
    st.markdown("What do you want to master today?")
    
    col_input, col_btn = st.columns([5, 1], vertical_alignment="bottom")
    
    with col_input:
        topic_in = st.text_input(
            "Topic", 
            placeholder="e.g. Quantum Computing, Data structures...", 
            label_visibility="collapsed"
        )
    
    with col_btn:
        start_btn = st.button("Generate Plan", type="primary", use_container_width=True)

    if start_btn and topic_in:
        st.session_state.main_topic = topic_in
        with st.spinner("Architecting your learning path..."):
            plan = generate_study_plan(llm, topic_in, st.session_state.doc_text)
            st.session_state.study_plan = plan
            st.session_state.step = "plan"
            st.rerun()
# VIEW: PLAN
elif st.session_state.step == "plan":
    st.subheader(f"Learning Path: {st.session_state.main_topic}")
    
    for cp in st.session_state.study_plan:
        col_text, col_action = st.columns([5, 1])
        with col_text:
            st.markdown(f"""
            <div class="step-card">
                <div class="step-title">{cp['id']}. {cp['topic']}</div>
                <div class="step-obj">{cp['objective']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_action:
            st.write("") 
            if st.button("Start", key=f"start_{cp['id']}", use_container_width=True):
                st.session_state.current_checkpoint = cp
                st.session_state.step = "generating"
                st.rerun()

# VIEW: GENERATING CONTENT
elif st.session_state.step == "generating":
    cp = st.session_state.current_checkpoint
    with st.status(f"Launching Module {cp['id']}...", expanded=True):
        st.write("Analyzing sources...")
        essay = generate_lesson_content(llm, search, cp['topic'], cp['objective'], st.session_state.doc_text)
        st.write("Synthesizing lesson...")
        st.session_state.final_essay = essay
        st.session_state.attempt_count = 1
        st.session_state.failed_concepts = []
        time.sleep(1) # UX pause
    
    st.session_state.step = "study"
    st.rerun()

# VIEW: STUDY
elif st.session_state.step == "study":
    cp = st.session_state.current_checkpoint
    st.subheader(f"Module {cp['id']}: {cp['topic']}")
    
    tab1, tab2 = st.tabs(["Lesson", "Feynman's Notes"])
    with tab1:
        st.markdown(st.session_state.final_essay.split("=== REMEDIAL")[0])
    with tab2:
        if "=== REMEDIAL" in st.session_state.final_essay:
            st.info("Simplified explanations based on your previous attempt.")
            st.markdown(st.session_state.final_essay.split("=== REMEDIAL")[1])
        else:
            st.caption("No remedial notes currently needed.")

    st.divider()
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Take Quiz", type="primary", use_container_width=True):
            with st.spinner("Drafting questions..."):
                qs = generate_quiz(llm, st.session_state.final_essay, cp['topic'])
                st.session_state.quiz_questions = qs
                st.session_state.step = "quiz"
                st.rerun()

# VIEW: QUIZ
elif st.session_state.step == "quiz":
    st.subheader(f"Quiz: Attempt {st.session_state.attempt_count}")
    
    with st.form("quiz_form"):
        answers = []
        for i, q in enumerate(st.session_state.quiz_questions):
            st.markdown(f"**{i+1}. {q}**")
            answers.append(st.text_input(f"Your Answer", key=f"q_{i}"))
        
        submitted = st.form_submit_button("Submit Answers", type="primary", use_container_width=True)
        if submitted:
            st.session_state.user_answers = answers
            st.session_state.step = "grading"
            st.rerun()

# VIEW: GRADING
elif st.session_state.step == "grading":
    with st.spinner("Grading..."):
        results = grade_answers(llm, st.session_state.current_checkpoint['topic'], st.session_state.quiz_questions, st.session_state.user_answers)
        st.session_state.grading_results = results
        score = sum(r['score'] for r in results)
        
        # Logic
        if score >= 70:
            st.session_state.modules_completed += 1
            st.session_state.total_score += score
            st.session_state.step = "success"
        else:
            failed = [r['concept'] for r in results if r['score'] < 12]
            st.session_state.failed_concepts = list(set(failed))
            st.session_state.step = "fail"
        st.rerun()

# VIEW: RESULTS
elif st.session_state.step in ["success", "fail"]:
    results = st.session_state.grading_results
    score = sum(r['score'] for r in results)
    
    # Header
    if st.session_state.step == "success":
        st.markdown(f"""<div class="status-box success-mode"><h3>Passed! Score: {score}%</h3>Great job mastering this concept.</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="status-box fail-mode"><h3>Score: {score}%</h3>You missed a few key concepts. Let's review.</div>""", unsafe_allow_html=True)
    
    # Feedback Accordion
    with st.expander("Detailed Feedback", expanded=True):
        for res in results:
            st.markdown(f"**Q{res['q_index']} ({res['score']}/20):** {res['feedback']}")

    # Actions
    c1, c2 = st.columns(2)
    with c1:
        if st.session_state.step == "success":
            if st.button("Next Module ➡", type="primary", use_container_width=True):
                st.session_state.step = "plan"
                st.rerun()
        else:
            if st.session_state.attempt_count <= st.session_state.max_attempts:
                if st.button("Explain with Feynman & Retry", type="primary", use_container_width=True):
                    with st.spinner("Consulting Feynman..."):
                        rem = generate_remedial(llm, st.session_state.current_checkpoint['topic'], st.session_state.failed_concepts)
                        st.session_state.final_essay += f"\n\n=== REMEDIAL EXPLANATION ===\n{rem}"
                        st.session_state.attempt_count += 1
                        st.session_state.step = "study"
                        st.rerun()
            else:
                st.error("Max attempts reached. Please restart or review notes.")
                if st.button("Back to Plan", use_container_width=True):
                    st.session_state.step = "plan"
                    st.rerun()