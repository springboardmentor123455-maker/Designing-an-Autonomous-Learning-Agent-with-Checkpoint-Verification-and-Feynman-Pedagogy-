import streamlit as st
import os
import json
import re
from typing import TypedDict, Optional

# LangChain & HuggingFace Imports
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace, HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="AI Tutor (Milestone 1)", page_icon="🎓", layout="wide")
st.title("Autonomous AI Tutor (Smart RAG & Graph Logic)")

# Force Legacy Keras to prevent import errors
os.environ["TF_USE_LEGACY_KERAS"] = "1"

# --- SESSION STATE INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = "setup"
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "topic": "",
        "objective": "",
        "doc_context": "",
        "web_context": "",
        "final_essay": "", 
        "quiz_questions": [],
        "user_answers": [],
        "grading_result": None
    }

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Agent Settings")
    
    # Hugging Face Token
    hf_token = st.text_input("1. Hugging Face Token:", type="password")
    if hf_token:
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token

    # LangSmith Token (Optional)
    st.markdown("---")
    ls_token = st.text_input("2. LangSmith API Key (Optional):", type="password", help="For tracing agent thoughts")
    if ls_token:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "AI Tutor Streamlit"
        os.environ["LANGCHAIN_API_KEY"] = ls_token

    st.markdown("---")
    
    # Checkpoints Map
    CHECKPOINTS = {
        "Transformer Architecture": "Explain the Encoder-Decoder structure and Self-Attention mechanism.",
        "Backpropagation": "Detail the chain rule and how gradients update weights in a neural network.",
        "RAG Systems": "Explain Retrieval-Augmented Generation, vector databases, and semantic search.",
        "GANs": "Explain the Generator vs Discriminator dynamic and training challenges.",
        "CNNs": "Explain Filters, Pooling layers, and their application in image recognition."
    }
    
    selected_topic = st.selectbox("Select Learning Topic:", list(CHECKPOINTS.keys()))
    uploaded_file = st.file_uploader("Upload Notes (PDF - Optional)", type=["pdf"])
    
    if st.button("🔄 Reset Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- 3. BACKEND NODES ---

@st.cache_resource
def load_models():
    if not os.environ.get("HUGGINGFACEHUB_API_TOKEN"):
        return None, None, None
    
    # Increased Token Limit for Long Essays
    llm_engine = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-72B-Instruct", 
        task="text-generation",
        max_new_tokens=2048, 
        do_sample=True,
        temperature=0.3,
    )
    llm = ChatHuggingFace(llm=llm_engine)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    web_search = DuckDuckGoSearchRun()
    return llm, embeddings, web_search

# --- NODE 1: SMART DOCUMENT CHECK ---
def check_user_doc(llm, embeddings, uploaded_file, topic):
    if not uploaded_file:
        return "", True, "No file uploaded. Proceeding to Web Search."

    try:
        temp_path = f"./temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        loader = PyPDFLoader(temp_path)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = splitter.split_documents(docs)
        
        if not splits:
            return "", True, "PDF empty or unreadable."

        vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        retrieved_docs = retriever.invoke(topic)
        context_text = "\n\n".join([d.page_content for d in retrieved_docs])
        
        # LLM Relevance Grader
        grader_prompt = f"""
        You are a Relevance Grader.
        Topic: {topic}
        Retrieved Text: {context_text[:2000]}
        
        Does the retrieved text contain a DETAILED explanation of the Topic?
        If it only contains headers, unrelated topics, or placeholders, answer NO.
        Answer only YES or NO.
        """
        response = llm.invoke([HumanMessage(content=grader_prompt)])
        grade = response.content.strip().upper()
        
        if "NO" in grade or len(context_text) < 200:
            return context_text, True, f"PDF content found ({len(context_text)} chars) but graded IRRELEVANT. Enabling Web Search."
            
        return context_text, False, f"Relevant PDF content found ({len(context_text)} chars)."

    except Exception as e:
        return "", True, f"Error reading PDF: {e}"

# --- NODE 2: WEB SEARCH ---
def perform_web_search(search_tool, topic, objective, needs_search):
    if not needs_search:
        return "", "Web search skipped (PDF sufficient)."
    
    try:
        query = f"{topic} {objective} detailed technical explanation structure mechanism"
        results = search_tool.invoke(query)
        return results, "Web search completed."
    except Exception as e:
        return "", f"Web search failed: {e}"

