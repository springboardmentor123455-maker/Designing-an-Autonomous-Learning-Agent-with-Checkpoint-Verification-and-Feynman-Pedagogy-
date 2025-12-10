import os
from dotenv import load_dotenv

load_dotenv()

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY", "")
if not os.environ["TAVILY_API_KEY"]:
    print("TAVILY_API_KEY not found in .env file")

from dataclasses import dataclass
from typing import List, Dict
import json

@dataclass
class Checkpoint:
    id: str
    topic: str
    objectives: List[str]
    pass_mark: float = 0.6

CHECKPOINTS: List[Checkpoint] = [
    Checkpoint(
        id="cp1",
        topic="Basics of Neural Networks",
        objectives=[
            "Explain what a neuron is in a neural network.",
            "Describe how weights and bias affect the output.",
            "Define an activation function and its purpose?",
        ]
    ),
    Checkpoint(
        id="cp2",
        topic="Forward Propagation",
        objectives=[
            "How input data go through all the layers?",
            "Calculate output for simple 2-layer network?"
        ]
    ),
    Checkpoint(
        topic="Loss Function",
        id="cp3",
        objectives=[
            "What loss function actually measure?",
            "Difference between training loss and accuracy explain?"
        ]
    )
]

USER_NOTES: Dict[str, str] = {
    "cp1": """
Neural network have many neurons in layers. Each neuron take inputs, multiply
them with weights, add bias, then put through activation function like ReLU
or sigmoid. Weights tell how much each input important, bias give little
adjustment. Activation function make it non-linear so model can learn
complex patterns not just straight lines.
    """
}

# Initialization

class FastLLMWrapper:
    
    def __init__(self):
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        )
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model.eval()
    
    def invoke(self, message):
        import torch
        
        prompt = f"<|system|>\nYou are a helpful AI teacher assistant.</s>\n<|user|>\n{message}</s>\n<|assistant|>\n"
        
        try:
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=768,
                padding=True,
                return_attention_mask=True
            )
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    attention_mask=inputs.attention_mask,
                    max_new_tokens=1000,
                    temperature=0.5,
                    top_p=0.8,
                    top_k=30,
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.15
                )
            
            generated = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            ).strip()
            
            class Response:
                def __init__(self, content):
                    self.content = content
            
            return Response(generated if generated else "")
            
        except Exception:
            class Response:
                def __init__(self, content):
                    self.content = content
            return Response("")

chat_ai = FastLLMWrapper()

# Web Search and Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_to_numbers = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

web_searcher = TavilySearchResults(k=3)

text_cutter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)

from typing import Dict, List, Any, TypedDict
from langchain_core.documents import Document

class StudyTracker(TypedDict):
    lesson_num: int
    current_checkpoint: Dict
    study_notes: str
    material_good: bool
    quiz_questions: List[str]
    my_answers: List[str]
    my_score: float
    marks_got: float
    weak_topics: List[str]
    all_done: bool
    all_checkpoints: List[Any]
    all_user_notes: Dict[str, str]
    search_index: Any
    material_retry_count: int
    available_checkpoints: List[Dict]

def make_search_query(checkpoint):
    goals_string = "; ".join(checkpoint.objectives)
    return f"{checkpoint.topic}: {goals_string}"

