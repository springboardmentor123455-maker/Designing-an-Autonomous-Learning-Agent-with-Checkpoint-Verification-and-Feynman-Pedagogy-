import streamlit as st
import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Dict
import re

# Load environment
load_dotenv()

from langsmith import traceable

# Langsmith Tracing
langsmith_api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY", "")
if langsmith_api_key:
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = langsmith_api_key
    os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT") or os.getenv("LANGCHAIN_PROJECT", "AI-Study-System")

from huggingface_hub import InferenceClient
from langchain_huggingface import HuggingFaceEmbeddings
from tavily import TavilyClient
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Secrets helper: read from Streamlit secrets and environment fallbacks
def get_secret_value(name: str, alt_names=None, default: str = "") -> str:
    alt_names = alt_names or []
    
    # 1) Try Environment variables First
    val = os.getenv(name)
    if val:
        return val
    for alt in alt_names:
        val = os.getenv(alt)
        if val:
            return val
    
    # 2) Try Streamlit Secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets") and len(st.secrets) > 0:
            if name in st.secrets:
                return str(st.secrets[name])
            for alt in alt_names:
                if alt in st.secrets:
                    return str(st.secrets[alt])
    except (FileNotFoundError, AttributeError, KeyError):
        pass
    except Exception:
        pass
    
    return default

# Page config
st.set_page_config(page_title="AI-Powered Study System", layout="wide")

# MILESTONE 1: CHECKPOINT STRUCTURE & CONTEXT GATHERING
@dataclass
class Checkpoint:
    id: str
    topic: str
    objectives: List[str]
    pass_mark: float = 0.7  # MILESTONE 2: 70% threshold as per requirements

# MILESTONE 1: Define structured learning checkpoints with specific objectives
CHECKPOINTS: List[Checkpoint] = [
    Checkpoint(
        id="cp1",
        topic="Artificial Intelligence",
        objectives=[
            "What is Artificial Intelligence and how is it different from normal programs?",
            "Give examples of AI in everyday life",
            "Explain the difference between AI, ML, and Deep Learning"
        ]
    ),
    Checkpoint(
        id="cp2",
        topic="Machine Learning",
        objectives=[
            "What is Machine Learning and how does it work?",
            "Explain supervised and unsupervised learning with examples",
            "What are training data and testing data?"
        ]
    ),
    Checkpoint(
        id="cp3",
        topic="Generative AI",
        objectives=[
            "What is Generative AI and what can it create?",
            "Give examples of GenAI tools like ChatGPT, DALL-E, etc.",
            "How is GenAI different from traditional AI?"
        ]
    ),
    Checkpoint(
        id="cp4",
        topic="Large Language Models",
        objectives=[
            "What are Large Language Models?",
            "How do LLMs understand and generate text?",
            "Give examples of popular LLMs and their uses"
        ]
    ),
    Checkpoint(
        id="cp5",
        topic="Prompt Engineering",
        objectives=[
            "What is prompt engineering and why is it important?",
            "How to write effective prompts for AI models?",
            "Give examples of good and bad prompts"
        ]
    ),
    Checkpoint(
        id="cp6",
        topic="AI Ethics and Safety",
        objectives=[
            "What are the ethical concerns with AI?",
            "Explain AI bias and fairness",
            "How can we use AI responsibly?"
        ]
    )
]

