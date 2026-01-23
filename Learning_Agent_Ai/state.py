
import operator
from typing import Annotated, Dict, List, Literal, Optional, TypedDict

from checkpoint_class_1 import Checkpoint


class LearningState(TypedDict):

    # max context valid perametar
    max_iteration : int 
    context_iteration : int
    #  max feynman teaching for one point 
    feynman_iteration : int

    checkpoint : Checkpoint

    user_Notes : Optional[str]
    gether_context : str

    context_evalution : Literal['approved' , 'need improment']

    revelence_score : Annotated[list[int], operator.add]

    chunks : list[str]
    
    vectore_semalirty : list[str]
    questions: list[str]
    answers: Optional[List[str]] 
    score_percentage: Optional[List[float]]

    gaps_list : Dict[int, str]
    gaps: str 
    feynman_explanation: str

    # =========================
    # CONTROL FLAGS (OPTIONAL)
    # =========================
    passed: bool = False