# Get study material from notes or web search
def get_study_stuff(checkpoint_obj, user_notes_data):
    if checkpoint_obj.id in user_notes_data and user_notes_data[checkpoint_obj.id].strip():
        print("Using notes for this checkpoint.")
        return user_notes_data[checkpoint_obj.id]

    search_string = make_search_query(checkpoint_obj)
    print(f"[Web Search] Fetching material for topic: {checkpoint_obj.topic}")
    
    try:
        web_results = web_searcher.invoke({"query": search_string})
    except Exception:
        return f"Topic: {checkpoint_obj.topic}\n\nLearning objectives:\n" + "\n".join([f"- {obj}" for obj in checkpoint_obj.objectives])

    all_content = []
    
    if isinstance(web_results, list):
        for result in web_results:
            if isinstance(result, dict):
                text_content = result.get("content", "")
            elif isinstance(result, str):
                text_content = result
            else:
                text_content = str(result)
            
            if text_content and len(text_content.strip()) > 0:
                all_content.append(text_content)
    elif isinstance(web_results, dict):
        text_content = web_results.get("content", str(web_results))
        if text_content:
            all_content.append(text_content)
    else:
        all_content.append(str(web_results))
    
    if all_content:
        print(f"[Web Search] Retrieved {len(all_content)} result(s). Full content below:\n")
        full_content = "\n\n---\n\n".join(all_content)
        print(full_content)
        print("\n[Web Search] End of content.\n")
        return full_content
    else:
        print("[Web Search] No content returned; falling back to objectives.")
        return f"Topic: {checkpoint_obj.topic}\n\nLearning objectives:\n" + "\n".join([f"- {obj}" for obj in checkpoint_obj.objectives])

# Check if study material is of good quality
def check_material_good(checkpoint, material_text):
    if len(material_text.strip()) > 50 and "neural network" in material_text.lower():
        return True, 5.0, "User-provided notes"
    
    message = f"""Rate learning material 1-5 (5=excellent).

Topic: {checkpoint.topic}
Objectives: """ + "; ".join(checkpoint.objectives) + f"""

Respond ONLY with JSON: {{"score": 4.5, "reason": "brief explanation"}}

Material:
{material_text[:1500]}
"""

    ai_reply = chat_ai.invoke(message)
    reply_text = ai_reply.content if hasattr(ai_reply, "content") else str(ai_reply)

    info = None
    
    try:
        info = json.loads(reply_text)
    except:
        pass
    
    if not info:
        try:
            import re
            json_pattern = r'\{[^{}]*"score"[^{}]*\}'
            matches = re.findall(json_pattern, reply_text)
            if matches:
                info = json.loads(matches[0])
        except:
            pass
    
    if not info:
        start_pos = reply_text.find("{")
        end_pos = reply_text.rfind("}")
        if start_pos != -1 and end_pos != -1:
            try:
                info = json.loads(reply_text[start_pos:end_pos+1])
            except:
                pass
    
    if not info:
        return True, 4.5, "Material approved"

    mark = float(info.get("score", 4.5))
    reason = info.get("reason", "Good material")
    good_enough = mark >= 4.0

    return good_enough, mark, reason

def make_search_index(material_text):
    one_doc = [Document(page_content=material_text)]
    small_pieces = text_cutter.split_documents(one_doc)
    search_index = FAISS.from_documents(small_pieces, text_to_numbers)
    return search_index

# RAG: Get relevant context from knowledge base
def get_rag_context(search_index, question, top_k=3):
    if search_index is None:
        return ""
    
    try:
        relevant_docs = search_index.similarity_search(question, k=top_k)
        context_pieces = [doc.page_content for doc in relevant_docs]
        return "\n\n".join(context_pieces)
    except Exception:
        return ""

# RAG: Answer question using retrieved context
def answer_with_rag(search_index, question, checkpoint_topic):
    context = get_rag_context(search_index, question)
    
    if not context:
        return f"Unable to retrieve relevant information for: {question}"
    
    prompt = f"""Topic: {checkpoint_topic}
Question: {question}

Relevant Context:
{context[:1000]}

Provide a clear, concise answer based on the context above."""
    
    try:
        response = chat_ai.invoke(prompt)
        answer = response.content if hasattr(response, "content") else str(response)
        return answer.strip() if answer else "Unable to generate answer"
    except Exception:
        return "Error generating answer"