# MILESTONE 1: User-provided notes
USER_NOTES: Dict[str, str] = {
    "cp1": """
Artificial Intelligence (AI) is when computers can do tasks that normally need
human intelligence, like understanding language, recognizing images, or making
decisions. Unlike normal programs that follow fixed rules, AI learns from data
and improves over time. Examples in daily life: Google search suggestions,
Netflix recommendations, face unlock on phones, and spam email filters. AI is
the big umbrella, Machine Learning (ML) is a type of AI that learns from data,
and Deep Learning is a special ML technique using neural networks with many layers.
    """,
    "cp3": """
Generative AI (GenAI) is AI that can create new content like text, images,
music, or videos. Popular tools include ChatGPT for text, DALL-E for images,
and Midjourney for art. Traditional AI mainly analyzes or classifies existing
data (like detecting spam), but GenAI creates something completely new. It learns
patterns from millions of examples and then generates original content based on
what it learned. GenAI is becoming very popular because it can help write emails,
create artwork, code programs, and many creative tasks.
    """,
    "cp4": """
Large Language Models (LLMs) are AI systems trained on huge amounts of text
from the internet to understand and generate human language. Examples include
ChatGPT, Google Bard, and Claude. They work by predicting what word should come
next based on patterns learned from training data. LLMs can answer questions,
write essays, translate languages, write code, and have conversations. They use
billions of parameters (settings) to understand context and meaning. The more
data and parameters they have, the better they perform at language tasks.
    """
}

# MILESTONE 4: STATE MANAGEMENT FOR SEAMLESS MULTI-CHECKPOINT PROGRESSION

if 'current_checkpoint' not in st.session_state:
    st.session_state.current_checkpoint = None
    st.session_state.study_material = None
    st.session_state.search_index = None
    st.session_state.questions = []
    st.session_state.answers = {}
    st.session_state.quiz_submitted = False
    st.session_state.score = 0
    st.session_state.weak_areas = []
    st.session_state.completed_checkpoints = []  # MILESTONE 4: Track completed checkpoints
    st.session_state.show_hint = {}
    st.session_state.hints_cache = {}
    st.session_state.stage = "select"  # select, study, quiz, results, feynman

    # MILESTONE 3: Feynman Teaching Module state
    st.session_state.feynman_explanations = {}
    st.session_state.incorrect_answers = {}
    st.session_state.retry_count = {}
    st.session_state.max_retries = 3

# LLM INTEGRATION: Core Large Language Model for reasoning and generation
@st.cache_resource
def load_llm():
    """Load Hugging Face Inference API client."""
    try:
        api_key = get_secret_value("HF_API_KEY")
        if not api_key:
            raise ValueError("HF_API_KEY is not set in secrets")
  
        model_name = os.getenv("MODEL_NAME", "meta-llama/Llama-3.2-3B-Instruct")
        client = InferenceClient(token=api_key)
        
        return client, model_name
    except Exception as e:
        st.error(f"Error loading Hugging Face client: {e}")
        return None, None

@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

@st.cache_resource
def load_web_searcher():
    api_key = get_secret_value("TAVILY_API_KEY", default="")
    if not api_key:
        raise ValueError("TAVILY_API_KEY is not set")
    return TavilyClient(api_key=api_key)

@st.cache_resource
def load_text_splitter():
    return RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

# Helper functions
@traceable(name="invoke_llm", run_type="llm")
def invoke_llm(message, max_tokens=1000, system_prompt=None):
    result = load_llm()
    
    if result is None or result[0] is None:
        return "Error: Hugging Face client not loaded. Please check HF_API_KEY in secrets."
    
    client, model_name = result
    
    # Use chat completion for conversational models
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": message})
    
    try:
        response = client.chat_completion(
            messages=messages,
            model=model_name,
            max_tokens=min(max_tokens, 500),
            temperature=0.7
        )
        
        # Extract the assistant's response
        if hasattr(response, 'choices') and len(response.choices) > 0:
            generated = response.choices[0].message.content.strip()
        else:
            generated = str(response).strip()
            
        return generated if generated else "I apologize, but I couldn't generate a response. Please try again."
    except Exception as e:
        error_msg = str(e)
        # Provide more helpful error message
        if "404" in error_msg or "not found" in error_msg.lower():
            return "The AI model is currently unavailable. Please try again later."
        elif "503" in error_msg or "loading" in error_msg.lower():
            return "The AI model is loading. Please wait a moment and try again."
        else:
            return f"Error: {error_msg[:200]}"

