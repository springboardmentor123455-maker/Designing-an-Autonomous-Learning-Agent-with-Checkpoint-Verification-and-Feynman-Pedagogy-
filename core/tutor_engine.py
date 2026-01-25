"""
Updated Tutor Engine with better error handling
"""

import json
from typing import Dict, List, Optional
import logging
from .huggingface_api import HuggingFaceAPI

logger = logging.getLogger(__name__)

class TutorSession:
    """Tutor Session State"""
    def __init__(self):
        self.topic = ""
        self.study_plan = []
        self.current_module = None
        self.lesson_content = ""
        self.quiz_questions = []
        self.user_answers = []
        self.quiz_results = None
        self.failed_concepts = []
        self.modules_completed = 0
        self.attempt_count = 0

class TutorEngine:
    """Main Tutor Engine with error handling"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api = HuggingFaceAPI(api_key)
        self.session = TutorSession()
        logger.info("TutorEngine initialized")
    
    def start_new_session(self, topic: str, doc_text: Optional[str] = None):
        """Start a new learning session"""
        logger.info(f"Starting session for topic: {topic}")
        self.session = TutorSession()
        self.session.topic = topic
        
        # Generate study plan with simple prompt first
        self._generate_simple_study_plan()
    
    def _generate_simple_study_plan(self):
        """Generate simple study plan (fallback)"""
        logger.info("Generating study plan...")
        
        # Use very simple prompt
        prompt = f"""
        Create a 5-step learning path for: {self.session.topic}
        
        Return JSON format:
        {{
            "plan": [
                {{"id": 1, "title": "Step 1", "objective": "Learn basics"}},
                {{"id": 2, "title": "Step 2", "objective": "Core concepts"}},
                {{"id": 3, "title": "Step 3", "objective": "Practice"}},
                {{"id": 4, "title": "Step 4", "objective": "Advanced"}},
                {{"id": 5, "title": "Step 5", "objective": "Mastery"}}
            ]
        }}
        
        Keep titles short and objectives clear.
        """
        
        try:
            response = self.api.generate_text(prompt, max_tokens=512)
            logger.info(f"Study plan response received: {len(response)} chars")
            
            # Try to parse JSON
            json_data = self.api.extract_json(response)
            
            if json_data and 'plan' in json_data:
                plan = json_data['plan'][:5]
                self.session.study_plan = []
                
                for i, item in enumerate(plan):
                    self.session.study_plan.append({
                        'id': i + 1,
                        'title': item.get('title', f'Step {i+1}'),
                        'objective': item.get('objective', f'Learn {self.session.topic}'),
                        'description': item.get('description', '')
                    })
                logger.info(f"Study plan created with {len(self.session.study_plan)} modules")
            else:
                # Use default plan
                self._create_default_plan()
                
        except Exception as e:
            logger.error(f"Error generating study plan: {e}")
            self._create_default_plan()
    
    def _create_default_plan(self):
        """Create default study plan"""
        logger.info("Creating default study plan")
        self.session.study_plan = [
            {
                'id': 1, 
                'title': 'Introduction', 
                'objective': 'Learn the basics',
                'description': 'Start with fundamentals'
            },
            {
                'id': 2, 
                'title': 'Core Concepts', 
                'objective': 'Understand key principles',
                'description': 'Dive into main concepts'
            },
            {
                'id': 3, 
                'title': 'Practice', 
                'objective': 'Apply your knowledge',
                'description': 'Hands-on practice'
            },
            {
                'id': 4, 
                'title': 'Advanced Topics', 
                'objective': 'Explore complex ideas',
                'description': 'Go deeper'
            },
            {
                'id': 5, 
                'title': 'Mastery', 
                'objective': 'Achieve proficiency',
                'description': 'Complete understanding'
            }
        ]
    
    def generate_lesson(self) -> str:
        """Generate lesson content"""
        if not self.session.current_module:
            return "Please select a module first."
        
        logger.info(f"Generating lesson for: {self.session.current_module['title']}")
        
        # Simple prompt for faster response
        prompt = f"""
        Explain this topic simply: {self.session.current_module['title']}
        
        Goal: {self.session.current_module['objective']}
        
        Make it:
        - Easy to understand
        - 300-400 words
        - With examples
        - Clear structure
        
        Use plain language.
        """
        
        try:
            lesson = self.api.generate_text(prompt, max_tokens=768)
            
            if "AI Service Temporarily Unavailable" in lesson:
                # Return a simple offline lesson
                lesson = self._create_offline_lesson()
            
            self.session.lesson_content = lesson
            logger.info(f"Lesson generated: {len(lesson)} chars")
            return lesson
            
        except Exception as e:
            logger.error(f"Lesson generation error: {e}")
            return self._create_offline_lesson()
    
    def _create_offline_lesson(self) -> str:
        """Create a simple offline lesson"""
        module = self.session.current_module
        
        return f"""
        # {module['title']}
        
        ## Learning Objective
        {module['objective']}
        
        ## Key Concepts
        1. **Fundamentals**: Start with basic principles
        2. **Core Ideas**: Understand the main concepts  
        3. **Applications**: Learn how to use this knowledge
        4. **Practice**: Apply what you've learned
        
        ## Study Tips
        - Take notes as you learn
        - Ask questions about unclear points
        - Practice regularly
        - Review previous lessons
        
        ## Next Steps
        1. Make sure you understand these basics
        2. Try to explain it to someone else
        3. Take the quiz to test your knowledge
        
        *Note: AI service is busy. This is a basic outline.*
        """
    
    # Keep other methods similar but add more logging
    
    def generate_quiz(self) -> List[str]:
        """Generate simple quiz questions"""
        logger.info("Generating quiz...")
        
        if not self.session.current_module:
            return []
        
        # Simple questions
        questions = [
            f"What is the main idea of {self.session.current_module['title']}?",
            f"How would you explain this to a beginner?",
            f"What are the key points to remember?",
            f"How is this knowledge useful in practice?",
            f"What should you focus on when learning this?"
        ]
        
        self.session.quiz_questions = questions
        return questions
    
    def grade_quiz(self, answers: List[str]) -> Dict:
        """Simple grading"""
        logger.info("Grading quiz...")
        
        # Simple scoring
        scores = []
        for answer in answers:
            if answer and len(answer.strip()) > 50:
                scores.append(18)  # Good answer
            elif answer and len(answer.strip()) > 20:
                scores.append(12)  # Okay answer
            elif answer and len(answer.strip()) > 0:
                scores.append(8)   # Short answer
            else:
                scores.append(0)   # No answer
        
        total = sum(scores)
        passed = total >= 70
        
        result = {
            "total_score": total,
            "passed": passed,
            "feedback": f"Score: {total}/100",
            "detailed_feedback": [
                {"question": i+1, "score": score, "feedback": "Good!" if score > 15 else "Could be better"}
                for i, score in enumerate(scores)
            ]
        }
        
        if passed:
            self.session.modules_completed += 1
        
        return result