# Generate quiz questions from study material
def make_questions_from_notes(checkpoint_info, notes_content, number_of_questions=5):
    message_for_ai = f"""Create {number_of_questions} specific questions about: {checkpoint_info.topic}

Must cover these learning objectives:
""" + "\n".join([f"- {obj}" for obj in checkpoint_info.objectives]) + f"""

Based on this content:
{notes_content[:1500]}

IMPORTANT: Generate real questions about the topic above. Number them 1., 2., 3., etc.
Do NOT include any answers or explanations.

Your questions:"""

    ai_reply_got = chat_ai.invoke(message_for_ai)
    reply_text_got = ai_reply_got.content if hasattr(ai_reply_got, "content") else str(ai_reply_got)

    ready_questions_list = []
    lines = reply_text_got.split("\n")
    
    # Exclude bad patterns
    bad_patterns = ["what is x", "how does y", "what is z", "example", "like:", "such as:", "e.g."]
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        line_lower = line.lower()
        if any(bad in line_lower for bad in bad_patterns):
            continue
        
        # Skip lines that start with "Answer:" or similar
        if line_lower.startswith(("answer:", "explanation:", "note:", "important:", "your questions:")):
            continue
        
        if len(line) > 3 and line[0].isdigit() and '.' in line[:4]:
            # Extract question text after number
            parts = line.split(".", 1)
            if len(parts) > 1:
                question = parts[1].strip()

                ans_pos = question.lower().find("answer:")
                if ans_pos != -1:
                    question = question[:ans_pos].strip()

                # Remove leading "Q:" prefixes
                if question.lower().startswith("q:"):
                    question = question[2:].strip()

                qmark_pos = question.find("?")
                if qmark_pos != -1:
                    question = question[:qmark_pos+1].strip()
                
                if question and len(question) > 15 and '?' in question:
                    topic_words = checkpoint_info.topic.lower().split()
                    if any(word in question.lower() for word in topic_words) or len(ready_questions_list) < 2:
                        ready_questions_list.append(question)
                        
                        if len(ready_questions_list) >= number_of_questions:
                            break
    
    if len(ready_questions_list) < 2:
        ready_questions_list = []
        for obj in checkpoint_info.objectives:
            if not obj.endswith("?"):
                ready_questions_list.append(obj + "?")
            else:
                ready_questions_list.append(obj)
            if len(ready_questions_list) >= number_of_questions:
                break
    
    return ready_questions_list[:number_of_questions]

# Grade student answers
def check_student_answers(checkpoint_info, notes_content, questions_list, student_answers_list):
    if len(questions_list) != len(student_answers_list):
        return 0.0, []

    all_marks_list = []
    student_weak_areas = []

    # Extract concepts from notes
    notes_lower = notes_content.lower()
    
    question_count = 0
    for one_question, one_student_answer in zip(questions_list, student_answers_list):
        question_count = question_count + 1
        
        if not one_student_answer or len(one_student_answer.strip()) < 3:
            all_marks_list.append(0.0)
            student_weak_areas.append("No answer provided")
            continue

        mark_received = 0.0 

        try:
            mark_received = keyword_based_grading(one_question, one_student_answer, notes_content)
            all_marks_list.append(mark_received)
            if mark_received < 0.7:
                weak_label = one_question.strip()[:140] or f"Question {question_count}"
                student_weak_areas.append(weak_label)
        except Exception:
            mark_received = keyword_based_grading(one_question, one_student_answer, notes_content)
            all_marks_list.append(mark_received)
            if mark_received < 0.7:
                weak_label = one_question.strip()[:140] or f"Question {question_count}"
                student_weak_areas.append(weak_label)

    if len(all_marks_list) > 0:
        average_marks = sum(all_marks_list) / len(all_marks_list)
    else:
        average_marks = 0.0

    return average_marks, student_weak_areas