def sanitize_hint(text: str) -> str:
    """Clean model output to a concise, single hint without role tags or extra Q&A."""
    if not text:
        return ""
    # Remove bracketed role markers like [STU], [/ASS], [USER], [STUDENT], [HINT], etc.
    text = re.sub(r"\[/?(STU|ASS|SYS|INST|USER|ASSISTANT|STUDENT|TEACHER|HINT|ANSWER|QUESTION)\]", "", text, flags=re.IGNORECASE)
    # Remove lines that are questions or dialogue labels
    lines = []
    for line in text.splitlines():
        line = line.strip()
        # Skip dialogue labels
        if re.match(r"^\s*(Q:|A:|Student:|Assistant:|User:|System:|Hint:|Answer:)\s*", line, flags=re.IGNORECASE):
            continue
        # Skip lines that are just questions (likely echo of the original question)
        if line.endswith('?') and len(line) > 30:
            continue
        if line:
            lines.append(line)
    text = "\n".join(lines).strip()
    # Collapse excessive whitespace
    text = re.sub(r"\n{2,}", "\n", text).strip()
    # Keep only the first 2-3 sentences
    sentences = re.split(r"(?<=[\.\!?])\s+", text)
    if len(sentences) > 3:
        text = " ".join(sentences[:3]).strip()
    # Ensure it's a single concise paragraph
    return text

@traceable(name="get_study_material", run_type="retriever")
def get_study_material(checkpoint_obj):
    # MILESTONE 1: Prioritize user-provided notes first
    if checkpoint_obj.id in USER_NOTES and USER_NOTES[checkpoint_obj.id].strip():
        return USER_NOTES[checkpoint_obj.id], "Using saved notes"
    
    # MILESTONE 1: Fallback to web search for dynamic content retrieval
    search_string = f"{checkpoint_obj.topic}: " + "; ".join(checkpoint_obj.objectives)
    
    try:
        tavily_client = load_web_searcher()
        # Use advanced search depth for more comprehensive content
        web_results = tavily_client.search(
            search_string, 
            max_results=3,
            search_depth="advanced",
            include_answer=True,
        )
    except Exception as e:
        return f"Topic: {checkpoint_obj.topic}\n\nLearning objectives:\n" + "\n".join([f"- {obj}" for obj in checkpoint_obj.objectives]), f"Error: {str(e)}"
    
    all_content = []
    
    # Include AI-generated answer summary if available
    if isinstance(web_results, dict) and web_results.get("answer"):
        all_content.append(f"**Summary:** {web_results['answer']}")
    
    # Tavily returns a dict with a "results" list
    results_list = web_results.get("results", web_results) if isinstance(web_results, dict) else web_results

    if isinstance(results_list, list):
        for result in results_list:
            if isinstance(result, dict):
                # Prefer raw_content (full page) > content (snippet)
                text_content = result.get("raw_content") or result.get("content") or result.get("snippet") or ""
                title = result.get("title", "")
                url = result.get("url", "")
                
                if text_content and len(text_content.strip()) > 0:
                    # Format with title and source for better readability
                    if title:
                        formatted = f"**{title}**\n\n{text_content}"
                    else:
                        formatted = text_content
                    if url:
                        formatted += f"\n\n_Source: {url}_"
                    all_content.append(formatted)
            elif isinstance(result, str):
                if result.strip():
                    all_content.append(result)
            else:
                text_content = str(result)
                if text_content.strip():
                    all_content.append(text_content)
    elif isinstance(results_list, dict):
        text_content = results_list.get("raw_content") or results_list.get("content", str(results_list))
        if text_content:
            all_content.append(text_content)
    else:
        all_content.append(str(results_list))
    
    if all_content:
        return "\n\n---\n\n".join(all_content), f"Retrieved {len(all_content) - (1 if web_results.get('answer') else 0)} web results"
    else:
        return f"Topic: {checkpoint_obj.topic}\n\nLearning objectives:\n" + "\n".join([f"- {obj}" for obj in checkpoint_obj.objectives]), "No web results; using objectives"

