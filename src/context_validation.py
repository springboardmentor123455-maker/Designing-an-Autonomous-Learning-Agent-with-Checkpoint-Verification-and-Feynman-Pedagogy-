"""
Context Validation and Relevance Scoring Module

Validates that gathered learning materials adequately cover checkpoint objectives
using LLM-based relevance scoring (1-5 scale). Implements retry mechanism if 
average relevance score is below 4/5.
"""

import logging
from typing import List, Dict, Tuple
from .llm_service import LLMService
from .models import Checkpoint

logger = logging.getLogger(__name__)

class ContextValidator:
    """Validate relevance of learning materials to checkpoint objectives."""
    
    def __init__(self):
        """Initialize context validator."""
        self.llm_service = LLMService()
        self.relevance_threshold = 4.0  # Average score must be >= 4/5
        self.max_retries = 2
    
    async def score_material_relevance(self, material: Dict, checkpoint: Checkpoint) -> Dict:
        """
        Score a single material's relevance to checkpoint objectives.
        
        Args:
            material: Learning material to score
            checkpoint: Target checkpoint with objectives
            
        Returns:
            Scoring result with 1-5 score and reasoning
        """
        prompt = f"""You are an expert educational content evaluator. Rate how well this learning material covers the checkpoint objectives.

CHECKPOINT: {checkpoint['title']}
DESCRIPTION: {checkpoint['description']}

LEARNING OBJECTIVES:
{chr(10).join(f"- {req}" for req in checkpoint['requirements'])}

MATERIAL TO EVALUATE:
Title: {material.get('title', 'N/A')}
Content: {material.get('content', '')[:1000]}...

EVALUATION CRITERIA:
- Does it cover the core topic?
- Does it address the learning objectives?
- Is the content depth appropriate?
- Is it clear and understandable?

Rate the material on a scale of 1-5:
1 = Not relevant at all, completely off-topic
2 = Minimally relevant, touches on topic but lacks substance
3 = Moderately relevant, covers topic but misses key objectives
4 = Highly relevant, covers most objectives well
5 = Perfectly relevant, comprehensively covers all objectives

Provide your rating and brief reasoning.

Format your response EXACTLY as:
SCORE: [1-5]
REASONING: [Your explanation]"""

        try:
            response = await self.llm_service.ollama_client.chat(
                model=self.llm_service.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response["message"]["content"].strip()
            
            # Parse score
            score = 3  # Default
            reasoning = content
            
            if "SCORE:" in content:
                try:
                    score_line = [line for line in content.split('\n') if 'SCORE:' in line][0]
                    score_str = score_line.split('SCORE:')[1].strip()
                    score = float(score_str.split()[0])  # Get first number
                    score = max(1, min(5, score))  # Clamp to 1-5
                except:
                    pass
            
            if "REASONING:" in content:
                try:
                    reasoning = content.split('REASONING:')[1].strip()
                except:
                    pass
            
            return {
                "material_id": material.get('id', 'unknown'),
                "material_title": material.get('title', 'N/A'),
                "score": score,
                "reasoning": reasoning,
                "raw_response": content
            }
            
        except Exception as e:
            logger.error(f"❌ Error scoring material relevance: {e}")
            return {
                "material_id": material.get('id', 'unknown'),
                "material_title": material.get('title', 'N/A'),
                "score": 3.0,
                "reasoning": f"Error during scoring: {e}",
                "raw_response": ""
            }
    
    async def validate_materials(self, materials: List[Dict], 
                                checkpoint: Checkpoint) -> Dict:
        """
        Validate all materials and calculate average relevance score.
        
        Args:
            materials: List of learning materials
            checkpoint: Target checkpoint
            
        Returns:
            Validation result with scores and pass/fail status
        """
        logger.info(f"🔍 Validating {len(materials)} materials for relevance...")
        
        if not materials:
            return {
                "valid": False,
                "average_score": 0.0,
                "individual_scores": [],
                "message": "No materials to validate"
            }
        
        # Score each material
        individual_scores = []
        for i, material in enumerate(materials, 1):
            logger.info(f"  Scoring material {i}/{len(materials)}...")
            score_result = await self.score_material_relevance(material, checkpoint)
            individual_scores.append(score_result)
            logger.info(f"    Score: {score_result['score']}/5 - {score_result['material_title'][:50]}")
        
        # Calculate average
        avg_score = sum(s['score'] for s in individual_scores) / len(individual_scores)
        
        # Determine if validation passed
        passed = avg_score >= self.relevance_threshold
        
        result = {
            "valid": passed,
            "average_score": avg_score,
            "threshold": self.relevance_threshold,
            "individual_scores": individual_scores,
            "total_materials": len(materials),
            "message": self._get_validation_message(avg_score, passed)
        }
        
        logger.info(f"📊 Average relevance score: {avg_score:.2f}/5.0 (threshold: {self.relevance_threshold})")
        logger.info(f"{'✅ PASSED' if passed else '❌ FAILED'} - {result['message']}")
        
        return result
    
    def _get_validation_message(self, score: float, passed: bool) -> str:
        """Generate validation message based on score."""
        if passed:
            if score >= 4.5:
                return "Excellent! Materials are highly relevant and comprehensive."
            else:
                return "Good! Materials meet relevance requirements."
        else:
            if score >= 3.5:
                return "Materials are moderately relevant but need improvement."
            elif score >= 2.5:
                return "Materials are minimally relevant. Gathering additional resources."
            else:
                return "Materials are not sufficiently relevant. Re-gathering content."
    
    async def validate_with_retry(self, materials: List[Dict], 
                                  checkpoint: Checkpoint,
                                  retry_callback=None) -> Tuple[bool, Dict, List[Dict]]:
        """
        Validate materials with automatic retry if relevance is too low.
        
        Args:
            materials: Initial materials to validate
            checkpoint: Target checkpoint
            retry_callback: Async function to call for gathering new materials
            
        Returns:
            Tuple of (success, validation_result, final_materials)
        """
        attempt = 0
        current_materials = materials
        
        while attempt <= self.max_retries:
            logger.info(f"🔍 Validation attempt {attempt + 1}/{self.max_retries + 1}")
            
            # Validate current materials
            validation = await self.validate_materials(current_materials, checkpoint)
            
            if validation['valid']:
                logger.info(f"✅ Validation passed on attempt {attempt + 1}")
                return True, validation, current_materials
            
            # If not valid and we can retry
            if attempt < self.max_retries and retry_callback:
                logger.info(f"🔄 Relevance too low ({validation['average_score']:.2f}/5), retrying...")
                
                # Call retry callback to gather new materials
                try:
                    new_materials = await retry_callback(checkpoint)
                    if new_materials:
                        # Combine with existing materials
                        current_materials = current_materials + new_materials
                        logger.info(f"📚 Added {len(new_materials)} new materials, total now: {len(current_materials)}")
                    else:
                        logger.warning("⚠️ Retry callback returned no new materials")
                        break
                except Exception as e:
                    logger.error(f"❌ Error in retry callback: {e}")
                    break
            else:
                logger.warning(f"❌ Validation failed after {attempt + 1} attempts")
                break
            
            attempt += 1
        
        # Return final result even if failed
        final_validation = await self.validate_materials(current_materials, checkpoint)
        return False, final_validation, current_materials

# Global instance
_context_validator = None

def get_context_validator() -> ContextValidator:
    """Get or create global context validator instance."""
    global _context_validator
    if _context_validator is None:
        _context_validator = ContextValidator()
    return _context_validator