def keyword_based_grading(question, answer, notes):
    answer_lower = answer.lower()
    notes_lower = notes.lower()
    question_lower = question.lower()
    
    score = 0.0
    
    word_count = len(answer.split())
    if word_count >= 10:
        score += 0.3
    elif word_count >= 5:
        score += 0.2
    elif word_count >= 3:
        score += 0.1
    
    key_terms = []
    if "neuron" in question_lower:
        key_terms = ["neuron", "input", "weight", "bias", "activation"]
    elif "weight" in question_lower or "bias" in question_lower:
        key_terms = ["weight", "bias", "multiply", "important", "adjust"]
    elif "activation" in question_lower:
        key_terms = ["activation", "function", "relu", "sigmoid", "non-linear"]
    elif "forward" in question_lower or "propagation" in question_lower:
        key_terms = ["layer", "forward", "propagation", "input", "output"]
    elif "loss" in question_lower:
        key_terms = ["loss", "error", "measure", "training", "accuracy"]
    else:
        key_terms = ["neural", "network", "learn", "data", "model"]
    
    terms_found = sum(1 for term in key_terms if term in answer_lower)
    term_score = min(0.5, terms_found * 0.15)
    score += term_score
    
    if any(word in answer_lower for word in ["process", "compute", "calculate"]):
        score += 0.1
    
    if any(word in answer_lower for word in ["multiply", "add", "apply", "function"]):
        score += 0.1
    
    score = max(0.0, min(1.0, score))
    
    return score

# Explanation for weak topics
def explain_in_simple_words(checkpoint_info, notes_content, weak_areas_list):
    if weak_areas_list:
        weak_areas_text = ", ".join(weak_areas_list)
    else:
        weak_areas_text = "basic concepts"

    simple_explanation_ask = f"""Explain simply for topic: {checkpoint_info.topic}
Weak areas: {weak_areas_text}

Notes:
{notes_content[:1200]}

Use simple words, examples, max 150 words.
"""

    simple_reply = chat_ai.invoke(simple_explanation_ask)
    simple_explanation = simple_reply.content if hasattr(simple_reply, "content") else "simple explanation not available"
    return simple_explanation

# Build study flow using LangGraph
from langgraph.graph import StateGraph, START, END

def pick_next_lesson(current_state):
    all_checkpoints = current_state.get("all_checkpoints", [])
    remaining = current_state.get("available_checkpoints", all_checkpoints[:])
    all_user_notes = current_state["all_user_notes"]
    lesson_number = current_state.get("lesson_num", 0)

    if not remaining:
        print("All lessons finished completely!")
        return {"study_complete": True}

    print("\nChoose a checkpoint to study:")
    for idx, cp in enumerate(remaining, 1):
        print(f"  {idx}. {cp['topic']}")
    print("  q. Quit")

    chosen = None
    while chosen is None:
        user_input = input("Enter number (or q to quit): ").strip().lower()
        if user_input in {"q", "quit", "exit"}:
            print("Ending session by user choice.")
            return {"study_complete": True}
        if user_input.isdigit():
            num = int(user_input)
            if 1 <= num <= len(remaining):
                chosen = remaining[num - 1]
            else:
                print("Invalid number, try again.")
        else:
            print("Please enter a valid number or q to quit.")

    print(f"\n=== Selected: {chosen['topic']} ===")

    return {
        "current_checkpoint": chosen,
        "study_notes": "",
        "notes_good": False,
        "search_index": None,
        "quiz_questions": [],
        "my_answers": [],
        "marks_got": 0.0,
        "weak_topics": [],
        "study_complete": False,
        "lesson_num": lesson_number,
        "all_checkpoints": all_checkpoints,
        "all_user_notes": all_user_notes,
        "material_retry_count": 0,
        "available_checkpoints": remaining
    }

def get_study_material_step(current_state):
    checkpoint_details = current_state["current_checkpoint"]
    checkpoint_obj = Checkpoint(**checkpoint_details)
    user_notes_data = current_state["all_user_notes"]

    notes_got = get_study_stuff(checkpoint_obj, user_notes_data)

    if checkpoint_obj.id not in user_notes_data or not user_notes_data[checkpoint_obj.id].strip():
        print(f"Got study material, length {len(notes_got)} characters.")

    return {"study_notes": notes_got}