# MILESTONE 2: CONTEXT PROCESSING (Chunking, Embedding, Vector Store)
def make_search_index(material_text):
    embeddings = load_embeddings()  # Load embedding model
    text_splitter = load_text_splitter()  # Chunk size 800, overlap 150
    one_doc = [Document(page_content=material_text)]
    small_pieces = text_splitter.split_documents(one_doc)  # Text chunking
    search_index = FAISS.from_documents(small_pieces, embeddings)  # Vector store
    return search_index

# MILESTONE 2: QUESTION GENERATION
@traceable(name="generate_questions", run_type="chain")
def generate_questions(checkpoint_obj, material, num_questions=6):
    # Generate targeted questions based on checkpoint objectives
    message = f"Generate {num_questions} numbered questions about: {checkpoint_obj.topic}\n\nQuestions:"
    
    reply = invoke_llm(message, max_tokens=300)
    
    questions = []
    lines = reply.split("\n")
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 10:
            continue
        
        if line[0].isdigit() and ('.' in line[:4] or ')' in line[:4]):
            for sep in ['. ', ') ', ': ']:
                if sep in line[:5]:
                    question = line.split(sep, 1)[1].strip()
                    break
            else:
                question = line
            
            # Strip point annotations like "(2 points)" or "(5 pts)"
            question = re.sub(r'\s*\(\d+\s*(?:points?|pts?)\)\s*$', '', question, flags=re.IGNORECASE).strip()
            
            if not question.endswith('?'):
                question += '?'
            
            if len(question) > 15 and question not in questions:
                questions.append(question)
                if len(questions) >= num_questions:
                    break
    
    if len(questions) < 1:
        questions = [obj if obj.endswith('?') else obj + '?' 
                    for obj in checkpoint_obj.objectives[:num_questions]]
    
    return questions[:num_questions]

@traceable(name="get_rag_hint", run_type="chain")
def get_rag_hint(search_index, question, topic):
    if search_index is None:
        return "Hint not available (no study material indexed)"
    
    try:
        relevant_docs = search_index.similarity_search(question, k=2)
        context = "\n".join([doc.page_content for doc in relevant_docs])
    except Exception:
        return "Unable to retrieve hint"
    
    if not context:
        return f"Unable to retrieve relevant information for: {question}"

    system_prompt = (
        "You are a helpful tutor who provides clear, direct explanations. "
        "Give a brief explanatory ANSWER (2-3 sentences) that helps the student understand the concept. "
        "Do NOT ask questions. Do NOT echo the question back. Do NOT use role tags like [STUDENT] or [HINT]. "
        "Just provide a helpful explanation based on the context."
    )

    user_prompt = (
        f"Context:\n{context[:1000]}\n\n"
        f"Student's question: {question}\n\n"
        "Provide a helpful 2-3 sentence explanation that answers this question. Do not ask any questions in your response."
    )

    answer = invoke_llm(user_prompt, max_tokens=180, system_prompt=system_prompt)
    clean = sanitize_hint(answer)
    return clean if clean else "Unable to generate hint"

# MILESTONE 3: FEYNMAN TEACHING MODULE
@traceable(name="generate_feynman_explanation", run_type="chain")
def generate_feynman_explanation(question, incorrect_answer, search_index):
    """Generate simplified Feynman-style explanation with analogies for incorrect answers."""
    
    # Get relevant context from study material
    context = ""
    if search_index:
        try:
            relevant_docs = search_index.similarity_search(question, k=2)
            context = "\n".join([doc.page_content for doc in relevant_docs])[:500]
        except:
            context = "General neural network concepts"
    
    # Feynman-style prompt: Simple terms + Analogies + Avoid jargon
    feynman_prompt = f"""Explain this concept in the simplest way possible, like teaching a 10-year-old:

Question: {question}

Their confused answer: {incorrect_answer}

Context: {context}

Rules:
1. Use simple everyday analogies (like comparing to cooking, building blocks, etc.)
2. Avoid technical jargon - if you must use it, explain it immediately
3. Use concrete examples
4. Keep it short (2-3 sentences)

Simple explanation:"""
    
    explanation = invoke_llm(feynman_prompt, max_tokens=1000)
    return explanation if explanation else "Let me explain this more simply: " + context[:200]

