"""
Dynamic Materials Generation for Learning Agent System

Generates learning materials dynamically using LLM and web search for custom topics.
No hardcoded materials required - all content is generated on-demand.
"""

import logging
from typing import List, Dict, Optional
from .llm_service import LLMService
from .web_search import get_web_search_service
from .models import Checkpoint

logger = logging.getLogger(__name__)

class DynamicMaterialsGenerator:
    """Generate learning materials dynamically for any topic."""
    
    def __init__(self):
        """Initialize materials generator."""
        self.llm_service = LLMService()
        self.web_search = get_web_search_service()
    
    async def generate_materials_from_llm(self, checkpoint: Checkpoint) -> List[Dict]:
        """
        Generate educational materials using LLM.
        
        Args:
            checkpoint: Learning checkpoint with topic and requirements
            
        Returns:
            List of generated materials
        """
        logger.info(f"🤖 Generating LLM-based materials for: {checkpoint['title']}")
        
        prompt = f"""You are an expert educator creating comprehensive learning materials IN ENGLISH.

TOPIC: {checkpoint['title']}
DESCRIPTION: {checkpoint['description']}

LEARNING REQUIREMENTS:
{chr(10).join(f"- {req}" for req in checkpoint['requirements'])}

Generate comprehensive educational content IN ENGLISH LANGUAGE ONLY that covers all requirements. Include:
1. Core concepts and definitions
2. Key principles and how they work
3. Practical examples and use cases
4. Common patterns and best practices
5. Important considerations and gotchas

IMPORTANT: Write ONLY in English. Use clear, simple English language.

Format the content in clear, structured paragraphs. Aim for 500-800 words of high-quality educational content.

EDUCATIONAL CONTENT:"""

        try:
            response = await self.llm_service.ollama_client.chat(
                model=self.llm_service.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response["message"]["content"].strip()
            
            material = {
                "id": f"llm_generated_{checkpoint['id']}",
                "title": f"{checkpoint['title']} - Comprehensive Guide",
                "content": content,
                "source": "AI-Generated Educational Content",
                "type": "llm_generated"
            }
            
            logger.info(f"✅ Generated {len(content)} characters of LLM content")
            return [material]
            
        except Exception as e:
            logger.error(f"❌ Error generating LLM materials: {e}")
            return []
    
    async def generate_materials_from_web(self, checkpoint: Checkpoint) -> List[Dict]:
        """
        Generate materials by searching the web.
        
        Args:
            checkpoint: Learning checkpoint
            
        Returns:
            List of materials from web search
        """
        logger.info(f"🔍 Searching web for materials: {checkpoint['title']}")
        
        try:
            materials = await self.web_search.gather_learning_materials(checkpoint)
            
            if materials:
                logger.info(f"✅ Found {len(materials)} materials from web")
            else:
                logger.warning("⚠️ No web materials found")
            
            return materials
            
        except Exception as e:
            logger.error(f"❌ Error gathering web materials: {e}")
            return []
    
    async def generate_comprehensive_materials(self, checkpoint: Checkpoint, 
                                              use_web: bool = True,
                                              use_llm: bool = True) -> List[Dict]:
        """
        Generate comprehensive materials using multiple sources.
        
        Args:
            checkpoint: Learning checkpoint
            use_web: Whether to use web search
            use_llm: Whether to use LLM generation
            
        Returns:
            Combined list of materials from all sources
        """
        logger.info(f"📚 Generating comprehensive materials for: {checkpoint['title']}")
        
        all_materials = []
        
        # Strategy 1: LLM-generated comprehensive content (always high quality)
        if use_llm:
            llm_materials = await self.generate_materials_from_llm(checkpoint)
            all_materials.extend(llm_materials)
        
        # Strategy 2: Web search for diverse perspectives
        if use_web:
            web_materials = await self.generate_materials_from_web(checkpoint)
            all_materials.extend(web_materials)
        
        if not all_materials:
            logger.warning("⚠️ No materials generated, creating minimal fallback")
            # Create minimal fallback material
            all_materials.append({
                "id": f"fallback_{checkpoint['id']}",
                "title": checkpoint['title'],
                "content": f"Learn about {checkpoint['title']}. {checkpoint['description']}",
                "source": "Checkpoint Description",
                "type": "fallback"
            })
        
        logger.info(f"✅ Generated {len(all_materials)} total materials")
        return all_materials
    
    async def enhance_user_materials(self, user_materials: List[Dict], 
                                    checkpoint: Checkpoint) -> List[Dict]:
        """
        Enhance user-provided materials with generated content.
        
        Args:
            user_materials: Materials uploaded by user
            checkpoint: Current checkpoint
            
        Returns:
            Combined user and generated materials
        """
        logger.info(f"🎯 Enhancing {len(user_materials)} user materials")
        
        # If user materials are sufficient, just add LLM summary
        if sum(len(m.get('content', '')) for m in user_materials) > 1000:
            logger.info("✅ User materials are comprehensive, adding LLM summary only")
            llm_materials = await self.generate_materials_from_llm(checkpoint)
            return user_materials + llm_materials
        
        # If user materials are limited, add web search
        else:
            logger.info("⚠️ User materials limited, adding web search")
            web_materials = await self.generate_materials_from_web(checkpoint)
            return user_materials + web_materials

# Global instance
_materials_generator = None

def get_materials_generator() -> DynamicMaterialsGenerator:
    """Get or create global materials generator instance."""
    global _materials_generator
    if _materials_generator is None:
        _materials_generator = DynamicMaterialsGenerator()
    return _materials_generator