# --- NODE 3: GENERATION (Strict No-Math / Pure Concept) ---
def generate_essay(llm, topic, objective, doc_context, web_context):
    """
    Generates 750-1000 word essay.
    STRICT RULE: NO EQUATIONS. Purely conceptual.
    """
    system_instruction = """You are an expert AI Professor who explains complex technical concepts using ONLY plain English.
    
    YOUR TASK: Write a comprehensive 750-1000 word Technical Guide.
    
    CRITICAL RULE: NO MATHEMATICAL NOTATION ALLOWED.
    1. STRICTLY FORBIDDEN: LaTeX, symbols (∑, ∂, α, σ), standalone variables (x, y, w, b), or formulas.
    2. REQUIRED FORMAT: You must describe mathematical relationships using ONLY descriptive sentences.
    
    --- EXAMPLES OF HOW TO WRITE ---
    BAD: "y = wx + b"
    GOOD: "The neuron calculates its output by multiplying the input signal by a specific weight, adding a bias value, and then passing the result through an activation function."
    
    BAD: "L = (y - ŷ)²"
    GOOD: "The error is calculated by taking the difference between the predicted value and the actual target, and then squaring that difference to ensure the result is always positive."
    ---------------------------------
    
    ADDITIONAL INSTRUCTIONS:
    - Length: 750 - 1000 words.
    - Structure: Use clear Sections, Headers, and Bullet Points.
    - Tone: Professional, academic, yet accessible.
    - Citations: DO NOT use citations.
    """
    
    user_content = f"""
    TOPIC: {topic}
    OBJECTIVE: {objective}
    
    SOURCE MATERIAL:
    {doc_context[:4000]} 
    {web_context[:4000]}
    
    Write the detailed guide now. Remember: Narrative explanation only, absolutely no formulas.
    """
    
    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=user_content)
    ]
    
    try:
        response_msg = llm.invoke(messages)
        return response_msg.content
    except Exception as e:
        return f"Error generating essay: {str(e)}"