# MILESTONE 2 & 3: UNDERSTANDING VERIFICATION & KNOWLEDGE GAP IDENTIFICATION
@traceable(name="grade_answers", run_type="chain")
def grade_answers(checkpoint_obj, material, questions, answers):
    all_marks = []
    weak_areas = []
    incorrect_qa = {}  
    for idx, (question, answer) in enumerate(zip(questions, answers)):
        if not answer or len(answer.strip()) < 3:
            all_marks.append(0.0)
            weak_areas.append(question[:100])
            incorrect_qa[idx] = {"question": question, "answer": answer, "score": 0.0}
            continue
        
        # Keyword grading
        answer_lower = answer.lower()
        question_lower = question.lower()
        
        score = 0.0
        word_count = len(answer.split())
        if word_count >= 10:
            score += 0.3
        elif word_count >= 5:
            score += 0.2
        elif word_count >= 3:
            score += 0.1
        
        # Topic-specific keywords
        key_terms = []
        if "artificial intelligence" in question_lower or "ai" in question_lower:
            key_terms = ["intelligence", "human", "learn", "data", "computer", "program"]
        elif "machine learning" in question_lower or "ml" in question_lower:
            key_terms = ["learn", "data", "training", "supervised", "unsupervised", "model"]
        elif "generative" in question_lower or "genai" in question_lower:
            key_terms = ["generate", "create", "content", "text", "image", "chatgpt"]
        elif "llm" in question_lower or "language model" in question_lower:
            key_terms = ["language", "text", "predict", "understand", "chatgpt", "parameters"]
        elif "prompt" in question_lower:
            key_terms = ["prompt", "instruction", "clear", "specific", "context", "example"]
        elif "ethics" in question_lower or "bias" in question_lower:
            key_terms = ["bias", "fair", "ethical", "responsible", "safety", "privacy"]
        else:
            key_terms = ["ai", "machine", "learn", "data", "model", "intelligent"]
        
        terms_found = sum(1 for term in key_terms if term in answer_lower)
        term_score = min(0.5, terms_found * 0.15)
        score += term_score
        
        if any(word in answer_lower for word in ["process", "compute", "calculate"]):
            score += 0.1
        
        if any(word in answer_lower for word in ["multiply", "add", "apply", "function"]):
            score += 0.1
        
        score = max(0.0, min(1.0, score))
        all_marks.append(score)
        
        # MILESTONE 2: Apply 70% threshold for understanding verification
        # MILESTONE 3: Track incorrect answers (< 70%) for Feynman teaching
        if score < 0.7:
            weak_areas.append(question[:100])
            incorrect_qa[idx] = {"question": question, "answer": answer, "score": score}
    
    avg_score = sum(all_marks) / len(all_marks) if all_marks else 0.0
    return avg_score, weak_areas, incorrect_qa

# UI Components
def render_header():
    st.title("AI-Powered Study System")
    st.markdown("---")

# MILESTONE 4: CHECKPOINT SELECTION & SEQUENTIAL PROGRESSION
def render_checkpoint_selection():
    st.header("Select a Checkpoint")
    
    # MILESTONE 4: Filter out completed checkpoints for sequential progression
    available = [cp for cp in CHECKPOINTS if cp.id not in st.session_state.completed_checkpoints]
    
    if not available:
        st.success("Congratulations! You've completed all checkpoints!")
        if st.button("Start Over"):
            st.session_state.completed_checkpoints = []
            st.rerun()
        return
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        for cp in available:
            if st.button(f"{cp.topic}", key=f"select_{cp.id}", use_container_width=True):
                st.session_state.current_checkpoint = cp
                st.session_state.stage = "loading"
                # Reset checkpoint-specific state
                st.session_state.study_material = None
                st.session_state.search_index = None
                st.session_state.questions = []
                st.session_state.answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.show_hint = {}
                st.session_state.hints_cache = {}
                st.rerun()
    
    with col2:
        st.metric("Completed", f"{len(st.session_state.completed_checkpoints)}/{len(CHECKPOINTS)}")

