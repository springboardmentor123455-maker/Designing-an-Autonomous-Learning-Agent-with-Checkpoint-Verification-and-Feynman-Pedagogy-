from contextProcessor import ContextProcessor, SessionVectorStore
from gathercontext import GatherContext
from langgraph.types import interrupt
from langsmith import traceable
from llm_model import model, model_1
from promts import (answer_parser, answer_templete, feynman_parser,
                    feynman_promt, gap_detection_prompt, gap_parser,
                    question_parser, question_temp, validator_parser,
                    validatorTemplate)
from state import LearningState


@traceable(name="start_checkpoint")
def start_checkpoint(state: LearningState) -> LearningState:
    """
    Entry node.
    Currently a pass-through, but kept for clarity and extensibility.
    """
    return state

@traceable(name="gather_context")
def gather_context(state: LearningState):
    """
    Gather context:
    - Use user notes if provided
    - Otherwise fallback to web search using checkpoint topic
    """
    context = ""
    gatherer = GatherContext()
    topic = state['checkpoint']['topic']
    objectives = state['checkpoint']['objectives']
    success = state['checkpoint']['success_criteria']
    if not state['user_Notes']:
        context = gatherer.gathercontext(topic , objectives , success)
    else :
        context = state['user_Notes']
    
    context_itr = state["context_iteration"]+1
    return {'gether_context': context , "context_iteration" : context_itr}

validator_chain = validatorTemplate | model | validator_parser
@traceable(name="evalution_context")
def evalution_context(state : LearningState):
    topic = state['checkpoint']['topic']
    objective = state['checkpoint']['objectives']
    context = state['gether_context']
    score = 10
    evalution = "approved"
    try :
        respone=validator_chain.invoke({'topic' : topic ,'objective' : objective ,'context': context})
        score = respone.score
        evalution = respone.evaluation
    except Exception as e :
        print(e)

    return {'context_evalution':evalution ,'revelence_score':[score]}

@traceable(name="process_context")
def process_context(state: LearningState):
    context = state['gether_context']
    process = ContextProcessor()
    chunks = process.chunk(context)
    vetore = SessionVectorStore()
    vetore.create(chunks)
    query = f'topic{state["checkpoint"]["topic"]} and objective {state["checkpoint"]["objectives"]}'
    docs = vetore.similarity_search(query)
    return {'chunks':chunks , 'vectore_semalirty':docs} 

question_chain = question_temp | model_1| question_parser
@traceable(name="question_gentration")
def question_gentration(state:LearningState):
    docs = state['vectore_semalirty']
    str = ""
    for d in docs:
        str += d
    promt = {'topic':state['checkpoint']['topic'],
            'objectives':state['checkpoint']['objectives'], 
            'context_chunks':docs
            }
    ques = []
    try :
        respone=question_chain.invoke(promt)
        ques.append(respone.question_1)
        ques.append(respone.question_2)
        ques.append(respone.question_3)
    except Exception as e :
        print("unexpected  error ", e)
        ques.append(f"{state['checkpoint']['objectives'][0]}")
        ques.append(f"{state['checkpoint']['objectives'][1]}")
        ques.append(f"{state['checkpoint']['objectives'][2]}")
    return{'questions' : ques }

@traceable(name="wait_answer")
def wait_answer(state: LearningState):
    """
    Explicit human-in-the-loop pause.
    Graph execution stops here.
    """
    decision = interrupt({
        "type": "approval",
        "reason": "User Submit are your answer",
        "gather_contex" : state['gether_context'],
        "question": state['questions'],
        "answers" : [],
        "instruction": "Approve this question? yes/no"
    })

    if decision['approved'] == 'yes':
        print(f" Approved the answers : {decision['answers']}")
        return {'answers' :decision['answers']}
    else:
        return state

@traceable(name="evauate_answer")
def evauate_answer(state:LearningState):
    chain = answer_templete|model_1|answer_parser
    context = state['vectore_semalirty']
    question = state['questions']
    answers = state['answers']
    result = chain.invoke({"questions": question,   # List[str]
    "answers": answers,       # List[str]
    "context": context })
    print(answers)
    score = result.scores
    return {'answers': answers ,'score_percentage':score , 'passed':sum(score)/len(score)>=70}

@traceable(name="detect_gap")
def detect_gap(state:LearningState):
    chain = gap_detection_prompt|model_1|gap_parser
    question  = state['questions']
    answer = state['answers']
    context = state['vectore_semalirty']
    respone = chain.invoke({'questions' : question , 'answers':answer , 'context':context})
    gap = ""
    gaps_with_number = {}
    for doc in respone.gaps:
        gap += doc.gap
        gaps_with_number[doc.question_number] = doc.gap  
    return {'gaps':gap , 'gaps_list' : gaps_with_number}

@traceable(name="feynman_teach")
def feynman_teach(state:LearningState):
    chain = feynman_promt|model_1|feynman_parser
    gaps = state['gaps']
    context = state['gether_context']
    respones = chain.invoke({'gaps' : gaps , "context" : context})
    itr = state["feynman_iteration"]+1
    print(respones)
    return {'feynman_explanation' : respones.explanation , "feynman_iteration" : itr} 
    