def check_material_step(current_state):
    checkpoint_details = current_state["current_checkpoint"]
    checkpoint_obj = Checkpoint(**checkpoint_details)
    notes_text = current_state["study_notes"]
    retry_count = current_state.get("material_retry_count", 0)

    if retry_count >= 2:
        return {"notes_good": True, "material_retry_count": retry_count + 1}

    good_or_not, quality_mark, reason_text = check_material_good(checkpoint_obj, notes_text)

    return {"notes_good": good_or_not, "material_retry_count": retry_count + 1}

def material_decision(current_state):
    return "good_material" if current_state.get("notes_good", False) else "bad_material"

def make_search_index_step(current_state):
    notes_text = current_state["study_notes"]
    index_made = make_search_index(notes_text)
    return {"search_index": index_made}

def make_quiz_step(current_state):
    checkpoint_details = current_state["current_checkpoint"]
    checkpoint_obj = Checkpoint(**checkpoint_details)
    notes_text = current_state["study_notes"]

    questions_made = make_questions_from_notes(checkpoint_obj, notes_text)
    print("\n" + "="*60)
    print(f"QUIZ: {checkpoint_obj.topic}")
    print("="*60)
    print(f"\n{len(questions_made)} questions ready:\n")
    for num, one_q in enumerate(questions_made, 1):
        print(f"  Q{num}. {one_q}")
    print("\n" + "="*60 + "\n")

    return {"quiz_questions": questions_made, "my_answers": []}

def take_quiz_step(current_state):
    questions_list = current_state["quiz_questions"]
    search_index = current_state.get("search_index")
    checkpoint_details = current_state["current_checkpoint"]
    checkpoint_topic = checkpoint_details.get("topic", "")
    
    print("\nPlease provide your answers below.")
    print("(Type 'hint' to get RAG-based help, or just provide your answer)\n")

    student_replies = []
    for q_num, question_text in enumerate(questions_list, 1):
        print(f"\n[Question {q_num}/{len(questions_list)}]")
        print(f"Q: {question_text}")
        print("-" * 50)
        
        while True:
            reply_got = input("Your Answer: ").strip()
            
            if reply_got.lower() == 'hint' and search_index:
                print("\n[RAG Helper]")
                rag_answer = answer_with_rag(search_index, question_text, checkpoint_topic)
                print(f"Hint: {rag_answer}\n")
                print("Now provide your answer:")
                continue
            elif reply_got.lower() == 'hint':
                print("Hint not available. Please provide your answer.\n")
                continue
            else:
                student_replies.append(reply_got)
                break

    return {"my_answers": student_replies}

def check_marks_step(current_state):
    checkpoint_details = current_state["current_checkpoint"]
    checkpoint_obj = Checkpoint(**checkpoint_details)
    notes_text = current_state["study_notes"]
    questions_list = current_state["quiz_questions"]
    answers_list = current_state["my_answers"]

    print("\n" + "="*60)
    print("GRADING RESULTS")
    print("="*60)
    
    final_marks, weak_list = check_student_answers(checkpoint_obj, notes_text, questions_list, answers_list)
    
    print(f"\nYour Total Score: {final_marks*100:.1f}%")
    print(f"Pass Mark Required: {checkpoint_obj.pass_mark*100:.0f}%")
    
    if final_marks >= checkpoint_obj.pass_mark:
        print("\nPASSED! Great job!\n")
    else:
        print(f"\nNeed to improve. You need {(checkpoint_obj.pass_mark - final_marks)*100:.1f}% more.\n")

    if weak_list:
        print("Areas to review:", ", ".join(weak_list))
    print("="*60 + "\n")

    return {"marks_got": final_marks, "weak_topics": weak_list}