# MILESTONE 1 & 2: STUDY MATERIAL DISPLAY & CONTEXT PROCESSING
def render_study_material():
    # Only render study material if explicitly in study stage, not quiz
    if st.session_state.stage != "study":
        return
    
    cp = st.session_state.current_checkpoint
    st.header(f"Study Material: {cp.topic}")
    
    if st.session_state.study_material is None:
        with st.spinner("Fetching study material..."):
            material, source = get_study_material(cp)  # MILESTONE 1: Context gathering
            st.session_state.study_material = material
            st.info(f"{source}")
            
            # MILESTONE 2: Process context (chunk, embed, store in vector DB)
            st.session_state.search_index = make_search_index(material)
    
    with st.expander("View Study Material", expanded=True):
        st.markdown(st.session_state.study_material)
    
    st.markdown("---")

    # Only show start button when explicitly in study stage
    if st.session_state.stage == "study" and not st.session_state.questions:
        if st.button("Start Quiz", key=f"start_quiz_btn_{cp.id}", type="primary", use_container_width=True):
            st.session_state.stage = "quiz"  # Change stage FIRST
            st.session_state.questions = ["Generating..."]  # Mark as generating
            st.rerun()

# MILESTONE 2: QUIZ ASSESSMENT
def render_quiz():
    cp = st.session_state.current_checkpoint
    
    # Ensure study material and search index exist
    if st.session_state.study_material is None or st.session_state.search_index is None:
        with st.spinner("Fetching study material..."):
            material, source = get_study_material(cp)
            st.session_state.study_material = material
            st.session_state.search_index = make_search_index(material)
    
    # Generate questions if marked as generating
    if st.session_state.questions == ["Generating..."]:
        with st.spinner("Generating quiz questions..."):
            st.session_state.questions = generate_questions(cp, st.session_state.study_material)
            st.session_state.answers = {}
            st.session_state.show_hint = {}
            st.session_state.hints_cache = {}
        st.rerun()
    
    st.header(f"Quiz: {cp.topic}")
    st.info(f"Pass mark: {int(cp.pass_mark * 100)}%")  # MILESTONE 2: Display threshold
    
    for idx, question in enumerate(st.session_state.questions):
        st.markdown(f"**Question {idx + 1}/{len(st.session_state.questions)}**")
        st.write(question)
        
        answer = st.text_area(
            "Your Answer:",
            key=f"answer_{idx}",
            value=st.session_state.answers.get(idx, ""),
            height=100
        )
        st.session_state.answers[idx] = answer
        
        # Hint button
        if st.button("Get Hint", key=f"hint_btn_{idx}"):
            st.session_state.show_hint[idx] = True
            st.rerun()
        
        # Display hint if requested
        if st.session_state.show_hint.get(idx, False):
            with st.expander("Hint", expanded=True):
                # Check if hint is already cached
                if idx not in st.session_state.hints_cache:
                    with st.spinner("Generating hint..."):
                        hint = get_rag_hint(st.session_state.search_index, question, cp.topic)
                        st.session_state.hints_cache[idx] = hint
                else:
                    hint = st.session_state.hints_cache[idx]
                
                st.info(hint)
        
        st.markdown("---")
    
    if st.button("Submit Quiz", type="primary", use_container_width=True):
        # Check all answers provided and not empty
        unanswered = []
        for i in range(len(st.session_state.questions)):
            answer = st.session_state.answers.get(i, "").strip()
            if not answer:
                unanswered.append(i + 1)
        
        if unanswered:
            st.error(f"Please answer all questions before submitting! Missing answers for question(s): {', '.join(map(str, unanswered))}")
        else:
            answers_list = [st.session_state.answers.get(i, "") for i in range(len(st.session_state.questions))]
            score, weak, incorrect_qa = grade_answers(
                cp,
                st.session_state.study_material,
                st.session_state.questions,
                answers_list
            )
            st.session_state.score = score
            st.session_state.weak_areas = weak
            st.session_state.incorrect_answers = incorrect_qa
            st.session_state.quiz_submitted = True
            
            # MILESTONE 2: Evaluate score against 70% threshold
            # MILESTONE 3: Trigger Feynman teaching if score < 70%
            current_retry = st.session_state.retry_count.get(cp.id, 0)
            if score < 0.7 and current_retry < st.session_state.max_retries:
                st.session_state.stage = "feynman"  # MILESTONE 3: Route to Feynman node
            else:
                st.session_state.stage = "results"  # MILESTONE 2: Proceed if passed
            st.rerun()