# --- NODE 4: QUESTION GENERATOR (Conceptual Only) ---
def generate_questions(llm, topic, lesson_text):
    """
    Generates 5 questions.
    STRICT RULE: Conceptual questions only. No math/formula questions.
    """
    prompt = f"""
    You are an Examiner. The student has just read a lesson on "{topic}".
    
    Generate exactly 5 conceptual questions based ONLY on the LESSON TEXT below.
    
    RULES:
    1. QUESTIONS MUST BE PURELY THEORETICAL. 
       - Ask "Why", "How", "What is the purpose", "Explain the difference".
       - DO NOT ask to calculate anything.
       - DO NOT ask for formulas or equations.
    2. Do NOT include answers.
    3. Return ONLY the 5 questions as a numbered list (1., 2., 3., 4., 5.).
    
    LESSON TEXT:
    {lesson_text[:5000]}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    questions = []
    for line in response.content.split("\n"):
        line = line.strip()
        if line and (line[0].isdigit() or "?" in line):
            clean_q = re.sub(r'^\d+\.\s*', '', line)
            questions.append(clean_q)
    
    if len(questions) < 5:
        return questions + [f"Explain the core concept of {topic}."] * (5 - len(questions))
        
    return questions[:5]

# --- NODE 5: GRADER (Strict & Rigorous) ---
def grade_answers(llm, topic, lesson_text, questions, answers):
    """
    Grades answers with high rigor. Penalizes generic answers heavily.
    """
    qa_pairs = ""
    for i in range(len(questions)):
        # Handle skipped answers safely
        ans = answers[i] if i < len(answers) else "No Answer"
        qa_pairs += f"Q{i+1}: {questions[i]}\nStudent Answer: {ans}\n\n"
        
    prompt = f"""
    You are a STRICT Academic Examiner. 
    The student is taking a high-level technical exam on "{topic}".
    
    REFERENCE MATERIAL (THE TRUTH):
    {lesson_text[:5000]}
    
    STUDENT SUBMISSION:
    {qa_pairs}
    
    --- STRICT GRADING RUBRIC ---
    1. ZERO TOLERANCE FOR FLUFF: If the answer is generic, vague, or could apply to any topic (e.g., "It is very important"), award 0 marks immediately.
    2. KEYWORD REQUIREMENT: The student MUST use specific technical terminology found in the Reference Material. If key terms are missing, deduct 25% of the marks.
    3. ACCURACY: If the answer is factually incorrect or hallucinates details not in the text, award 0.
    4. COMPLETENESS: If the question asks "How and Why" and the student only answers "How", cap the score at 13/20.
    5. if the answer requires information more than what the generated content provides, give more weight to the part that is covered by the generated content.
    
    TASK:
    1. Grade EACH answer out of 20 marks. (Total 100).
    2. Be critical. Do not give "participation points".
    3. Provide a specific, corrective reason for the score.
    
    RETURN JSON FORMAT ONLY:
    {{
        "detailed_reviews": [
            {{
                "question": "text",
                "marks_awarded": <int>,
                "reason": "explanation"
            }},
            ...
        ]
    }}
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # Parse JSON
        json_match = re.search(r"\{.*\}", response.content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            total = sum([item['marks_awarded'] for item in data['detailed_reviews']])
            data['total_score'] = total
            
            # Strict Feedback Logic
            if total >= 80:
                data['feedback'] = "Distinction! Excellent mastery of concepts."
            elif total >= 50:
                data['feedback'] = "Passed, but lacks technical depth."
            else:
                data['feedback'] = "Failed. Answers were too vague or incorrect."
                
            return data
        else:
            return {"total_score": 0, "detailed_reviews": [], "feedback": "Error parsing grader response."}
            
    except Exception as e:
        return {"total_score": 0, "detailed_reviews": [], "feedback": f"Grading Error: {str(e)}"}

# --- 4. MAIN APP LOGIC ---

if "HUGGINGFACEHUB_API_TOKEN" in os.environ:
    llm, embeddings, web_search = load_models()
else:
    st.warning("Please enter your Hugging Face API Token in the sidebar.")
    st.stop()

# --- STEP 1: SETUP ---
if st.session_state.step == "setup":
    st.info(f"Welcome! Topic: **{selected_topic}**")
    
    if st.button("Generate Study Material"):
        with st.spinner("Running Workflow: Check PDF → Web Search → Synthesis..."):
            
            # 1. Check Doc
            doc_ctx, needs_search, log1 = check_user_doc(llm, embeddings, uploaded_file, selected_topic)
            
            # 2. Web Search
            objective = CHECKPOINTS[selected_topic]
            web_ctx, log2 = perform_web_search(web_search, selected_topic, objective, needs_search)
            
            # 3. Generate Lesson
            lesson = generate_essay(llm, selected_topic, objective, doc_ctx, web_ctx)
            
            # Update State
            st.session_state.agent_state["doc_context"] = doc_ctx
            st.session_state.agent_state["web_context"] = web_ctx
            st.session_state.agent_state["topic"] = selected_topic
            st.session_state.agent_state["final_essay"] = lesson
            st.session_state.logs = f"{log1}\n{log2}"
            st.session_state.step = "reading"
            st.rerun()

# --- STEP 2: READING ---
elif st.session_state.step == "reading":
    st.subheader(f"Study Guide: {st.session_state.agent_state['topic']}")
    with st.expander("System Logs"):
        st.text(st.session_state.logs)
        
    st.markdown(st.session_state.agent_state["final_essay"])
    st.divider()
    
    if st.button("I'm Ready - Take Quiz"):
        with st.spinner("Generating Questions based on this specific guide..."):
            qs = generate_questions(
                llm, 
                st.session_state.agent_state["topic"],
                st.session_state.agent_state["final_essay"]
            )
            st.session_state.agent_state["quiz_questions"] = qs
            st.session_state.step = "quiz_loop"
            st.rerun()

# --- STEP 3: QUIZ LOOP ---
elif st.session_state.step == "quiz_loop":
    st.subheader("Final Exam")
    questions = st.session_state.agent_state["quiz_questions"]
    
    with st.form("quiz_form"):
        answers = []
        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}: {q}**")
            ans = st.text_area(f"Answer for Q{i+1}:", key=f"a_{i}", height=100)
            answers.append(ans)
            st.markdown("---")
        
        submitted = st.form_submit_button("Submit All Answers")
        
        if submitted:
            if all(a.strip() for a in answers):
                st.session_state.agent_state["user_answers"] = answers
                st.session_state.step = "grading"
                st.rerun()
            else:
                st.warning("Please answer all questions before submitting.")

# --- STEP 4: GRADING ---
elif st.session_state.step == "grading":
    with st.spinner("Grading against the generated lesson..."):
        result = grade_answers(
            llm,
            st.session_state.agent_state["topic"],
            st.session_state.agent_state["final_essay"],
            st.session_state.agent_state["quiz_questions"],
            st.session_state.agent_state["user_answers"]
        )
        st.session_state.agent_state["grading_result"] = result
        st.session_state.step = "results"
        st.rerun()

# --- STEP 5: RESULTS ---
elif st.session_state.step == "results":
    data = st.session_state.agent_state["grading_result"]
    score = data.get("total_score", 0)
    
    if score >= 80:
        st.balloons()
        st.success(f"PASSED! Score: {score}/100")
    else:
        st.error(f"FAILED. Score: {score}/100")
        
    st.divider()
    for i, review in enumerate(data.get("detailed_reviews", [])):
        marks = review.get('marks_awarded', 0)
        color = "green" if marks == 20 else "orange" if marks >= 10 else "red"
        
        with st.expander(f"Q{i+1}: {review.get('question')} — **:{color}[{marks}/20]**"):
            st.markdown(f"**Your Answer:** {st.session_state.agent_state['user_answers'][i]}")
            st.markdown(f"**Reason:** {review.get('reason')}")
            
    if st.button("🔄 Start New Topic"):
        st.session_state.step = "setup"
        st.rerun()