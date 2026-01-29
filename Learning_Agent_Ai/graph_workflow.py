from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from nodes import (detect_gap, evalution_context, evauate_answer,
                   feynman_teach, gather_context, process_context,
                   question_gentration, start_checkpoint, wait_answer)
from routing import route_after_scoring, route_after_validation
from state import LearningState

# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"] = "Autonomous-Learning-Agent"

graph = StateGraph(LearningState)

graph.add_node('start_checkpoint' , start_checkpoint)
graph.add_node('gather' , gather_context)
graph.add_node('validate' , evalution_context)
graph.add_node('process_context' , process_context)
graph.add_node('question_generation' , question_gentration)
graph.add_node('evaluate_answer' , evauate_answer)
graph.add_node('detect_gap' , detect_gap)
graph.add_node('feynman_teaching' , feynman_teach)
graph.add_node('wait_answer', wait_answer)


graph.add_edge(START , 'start_checkpoint')
graph.add_edge('start_checkpoint' , 'gather')
graph.add_edge('gather' , 'validate')

graph.add_conditional_edges(
    'validate',
    route_after_validation,{
        'approved' : 'process_context',
        'need improment': 'gather'
    }
)
graph.add_edge('process_context' , 'question_generation')
graph.add_edge('question_generation' , 'wait_answer')
graph.add_edge( 'wait_answer', 'evaluate_answer' )
graph.add_conditional_edges(
    'evaluate_answer',
    route_after_scoring,{
        'pass' : END ,
        'feynman':'detect_gap'
    }
)

graph.add_edge('detect_gap' , 'feynman_teaching')
graph.add_edge('feynman_teaching' , 'question_generation')

checkpoint = InMemorySaver()
workflow = graph.compile(checkpointer=checkpoint)