def marks_decision(current_state):
    checkpoint_details = current_state["current_checkpoint"]
    checkpoint_obj = Checkpoint(**checkpoint_details)
    pass_limit = checkpoint_obj.pass_mark

    return "lesson_pass" if current_state.get("marks_got", 0) >= pass_limit else "need_reteach"

def reteach_simple_step(current_state):
    checkpoint_details = current_state["current_checkpoint"]
    checkpoint_obj = Checkpoint(**checkpoint_details)
    notes_text = current_state["study_notes"]
    weak_areas_list = current_state.get("weak_topics", [])

    simple_teaching = explain_in_simple_words(checkpoint_obj, notes_text, weak_areas_list)
    print("\n--- Simple Teaching for Weak Areas ---")
    print(simple_teaching)
    print("\nNow we will give new questions to check again.")

    return {}

def lesson_complete_step(current_state):
    checkpoint_details = current_state["current_checkpoint"]
    final_score = current_state.get("marks_got", 0.0) * 100
    all_checkpoints = current_state["all_checkpoints"]
    remaining_before = current_state.get("available_checkpoints", [])
    remaining = [cp for cp in remaining_before if cp.get("id") != checkpoint_details.get("id")]

    print(f"\nCheckpoint '{checkpoint_details['topic']}' finished! Final score: {final_score:.1f}%")

    next_lesson_num = current_state.get("lesson_num", 0) + 1
    all_done = len(remaining) == 0

    return {
        "lesson_num": next_lesson_num,
        "study_complete": all_done,
        "available_checkpoints": remaining
    }

def check_complete(current_state):
    return "finished_all" if current_state.get("study_complete", False) else "more_lessons"

study_flow = StateGraph(StudyTracker)

study_flow.add_node("pick_lesson", pick_next_lesson)
study_flow.add_node("get_material", get_study_material_step)
study_flow.add_node("check_material", check_material_step)
study_flow.add_node("make_index", make_search_index_step)
study_flow.add_node("make_quiz", make_quiz_step)
study_flow.add_node("take_quiz", take_quiz_step)
study_flow.add_node("check_marks", check_marks_step)
study_flow.add_node("reteach_simple", reteach_simple_step)
study_flow.add_node("lesson_done", lesson_complete_step)

study_flow.add_edge(START, "pick_lesson")
study_flow.add_edge("pick_lesson", "get_material")
study_flow.add_edge("get_material", "check_material")

study_flow.add_conditional_edges(
    "check_material",
    material_decision,
    {
        "good_material": "make_index",
        "bad_material": "get_material"
    }
)

study_flow.add_edge("make_index", "make_quiz")
study_flow.add_edge("make_quiz", "take_quiz")
study_flow.add_edge("take_quiz", "check_marks")

study_flow.add_conditional_edges(
    "check_marks",
    marks_decision,
    {
        "lesson_pass": "lesson_done",
        "need_reteach": "reteach_simple"
    }
)

study_flow.add_edge("reteach_simple", "make_quiz")

study_flow.add_conditional_edges(
    "lesson_done",
    check_complete,
    {
        "more_lessons": "pick_lesson",
        "finished_all": END
    }
)

complete_study_system = study_flow.compile()

initial_state = {
    "lesson_num": 0,
    "current_checkpoint": {},
    "study_notes": "",
    "material_good": False,
    "quiz_questions": [],
    "my_answers": [],
    "my_score": 0.0,
    "weak_topics": [],
    "all_done": False,
    "all_checkpoints": [vars(cp) for cp in CHECKPOINTS],
    "available_checkpoints": [vars(cp) for cp in CHECKPOINTS],
    "all_user_notes": USER_NOTES,
    "search_index": None,
    "material_retry_count": 0
}

for state in complete_study_system.stream(initial_state, config={"recursion_limit": 200}):
    pass
