"""Question generation module for assessment (Milestone 2)."""
from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.models.checkpoint import Checkpoint
from src.utils.llm_provider import get_llm


class QuestionGenerator:
    """
    Generates assessment questions based on processed context and objectives.
    
    Generates 3-5 relevant questions per checkpoint to evaluate learner understanding.
    """
    
    def __init__(self):
        """Initialize the question generator."""
        self.llm = get_llm()
    
    def generate_questions(
        self,
        checkpoint: Checkpoint,
        context: str,
        num_questions: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Generate assessment questions for the checkpoint.
        
        Args:
            checkpoint: The learning checkpoint
            context: Relevant context from vector store
            num_questions: Number of questions to generate (3-5)
            
        Returns:
            List of question dictionaries
        """
        num_questions = max(3, min(5, num_questions))  # Ensure 3-5 range
        
        print(f"\nGenerating {num_questions} assessment questions...")
        
        # Create prompt for question generation
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert educator creating assessment questions.

Generate {num_questions} thoughtful questions that test understanding of the learning objectives.
Each question should be clear, specific, and assess a key concept.

Format your response as follows for each question:
Q1: [question text]
OBJECTIVE: [which objective it tests]
DIFFICULTY: [easy/medium/hard]

Q2: [question text]
OBJECTIVE: [which objective it tests]
DIFFICULTY: [easy/medium/hard]

... and so on."""),
            ("user", """Topic: {topic}

Learning Objectives:
{objectives}

Context:
{context}

Generate {num_questions} assessment questions:""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        objectives_text = "\n".join(f"- {obj}" for obj in checkpoint.objectives)
        
        try:
            response = chain.invoke({
                "topic": checkpoint.topic,
                "objectives": objectives_text,
                "context": context[:3000],  # Limit context size
                "num_questions": num_questions
            })
            
            # Parse response into structured questions
            questions = self._parse_questions(response, checkpoint)
            
            print(f"Generated {len(questions)} questions")
            return questions
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            # Return default questions on error
            return self._get_default_questions(checkpoint)
    
    def _parse_questions(
        self,
        response: str,
        checkpoint: Checkpoint
    ) -> List[Dict[str, Any]]:
        """
        Parse LLM response into structured questions.
        
        Args:
            response: LLM response text
            checkpoint: The checkpoint
            
        Returns:
            List of question dictionaries
        """
        questions = []
        current_question = {}
        
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check for question start
            if line.startswith('Q') and ':' in line:
                # Save previous question if exists
                if current_question.get('question'):
                    questions.append(current_question)
                    current_question = {}
                
                # Extract question text
                question_text = line.split(':', 1)[1].strip()
                current_question['question'] = question_text
                current_question['id'] = len(questions) + 1
            
            elif line.upper().startswith('OBJECTIVE:'):
                objective = line.split(':', 1)[1].strip()
                current_question['objective'] = objective
            
            elif line.upper().startswith('DIFFICULTY:'):
                difficulty = line.split(':', 1)[1].strip().lower()
                current_question['difficulty'] = difficulty
        
        # Add last question
        if current_question.get('question'):
            questions.append(current_question)
        
        # Ensure all questions have required fields
        for q in questions:
            if 'objective' not in q:
                q['objective'] = checkpoint.objectives[0]
            if 'difficulty' not in q:
                q['difficulty'] = 'medium'
        
        return questions
    
    def _get_default_questions(self, checkpoint: Checkpoint) -> List[Dict[str, Any]]:
        """
        Get default questions when generation fails.
        
        Args:
            checkpoint: The checkpoint
            
        Returns:
            List of default questions
        """
        return [
            {
                'id': 1,
                'question': f"Explain the key concepts of {checkpoint.topic}",
                'objective': checkpoint.objectives[0],
                'difficulty': 'medium'
            },
            {
                'id': 2,
                'question': f"Provide an example demonstrating {checkpoint.objectives[0] if checkpoint.objectives else checkpoint.topic}",
                'objective': checkpoint.objectives[0] if checkpoint.objectives else checkpoint.topic,
                'difficulty': 'medium'
            },
            {
                'id': 3,
                'question': f"What are the main applications or use cases of {checkpoint.topic}?",
                'objective': checkpoint.objectives[-1] if len(checkpoint.objectives) > 1 else checkpoint.objectives[0],
                'difficulty': 'easy'
            }
        ]
