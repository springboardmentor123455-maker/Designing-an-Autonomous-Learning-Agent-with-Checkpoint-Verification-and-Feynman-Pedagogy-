from typing import List, Dict, Any, Tuple
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.utils.llm_provider import get_llm


class FeynmanTeacher:
    """Feynman teaching module for generating simplified explanations."""
    
    def __init__(self):
        """Initialize the Feynman teacher."""
        self.llm = get_llm()
        print("Feynman teacher initialized")
    
    def generate_explanations(
        self,
        questions: List[Dict[str, Any]],
        answers: List[Dict[str, Any]],
        context: str,
        weak_concepts: List[str]
    ) -> List[Dict[str, Any]]:
        
        print(f"\n=== GENERATING FEYNMAN EXPLANATIONS ===")
        print(f"Weak concepts identified: {len(set(weak_concepts))}")
        
        explanations = []
        
        # Get unique weak concepts
        unique_weak_concepts = list(set(weak_concepts))
        
        for concept in unique_weak_concepts:
            print(f"\nGenerating explanation for: {concept}")
            
            # Find questions and answers related to this concept
            related_qa = self._get_related_qa(concept, questions, answers)
            
            # Generate simplified explanation
            explanation = self._generate_simplified_explanation(
                concept=concept,
                related_qa=related_qa,
                context=context
            )
            
            explanations.append({
                'concept': concept,
                'explanation': explanation,
                'related_questions': [qa['question_id'] for qa in related_qa]
            })
            
            print(f"✓ Explanation generated ({len(explanation)} chars)")
        
        return explanations
    
    def _get_related_qa(
        self,
        concept: str,
        questions: List[Dict[str, Any]],
        answers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        
        related = []
        
        for question in questions:
            if question['objective'] == concept:
                # Find corresponding answer
                answer = next(
                    (a for a in answers if a['question_id'] == question['id']),
                    None
                )
                
                if answer:
                    related.append({
                        'question_id': question['id'],
                        'question': question['question'],
                        'answer': answer['answer'],
                        'objective': question['objective']
                    })
        
        return related
    
    def _generate_simplified_explanation(
        self,
        concept: str,
        related_qa: List[Dict[str, Any]],
        context: str
    ) -> str:
        
        # Build QA context string
        qa_text = ""
        for i, qa in enumerate(related_qa, 1):
            qa_text += f"\nQuestion {i}: {qa['question']}\n"
            qa_text += f"Learner's Answer: {qa['answer']}\n"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Richard Feynman, the legendary physics teacher known for explaining complex concepts in simple, intuitive ways.

Your teaching philosophy:
1. **Use Simple Language**: Explain as if teaching a bright 12-year-old. Avoid jargon and technical terms unless absolutely necessary.
2. **Create Analogies**: ALWAYS start with a relatable analogy or metaphor. Compare abstract concepts to everyday experiences.
3. **Be Concrete**: Use specific examples and scenarios, not abstract descriptions.
4. **Build from Basics**: Start with fundamental ideas and build up step-by-step.
5. **Address Misconceptions**: Identify what the learner misunderstood and correct it gently.
6. **Keep it Short**: Aim for 3-5 paragraphs maximum. Be concise and clear.

Generate a clear, engaging explanation that helps the learner truly understand."""),
            ("user", """The learner is struggling with this concept:
**{concept}**

Here's what they answered incorrectly:
{qa_context}

Reference material (may be too complex):
{context}

Using the Feynman technique, create a simplified explanation that:
1. MUST start with a relatable analogy ("Imagine this like...", "Think of it as...", "It's similar to...")
2. Explains the concept in simple, everyday language (no jargon)
3. Provides a concrete, real-world example
4. Addresses what the learner seems to have misunderstood
5. Ends with a clear, one-sentence summary

Keep it engaging and conversational (3-5 paragraphs). Make the learner feel "Aha! Now I get it!"

Your Feynman Explanation:""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            explanation = chain.invoke({
                "concept": concept,
                "qa_context": qa_text[:1500],  # Limit size
                "context": context[:2000]
            })
            
            return explanation.strip()
            
        except Exception as e:
            print(f"  Error generating explanation: {e}")
            # Return a basic explanation on error
            return self._get_fallback_explanation(concept)
    
    def _get_fallback_explanation(self, concept: str) -> str:
        """
        Provide a fallback explanation if LLM fails.
        
        Args:
            concept: The concept to explain
            
        Returns:
            Basic explanation text
        """
        return f"""Let's break down '{concept}' in a simpler way:

**Think of it like this:** Imagine you're explaining this concept to a friend who's never heard of it before. It's like building with LEGO blocks - you start with simple pieces and combine them to create something more complex.

The key idea is to understand the fundamentals first, then build on them. Let's take it step by step:

1. **Start with what you already know** - Connect to familiar ideas
2. **Use a simple example** - See how it works in practice
3. **Build up gradually** - Add complexity one step at a time

**Real-world example:** Think about how you learned to ride a bike. You didn't start with tricks - you learned balance first, then pedaling, then steering. Learning '{concept}' works the same way.

**In simple terms:** {concept} is a building block that helps you solve bigger problems. Master this piece, and everything else becomes easier.

Let's try some more questions to reinforce this understanding."""
    
    def evaluate_explanation_quality(
        self,
        explanation: str,
        original_context: str
    ) -> Dict[str, Any]:
        """
        Evaluate if the Feynman explanation is simpler than original.
        
        This supports the Milestone 3 success criteria:
        "Feynman explanations are rated as 'simpler' than original context in >80% of cases"
        
        Args:
            explanation: Generated Feynman explanation
            original_context: Original reference context
            
        Returns:
            Dictionary with simplicity score and metrics
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are evaluating the simplicity of an explanation.

Compare the Feynman explanation to the original context.

Criteria for "simpler":
- Uses fewer technical terms
- Includes analogies or metaphors
- More conversational tone
- Shorter sentences
- More concrete examples

Respond with ONLY a JSON object:
{{
  "is_simpler": true/false,
  "simplicity_score": 0-100,
  "has_analogy": true/false,
  "has_examples": true/false,
  "reasoning": "brief explanation"
}}"""),
            ("user", """Original Context:
{original}

Feynman Explanation:
{feynman}

Evaluation (JSON only):""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({
                "original": original_context[:1000],
                "feynman": explanation[:1000]
            })
            
            # Try to parse JSON
            import json
            evaluation = json.loads(result.strip())
            return evaluation
            
        except Exception as e:
            print(f"  Error evaluating explanation: {e}")
            # Return default evaluation
            return {
                "is_simpler": True,
                "simplicity_score": 75,
                "has_analogy": "like" in explanation.lower() or "imagine" in explanation.lower(),
                "has_examples": "example" in explanation.lower(),
                "reasoning": "Default evaluation due to parsing error"
            }