# MILESTONE 3: FEYNMAN TEACHING MODULE
def render_feynman_teaching():
    """Render Feynman-style simplified explanations for incorrect answers."""
    cp = st.session_state.current_checkpoint
    current_retry = st.session_state.retry_count.get(cp.id, 0)
    st.header("Let's Learn Together - Simplified Explanations")
    
    score_pct = st.session_state.score * 100
    st.info(f"Your score: {score_pct:.1f}% - Let me explain the tricky parts in simpler terms!")
    
    st.markdown("---")
    
    # Generate and display Feynman explanations for each incorrect answer
    if st.session_state.incorrect_answers:
        st.markdown("### Understanding Your Mistakes")
        
        for idx, qa_data in st.session_state.incorrect_answers.items():
            question = qa_data["question"]
            user_answer = qa_data["answer"]
            
            with st.expander(f"Question {idx + 1}: {question[:80]}...", expanded=True):
                st.markdown(f"**Your answer:** {user_answer}")
                st.markdown(f"**Score:** {qa_data['score']*100:.0f}%")
                
                # Generate Feynman explanation if not cached
                if idx not in st.session_state.feynman_explanations:
                    with st.spinner("Creating a simple explanation..."):
                        explanation = generate_feynman_explanation(
                            question,
                            user_answer,
                            st.session_state.search_index
                        )
                        st.session_state.feynman_explanations[idx] = explanation
                else:
                    explanation = st.session_state.feynman_explanations[idx]
                
                st.success(f"**Simple Explanation:**\n\n{explanation}")
    
    st.markdown("---")
    
    # MILESTONE 3: LOOP-BACK MECHANISM
    # After Feynman explanation, workflow returns to question generation/verification
    st.markdown("### Ready to Try Again?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(" Retake Quiz (with new questions)", type="primary", use_container_width=True):
            # MILESTONE 3: Track retry attempts per checkpoint
            st.session_state.retry_count[cp.id] = current_retry + 1
            st.session_state.answers = {}
            st.session_state.show_hint = {}
            st.session_state.hints_cache = {}
            st.session_state.feynman_explanations = {}
            st.session_state.quiz_submitted = False
            
            # MILESTONE 3: Generate new questions for adaptive re-assessment
            with st.spinner("Generating new questions based on your weak areas..."):
                st.session_state.questions = generate_questions(cp, st.session_state.study_material)
            
            # MILESTONE 3: Loop back to quiz stage
            st.session_state.stage = "quiz"
            st.rerun()
    
    with col2:
        if st.button("See Final Results", use_container_width=True):
            st.session_state.stage = "results"
            st.rerun()
    
    # Display retry information
    retries_left = st.session_state.max_retries - current_retry
    if retries_left > 0:
        st.info(f"You have {retries_left} more attempt(s) to improve your score!")
    else:
        st.warning("This is your final attempt. Review the explanations carefully!")

# MILESTONE 4: RESULTS & CHECKPOINT PROGRESSION
def render_results():
    cp = st.session_state.current_checkpoint
    st.header("Quiz Results")
    
    score_pct = st.session_state.score * 100
    passed = st.session_state.score >= cp.pass_mark  # MILESTONE 2: Threshold check
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Your Score", f"{score_pct:.1f}%")
    with col2:
        st.metric("Pass Mark", f"{int(cp.pass_mark * 100)}%")
    with col3:
        if passed:
            st.success("PASSED!")
        else:
            st.error("Not Passed")
    
    if st.session_state.weak_areas:
        st.markdown("### Areas to Review:")
        for area in st.session_state.weak_areas:
            st.markdown(f"- {area}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if passed:
            # MILESTONE 4: Mark checkpoint complete and progress to next
            if st.button("Complete Checkpoint", type="primary", use_container_width=True):
                if cp.id not in st.session_state.completed_checkpoints:
                    st.session_state.completed_checkpoints.append(cp.id)  # MILESTONE 4: Track completion
                # Reset retry count for this checkpoint since it's completed
                if cp.id in st.session_state.retry_count:
                    st.session_state.retry_count[cp.id] = 0
                st.session_state.stage = "select"
                st.session_state.current_checkpoint = None
                st.session_state.study_material = None
                st.session_state.search_index = None
                st.session_state.questions = []
                st.session_state.answers = {}
                st.session_state.quiz_submitted = False
                # MILESTONE 3: Reset Feynman state
                st.session_state.feynman_explanations = {}
                st.session_state.incorrect_answers = {}
                st.rerun()
        else:
            # MILESTONE 3: Loop-back to Feynman teaching for failed attempts
            current_retry = st.session_state.retry_count.get(cp.id, 0)
            if current_retry < st.session_state.max_retries:
                if st.button("Get Simplified Explanations", type="primary", use_container_width=True):
                    st.session_state.stage = "feynman"
                    st.rerun()
            else:
                if st.button("Retake Quiz", type="primary", use_container_width=True):
                    st.session_state.retry_count[cp.id] = 0
                    st.session_state.answers = {}
                    st.session_state.show_hint = {}
                    st.session_state.hints_cache = {}
                    st.session_state.feynman_explanations = {}
                    st.session_state.quiz_submitted = False
                    st.session_state.stage = "quiz"
                    st.rerun()
    
    with col2:
        if st.button("Back to Menu", use_container_width=True):
            st.session_state.stage = "select"
            st.session_state.current_checkpoint = None
            st.session_state.study_material = None
            st.session_state.search_index = None
            st.session_state.questions = []
            st.session_state.answers = {}
            st.session_state.hints_cache = {}
            st.session_state.quiz_submitted = False
            # MILESTONE 3: Reset Feynman state (but preserve retry_count per checkpoint)
            st.session_state.feynman_explanations = {}
            st.session_state.incorrect_answers = {}
            st.rerun()

# MILESTONE 4: MAIN WORKFLOW ORCHESTRATION
def main():
    render_header()
    
    # MILESTONE 4: State-based workflow routing
    if st.session_state.stage == "select":
        render_checkpoint_selection()  # MILESTONE 1: Define checkpoint
    elif st.session_state.stage == "loading":
        st.session_state.stage = "study"
        st.rerun()
    elif st.session_state.stage == "study":
        render_study_material()  # MILESTONE 1 & 2: Gather & process context
    elif st.session_state.stage == "quiz":
        render_quiz()  # MILESTONE 2: Generate questions & assess
    elif st.session_state.stage == "feynman":
        render_feynman_teaching()  # MILESTONE 3: Adaptive teaching
    elif st.session_state.stage == "results":
        render_results()  # MILESTONE 4: Show results & progress

if __name__ == "__main__":
    main()
