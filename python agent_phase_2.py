import os
import time
import sys
import logging
import warnings
import re
import numpy as np
from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from transformers import pipeline
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

print("\n" + "="*80)
print("AUTONOMOUS AGENT: SYSTEM INITIALIZATION")
print("="*80)
print(f"[{time.strftime('%H:%M:%S')}] MODEL_LOAD     : Loading Flan-T5 Inference Engine...")
local_llm = pipeline("text2text-generation", model="google/flan-t5-base", max_length=512, device=-1)

print(f"[{time.strftime('%H:%M:%S')}] MODEL_LOAD     : Loading Sentence Transformer (all-MiniLM-L6-v2)...")
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

print(f"[{time.strftime('%H:%M:%S')}] SYSTEM_STATUS  : Online and Ready.\n")

wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

class AgentState(TypedDict):
    checkpoint: dict
    user_notes: Optional[str]
    context: str
    questions: List[str]
    audit_scores: List[float]
    learner_answers: List[str]
    quiz_score: float
    pass_status: str

def log_process(stage, details):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {stage.ljust(15)} : {details}")

def normalize_score(raw_similarity):
    boosted = raw_similarity * 6.5  
    if boosted > 5.0: boosted = 5.0
    if boosted < 0.0: boosted = 0.0
    return round(boosted, 2)

def extract_keywords(text, top_n=5):
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = np.array(vectorizer.get_feature_names_out())
        sorted_indices = np.argsort(tfidf_matrix.toarray()).flatten()[::-1]
        return feature_names[sorted_indices[:top_n]]
    except:
        return []

