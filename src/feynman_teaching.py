"""
Feynman Teaching Module for Learning Agent System

Implements the Feynman Technique for adaptive concept simplification when learners
struggle to meet the 70% understanding threshold. Identifies knowledge gaps,
generates simplified explanations using analogies and clear language.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from .llm_service import LLMService
from .models import LearningAgentState

logger = logging.getLogger(__name__)

class FeynmanTeacher:
    """Implements Feynman Technique for adaptive teaching."""
    
    def __init__(self):
        """Initialize Feynman Teacher with LLM service."""
        self.llm_service = LLMService()
        self.max_retries = 3
    
    def identify_knowledge_gaps(self, verification_results: List[Dict]) -> List[Dict]:
        """
        Identify knowledge gaps from incorrect/weak answers.
        
        Args:
            verification_results: Results from understanding verification
            
        Returns:
            List of knowledge gaps with details
        """
        knowledge_gaps = []
        
        for result in verification_results:
            score = result.get("score", 0)
            
            # Consider questions with score < 0.7 as knowledge gaps
            if score < 0.7:
                gap = {
                    "question": result.get("question", ""),
                    "user_answer": result.get("learner_answer", ""),
                    "score": score,
                    "feedback": result.get("feedback", ""),
                    "concept": self._extract_concept_from_question(result.get("question", "")),
                    "severity": "high" if score < 0.4 else "medium"
                }
                knowledge_gaps.append(gap)
        
        logger.info(f"🔍 Identified {len(knowledge_gaps)} knowledge gaps")
        return knowledge_gaps
    
    def _extract_concept_from_question(self, question: str) -> str:
        """Extract the main concept being tested from a question."""
        # Simple extraction - could be enhanced with NLP
        # Remove question words
        concept = question.replace("What is", "").replace("Explain", "")
        concept = concept.replace("How does", "").replace("Why", "")
        concept = concept.replace("?", "").strip()
        
        # Take first significant phrase (up to 50 chars)
        if len(concept) > 50:
            concept = concept[:50] + "..."
        
        return concept
    
    async def generate_simplified_explanation(self, gap: Dict, context: str) -> str:
        """
        Generate simplified Feynman-style explanation for a knowledge gap.
        
        Args:
            gap: Knowledge gap details
            context: Original learning context
            
        Returns:
            Simplified explanation with analogies
        """
        concept = gap["concept"]
        question = gap["question"]
        user_answer = gap["user_answer"]
        
        prompt = f"""You are a master teacher using the Feynman Technique to explain complex concepts in simple terms.

CONCEPT TO EXPLAIN: {concept}

ORIGINAL QUESTION: {question}

LEARNER'S ANSWER (which was incorrect/incomplete): {user_answer}

CRITICAL INSTRUCTIONS:
- DO NOT copy or repeat any reference material verbatim
- DO NOT include web search results, URLs, or unrelated content
- Create your OWN simplified explanation from scratch
- Focus ONLY on explaining the concept in the question
- Ignore any irrelevant information in the reference context

Your task is to create a SIMPLIFIED explanation that:
1. Directly answers what {concept} means
2. Uses simple, everyday language (avoid jargon)
3. Includes concrete analogies and examples from everyday life
4. Addresses the specific misunderstanding in the learner's answer
5. Uses storytelling or real-world scenarios

Format:
Start with: "Let me explain {concept}..."
Then provide your explanation in 3-4 short paragraphs.

Rules:
- Explain like you're talking to a 12-year-old
- Use analogies from everyday life (cooking, sports, nature, etc.)
- Keep each sentence short and clear
- Create ORIGINAL content - do not copy from reference material
- 200-300 words maximum

Generate your simplified explanation now:"""

        try:
            # Use LLM service's invoke method
            explanation = await asyncio.to_thread(
                self.llm_service.llm.invoke,
                prompt
            )
            
            # Handle response - it might be a string or object with content
            if hasattr(explanation, 'content'):
                simplified_text = explanation.content.strip()
            elif isinstance(explanation, str):
                simplified_text = explanation.strip()
            else:
                simplified_text = str(explanation).strip()
            
            logger.info(f"✨ Generated simplified explanation for: {concept[:50]}...")
            return simplified_text
            
        except Exception as e:
            logger.error(f"Error generating Feynman explanation: {e}")
            # Return a helpful fallback explanation instead of raw context
            return f"""**Unable to generate AI explanation** (Ollama not available)

**Concept:** {concept}

**What you need to know:**
This concept relates to {question}

**Key points to understand:**
- Review the learning materials for this topic
- Focus on understanding the core principles
- Try breaking down the concept into smaller parts
- Look for examples and analogies that make sense to you

