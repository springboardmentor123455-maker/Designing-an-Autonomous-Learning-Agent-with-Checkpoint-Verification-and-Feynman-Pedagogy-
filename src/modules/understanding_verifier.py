"""Understanding verification module for scoring learner answers (Milestone 2)."""
from typing import List, Dict, Any, Tuple
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.models.checkpoint import Checkpoint
from src.utils.llm_provider import get_llm


class UnderstandingVerifier:
    """
    Evaluates learner answers against context and calculates understanding scores.
    
    Implements the 70% threshold logic for determining checkpoint passage.
    """
    
    def __init__(self, passing_threshold: float = 0.70):
        """
        Initialize the understanding verifier.
        
        Args:
            passing_threshold: Minimum score to pass (default 70%)
        """
        self.llm = get_llm()
        self.passing_threshold = passing_threshold
        print(f"Understanding verifier initialized (passing threshold: {passing_threshold*100:.0f}%)")
    
    def evaluate_answers(
        self,
        questions: List[Dict[str, Any]],
        answers: List[Dict[str, Any]],
        context: str
    ) -> Tuple[float, bool, List[str]]:
        """
        Evaluate learner answers and calculate overall score.
        
        Args:
            questions: List of questions
            answers: List of learner answers
            context: Relevant context from vector store
            
        Returns:
            Tuple of (average_score, passed, weak_concepts)
        """
        if not answers:
            return 0.0, False, []
        
        print(f"\n=== EVALUATING {len(answers)} ANSWERS ===")
        
        scores = []
        weak_concepts = []
        
        for answer in answers:
            question_id = answer.get('question_id')
            answer_text = answer.get('answer', '')
            
            # Find corresponding question
            question = next((q for q in questions if q['id'] == question_id), None)
            if not question:
                continue
            
            # Score the answer
            score = self._score_answer(question, answer_text, context)
            scores.append(score)
            
            print(f"\nQ{question_id}: {question['question'][:60]}...")
            print(f"Score: {score:.0%}")
            
            # Track weak concepts (< 70%)
            if score < self.passing_threshold:
                weak_concepts.append(question['objective'])
        
        # Calculate average
        avg_score = sum(scores) / len(scores) if scores else 0.0
        passed = avg_score >= self.passing_threshold
        
        print(f"\n{'='*50}")
        print(f"Average Score: {avg_score:.1%}")
        print(f"Status: {'PASSED' if passed else 'NEEDS IMPROVEMENT'}")
        print(f"{'='*50}")
        
        return avg_score, passed, weak_concepts
    
    def _score_answer(
        self,
        question: Dict[str, Any],
        answer: str,
        context: str
    ) -> float:
        """
        Score a single answer.
        
        Args:
            question: Question dictionary
            answer: Learner's answer
            context: Relevant context
            
        Returns:
            Score between 0.0 and 1.0
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert educator evaluating a learner's answer.

Score the answer based on:
1. Correctness: Is the answer factually correct?
2. Completeness: Does it address all parts of the question?
3. Understanding: Does it show genuine comprehension?

Provide ONLY a score from 0 to 100 (integer), nothing else.

Scoring guide:
- 90-100: Excellent, comprehensive, accurate
- 70-89: Good, mostly correct with minor gaps
- 50-69: Partial understanding, some errors
- 30-49: Significant misunderstanding
- 0-29: Incorrect or irrelevant"""),
            ("user", """Question: {question}

Objective Being Tested: {objective}

Reference Context:
{context}

Learner's Answer:
{answer}

Score (0-100):""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({
                "question": question['question'],
                "objective": question['objective'],
                "context": context[:2000],  # Limit context
                "answer": answer
            })
            
            # Extract numeric score
            score_text = result.strip()
            score = int(score_text) / 100.0
            
            # Clamp to 0-1 range
            score = max(0.0, min(1.0, score))
            
            return score
            
        except Exception as e:
            print(f"  Error scoring answer: {e}")
            # Default to moderate score on error
            return 0.5
    
    def generate_simulated_answers(
        self,
        questions: List[Dict[str, Any]],
        quality: str = "good"
    ) -> List[Dict[str, Any]]:
        """
        Generate simulated learner answers for testing.
        
        Args:
            questions: List of questions
            quality: Answer quality ('good', 'poor', or 'mixed')
            
        Returns:
            List of simulated answers
        """
        print(f"\nGenerating {quality} simulated answers for testing...")
        
        answers = []
        for i, question in enumerate(questions):
            # Determine quality for this specific question
            if quality == "mixed":
                # Mix good and poor answers (about 50/50 to get ~60% score)
                current_quality = "poor" if i % 2 == 0 else "good"
            else:
                current_quality = quality
            
            if current_quality == "good":
                # Generate comprehensive answers that should score >= 70%
                answer_prompt = f"Provide a comprehensive, accurate answer to: {question['question']}"
                system_msg = "You are simulating a knowledgeable learner. Provide a thorough, accurate answer that demonstrates understanding."
            else:
                # Generate incomplete/incorrect answers that should score < 70%
                answer_prompt = f"Provide a very brief, vague answer to: {question['question']}"
                system_msg = "You are simulating a confused learner. Provide a brief, incomplete answer with gaps or misconceptions. Keep it under 15 words."
            
            try:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", system_msg),
                    ("user", answer_prompt)
                ])
                
                chain = prompt | self.llm | StrOutputParser()
                answer_text = chain.invoke({})
                
                answers.append({
                    'question_id': question['id'],
                    'answer': answer_text
                })
                
                # Show sample of what was generated
                if i == 0:
                    print(f"  Sample answer: \"{answer_text[:60]}...\"")
                
            except Exception as e:
                print(f"  Error generating simulated answer: {e}")
                # Provide default answer based on quality
                if current_quality == "poor":
                    default_answer = "I don't know."
                else:
                    default_answer = "This is a simulated answer for testing."
                
                answers.append({
                    'question_id': question['id'],
                    'answer': default_answer
                })
        
        print(f"Generated {len(answers)} simulated answers")
        return answers
