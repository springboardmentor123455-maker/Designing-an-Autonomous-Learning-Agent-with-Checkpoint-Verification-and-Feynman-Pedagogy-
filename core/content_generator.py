import json
import re
from typing import List, Dict, Optional
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage
from services.huggingface_service import HuggingFaceService

class ContentGenerator:
    """Handles content generation for lessons, quizzes, and study plans"""
    
    def __init__(self, hf_service: HuggingFaceService):
        self.hf_service = hf_service
        self.search_tool = DuckDuckGoSearchRun()
    
    def generate_study_plan(self, topic: str, doc_context: Optional[str] = None) -> List[Dict]:
        """Generate a 5-step study plan"""
        # ... (same as original but using hf_service)
    
    def generate_lesson(self, topic: str, objective: str, doc_text: Optional[str] = None) -> str:
        """Generate lesson content"""
        # ... (same as original but using hf_service)
    
    def generate_quiz(self, context: str, topic: str) -> List[str]:
        """Generate quiz questions"""
        # ... (same as original but using hf_service)
    
    def grade_answers(self, topic: str, questions: List[str], answers: List[str]) -> List[Dict]:
        """Grade quiz answers"""
        # ... (same as original but using hf_service)
    
    def generate_remedial_explanation(self, topic: str, failed_concepts: List[str]) -> str:
        """Generate Feynman-style remedial explanations"""
        prompt = f"""Act as Richard Feynman, the Great Explainer. 
        
        The student is struggling with: {failed_concepts} about {topic}
        
        Please explain these concepts using:
        1. Simple, everyday analogies
        2. Plain English with no jargon
        3. Concrete examples a beginner would understand
        4. Encouraging, patient tone
        5. Colorful, vivid language that paints a picture
        
        Your explanation should help the student grasp the essence of these concepts intuitively."""
        
        try:
            response = self.hf_service.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            return f"I'd love to explain this in simple terms, but I'm having technical difficulties. Please try again!"