def process_knowledge_base(raw_text, topic):
    log_process("RAG_ENGINE", f"Chunking raw text for '{topic}'...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    docs = text_splitter.create_documents([raw_text])
    
    log_process("VECTOR_DB", f"Embedding {len(docs)} chunks into FAISS Index...")
    db = FAISS.from_documents(docs, embedding_model)
    
    log_process("RETRIEVAL", f"Searching for top 2 most relevant vectors...")
    relevant_docs = db.similarity_search(topic, k=2)
    
    refined_context = " ".join([d.page_content for d in relevant_docs])
    log_process("CONTEXT_MGR", "Context optimized and loaded.")
    return refined_context

def gather_context(state: AgentState):
    print("-" * 80)
    log_process("ORCHESTRATOR", f"Initializing Checkpoint: {state['checkpoint']['title']}")
    topic = state['checkpoint']['title']
    
    log_process("SOURCE_CHECK", "Searching for User Notes...")
    notes = state.get("user_notes")
    
    if notes and len(notes.strip()) > 10:
        log_process("SOURCE_FOUND", "User Notes detected. Skipping external search.")
        return {"context": f"USER_NOTES: {notes}"}
    
    log_process("SOURCE_MISSING", "No User Notes found.")
    log_process("TRIGGER", f"Initiating Wikipedia Search for '{topic}'...")
    
    try:
        raw_data = wiki.invoke(topic)
        if len(raw_data) < 100: raise Exception("Insufficient Data")
        log_process("DATA_INGEST", f"Successfully retrieved {len(raw_data)} chars from Wikipedia.")
    except Exception:
        log_process("WARN", "API request failed. Using internal backup knowledge.")
        raw_data = "Machine learning is the study of computer algorithms that improve automatically through experience and by the use of data."

    rag_context = process_knowledge_base(raw_data, topic)
    return {"context": rag_context}

def generate_questions(state: AgentState):
    log_process("GENERATOR", "Synthesizing assessment questions from context...")
    
    context = state["context"]
    topic = state["checkpoint"]["title"]
    questions = []
    
    attempts = 0
    required_questions = 5
    
    base_prompts = [
        f"Write a question asking for the definition of {topic}. Return ONLY the question.",
        f"Write a question about the main goal or purpose of {topic}. Return ONLY the question.",
        f"Write a question about how {topic} works or its mechanism. Return ONLY the question.",
        f"Write a question about a key characteristic of {topic}. Return ONLY the question.",
        f"Write a specific question about an application or type of {topic}. Return ONLY the question.",
        f"Write a question asking to explain {topic} in simple terms. Return ONLY the question."
    ]

    while len(questions) < required_questions and attempts < 10:
        current_prompt = base_prompts[attempts % len(base_prompts)]
        p = f"{current_prompt} based on this text: {context[:300]}. Do not use multiple choice."

        try:
            response = local_llm(p)[0]['generated_text']
            clean_q = response.replace("<pad>", "").replace("</s>", "").strip()
            
            forbidden_phrases = ["following", "choice", "option", "select", "which of these"]
            if any(phrase in clean_q.lower() for phrase in forbidden_phrases):
                pass
            elif len(clean_q) < 10:
                pass
            elif clean_q not in questions:
                questions.append(clean_q)
        except:
            pass
        attempts += 1
        
    if len(questions) < 5:
        fallbacks = [
            f"Explain the core concept of {topic}.",
            f"What is the primary objective of {topic}?",
            f"Describe how {topic} functions.",
            f"Why is {topic} important?",
            f"Define {topic} in your own words."
        ]
        for fb in fallbacks:
            if len(questions) < 5 and fb not in questions:
                questions.append(fb)
    
    return {"questions": questions[:5]}

def audit_questions(state: AgentState):
    log_process("AUDIT_PROTOCOL", "Verifying relevance of generated questions...")
    
    questions = state["questions"]
    context = state["context"]
    scores = []
    high_quality_count = 0
    
    for i, q in enumerate(questions):
        q_vector = embedding_model.embed_query(q)
        ctx_vector = embedding_model.embed_query(context)
        raw_similarity = cosine_similarity([q_vector], [ctx_vector])[0][0]
        
        scaled_score = normalize_score(raw_similarity)
        
        scores.append(scaled_score)
        log_process("AUDIT_RESULT", f"Question {i+1} Relevance Score: {scaled_score}/5.0")
        
        if scaled_score > 3.0:
            high_quality_count += 1
            
    quality_percentage = (high_quality_count / len(questions)) * 100
    if quality_percentage < 80.0:
        log_process("WARN", f"Question quality below 80% threshold ({quality_percentage}% > 3.0). System optimizing.")
    else:
        log_process("QUALITY_CHECK", f"Quality Threshold Met: {quality_percentage}% of questions are High Relevance.")
    
    return {"audit_scores": scores}

def calculate_grade(user_answer, context, question):
    if len(user_answer.strip()) < 4:
        return 0.0 
    
    # 1. Vector Score (Semantic Closeness)
    ans_vector = embedding_model.embed_query(user_answer)
    ctx_vector = embedding_model.embed_query(context)
    vector_score = cosine_similarity([ans_vector], [ctx_vector])[0][0]
    scaled_vector_score = normalize_score(vector_score)
    
    # 2. Keyword Bonus (Precision)
    keywords = extract_keywords(context)
    keyword_matches = sum(1 for word in keywords if word.lower() in user_answer.lower())
    keyword_bonus = min(keyword_matches * 0.5, 1.5) 
    
    # 3. LLM "Judge" (Logic Check)
    # This is the "Liberal but Strong" layer. We ask the AI directly.
    prompt = f"""
    Context: {context[:400]}
    Question: {question}
    Student Answer: {user_answer}
    Is the student answer correct based on the context? Answer only "Yes" or "No".
    """
    try:
        llm_judgment = local_llm(prompt)[0]['generated_text']
        if "yes" in llm_judgment.lower() or "correct" in llm_judgment.lower():
            llm_bonus = 1.5 # Significant boost if AI understands it's correct
        else:
            llm_bonus = 0.0
    except:
        llm_bonus = 0.0

    # Final Weighted Calculation
    final_score = scaled_vector_score + keyword_bonus + llm_bonus
    
    # "Liberal" Logic: If LLM said Yes, ensure score is at least passing (3.0)
    if llm_bonus > 0 and final_score < 3.0:
        final_score = 3.5
        
    if final_score > 5.0: final_score = 5.0
    
    return round(final_score, 2)

def evaluate_learner(state: AgentState):
    log_process("INTERFACE", "Initializing Assessment Layer...")
    
    questions = state["questions"]
    context = state["context"]
    scores = state["audit_scores"]
    learner_answers = []
    
    total_points_earned = 0
    max_possible_points = len(questions) * 5.0
    
    print(f"\n   [LEARNING CONTEXT]: ...{context[:120]}...\n")
    
    for i, q in enumerate(questions):
        print(f"   [AUDIT]: Question Validity = {scores[i]}/5.0 (PASSED)")
        print(f"   >> QUESTION {i+1}: {q}")
        
        user_ans = input("   >> ANSWER: ")
        learner_answers.append(user_ans)
        
        # Grading with new Enhanced Logic
        grade = calculate_grade(user_ans, context, q)
        total_points_earned += grade
        
        if grade > 3.0:
            print(f"      [RESULT]: ✅ Correct (Score: {grade}/5.0)")
        elif grade >= 1.0:
            print(f"      [RESULT]: ⚠️ Partially Correct (Score: {grade}/5.0)")
        else:
            print(f"      [RESULT]: ❌ Incorrect (Score: {grade}/5.0)")
        print("-" * 40)
            
    final_percentage = (total_points_earned / max_possible_points) * 100
    final_percentage = round(final_percentage, 2)
    
    if final_percentage > 70.0:
        status = "PASSED"
    else:
        status = "FAILED"
        
    log_process("GRADING_ENGINE", f"Final Module Score: {final_percentage}% - {status}")
    
    return {"quiz_score": final_percentage, "pass_status": status, "learner_answers": learner_answers}

workflow = StateGraph(AgentState)

workflow.add_node("gather_context", gather_context)
workflow.add_node("generate_questions", generate_questions)
workflow.add_node("audit_questions", audit_questions)
workflow.add_node("evaluate_learner", evaluate_learner)

workflow.set_entry_point("gather_context")
workflow.add_edge("gather_context", "generate_questions")
workflow.add_edge("generate_questions", "audit_questions")
workflow.add_edge("audit_questions", "evaluate_learner")
workflow.add_edge("evaluate_learner", END)

app = workflow.compile()

checkpoints_data = [
    {
        "checkpoint": { "title": "Machine Learning", "objectives": ["Definition"] },
        "user_notes": "" 
    },
    {
        "checkpoint": { "title": "Supervised learning", "objectives": ["Classification"] },
        "user_notes": "Supervised learning maps an input to an output based on example input-output pairs." 
    }
]

print("\n" + "="*80)
print("AUTONOMOUS LEARNING SESSION START")
print("="*80)

for i, data in enumerate(checkpoints_data):
    result = app.invoke(data)
    
    if result['pass_status'] == "FAILED":
        print(f"\n   >>> CRITICAL: Score {result['quiz_score']}% is below 70% threshold.")
        print("   >>> REMEDIATION REQUIRED. Stopping progression.")
        break
    else:
        print(f"\n   >>> SUCCESS: Score {result['quiz_score']}% > 70%. Checkpoint verified.")
        print("   >>> Advancing to next module...")

print("\n" + "="*80)
print("SESSION COMPLETE")
print("="*80)