**Next steps:**
1. Review your notes and materials
2. Try explaining the concept in your own words
3. Identify specific parts that are unclear
4. Seek additional resources or examples

*Note: Start Ollama (`ollama serve`) to get AI-generated simplified explanations.*"""
    
    async def generate_all_explanations(self, knowledge_gaps: List[Dict], 
                                       context_chunks: List[str]) -> List[Dict]:
        """
        Generate simplified explanations for all knowledge gaps.
        
        Args:
            knowledge_gaps: List of identified knowledge gaps
            context_chunks: Available context for reference
            
        Returns:
            List of gaps with added simplified explanations
        """
        # Extract text from context chunks (they are dicts with 'text' field)
        context_texts = []
        for chunk in context_chunks[:5]:
            if isinstance(chunk, dict):
                context_texts.append(chunk.get('text', ''))
            else:
                context_texts.append(str(chunk))
        context = "\n".join(context_texts)
        
        explanations = []
        
        for i, gap in enumerate(knowledge_gaps, 1):
            logger.info(f"📚 Generating explanation {i}/{len(knowledge_gaps)}...")
            
            simplified = await self.generate_simplified_explanation(gap, context)
            
            gap_with_explanation = {
                **gap,
                "simplified_explanation": simplified
            }
            
            explanations.append(gap_with_explanation)
        
        return explanations
    
    def display_feynman_teaching(self, explanations: List[Dict]) -> None:
        """
        Display Feynman teaching explanations to the user.
        
        Args:
            explanations: List of gaps with simplified explanations
        """
        print("\n" + "📚"*35)
        print("FEYNMAN TECHNIQUE - SIMPLIFIED LEARNING")
        print("📚"*35)
        
        print("\n💡 Don't worry! Let's break down these concepts in simpler terms.")
        print("I'll explain using everyday analogies and clear language.\n")
        
        for i, exp in enumerate(explanations, 1):
            print("\n" + "="*70)
            print(f"📖 CONCEPT {i}: {exp['concept']}")
            print("="*70)
            
            print(f"\n❌ Your Understanding Gap (Score: {exp['score']*100:.0f}%):")
            print(f"   Question: {exp['question']}")
            print(f"   Your Answer: {exp['user_answer'][:100]}...")
            
            print(f"\n✨ SIMPLIFIED EXPLANATION:\n")
            print(exp['simplified_explanation'])
            
            print("\n" + "-"*70)
        
        print("\n" + "="*70)
        print(f"✅ Reviewed {len(explanations)} concepts in simple terms")
        print("="*70)
        
        print("\n💭 Take a moment to think about these explanations...")
        print("When you're ready, we'll test your understanding again.\n")
    
    async def apply_feynman_technique(self, state: LearningAgentState) -> Tuple[bool, LearningAgentState]:
        """
        Apply complete Feynman Technique workflow.
        
        Args:
            state: Current learning agent state
            
        Returns:
            Tuple of (should_retry, updated_state)
        """
        logger.info("📚 Applying Feynman Technique...")
        
        try:
            # Get retry count
            retry_count = state.get("feynman_retry_count", 0)
            
            if retry_count >= self.max_retries:
                logger.info(f"⚠️ Maximum retries ({self.max_retries}) reached")
                print(f"\n⚠️ You've attempted this checkpoint {retry_count} times.")
                print("Consider reviewing the materials again before continuing.")
                return False, state
            
            # Identify knowledge gaps
            verification_results = state.get("verification_results", [])
            knowledge_gaps = self.identify_knowledge_gaps(verification_results)
            
            if not knowledge_gaps:
                logger.info("✅ No significant knowledge gaps found")
                return False, state
            
            # Generate simplified explanations
            context_chunks = state.get("processed_context", [])
            explanations = await self.generate_all_explanations(knowledge_gaps, context_chunks)
            
            # Display to user
            self.display_feynman_teaching(explanations)
            
            # Store in state
            state["feynman_explanations"] = explanations
            state["feynman_retry_count"] = retry_count + 1
            
            # Ask user if they want to retry
            from .user_interaction import ask_retry_confirmation
            should_retry = ask_retry_confirmation()
            
            logger.info(f"🔄 User wants to retry: {should_retry}")
            
            return should_retry, state
            
        except Exception as e:
            logger.error(f"Error in Feynman technique: {e}")
            return False, state

# Global instance
_feynman_teacher = None

def get_feynman_teacher() -> FeynmanTeacher:
    """Get or create global Feynman Teacher instance."""
    global _feynman_teacher
    if _feynman_teacher is None:
        _feynman_teacher = FeynmanTeacher()
    return _feynman_teacher
