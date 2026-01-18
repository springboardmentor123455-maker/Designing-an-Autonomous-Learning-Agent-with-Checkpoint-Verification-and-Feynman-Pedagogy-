"""
Web Search Integration for Learning Agent System

Provides dynamic content retrieval using DuckDuckGo search to gather learning materials
based on checkpoint topics and requirements.
"""

import logging
from typing import List, Dict, Optional
import asyncio

logger = logging.getLogger(__name__)

class WebSearchService:
    """Service for searching and retrieving web content."""
    
    def __init__(self):
        """Initialize web search service."""
        self.search_available = False
        self._init_search_client()
    
    def _init_search_client(self):
        """Initialize search client (DuckDuckGo)."""
        try:
            from duckduckgo_search import DDGS
            self.ddgs = DDGS()
            self.search_available = True
            logger.info("✅ DuckDuckGo search initialized")
        except ImportError:
            logger.warning("⚠️ duckduckgo-search not installed. Install with: pip install duckduckgo-search")
            logger.warning("Web search features will be disabled")
            self.ddgs = None
    
    def generate_search_queries(self, checkpoint: Dict, max_queries: int = 3) -> List[str]:
        """
        Generate search queries based on checkpoint content.
        
        Args:
            checkpoint: Learning checkpoint details
            max_queries: Maximum number of queries to generate
            
        Returns:
            List of search query strings
        """
        queries = []
        
        # Primary query: topic title
        queries.append(f"{checkpoint['title']} tutorial")
        
        # Secondary query: topic + "explained"
        queries.append(f"{checkpoint['title']} explained for beginners")
        
        # Tertiary query: from requirements
        if checkpoint.get('requirements'):
            first_req = checkpoint['requirements'][0][:60]  # First requirement, truncated
            queries.append(f"{first_req}")
        
        return queries[:max_queries]
    
    async def search_web(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search the web for relevant content.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, url, and snippet
        """
        if not self.search_available or not self.ddgs:
            logger.warning(f"⚠️ Web search not available. Skipping search for: {query}")
            return []
        
        try:
            logger.info(f"🔍 Searching web for: {query}")
            
            # Execute search in thread pool (DDGS is synchronous)
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: list(self.ddgs.text(query, max_results=max_results))
            )
            
            # Format results
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "title": r.get("title", ""),
                    "url": r.get("link", ""),
                    "snippet": r.get("body", ""),
                    "source": "DuckDuckGo"
                })
            
            logger.info(f"✅ Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error searching web: {e}")
            return []
    
    async def gather_learning_materials(self, checkpoint: Dict) -> List[Dict[str, str]]:
        """
        Gather learning materials from web search for a checkpoint.
        
        Args:
            checkpoint: Learning checkpoint details
            
        Returns:
            List of materials with content from web search
        """
        if not self.search_available:
            logger.warning("⚠️ Web search unavailable, returning empty materials")
            return []
        
        # Generate search queries
        queries = self.generate_search_queries(checkpoint)
        logger.info(f"📋 Generated {len(queries)} search queries")
        
        # Search for each query
        all_results = []
        for query in queries:
            results = await self.search_web(query, max_results=3)
            all_results.extend(results)
        
        # Convert to materials format
        materials = []
        for i, result in enumerate(all_results, 1):
            material = {
                "id": f"web_search_{i}",
                "title": result["title"],
                "content": result["snippet"],
                "source": f"{result['source']} - {result['url']}",
                "url": result["url"],
                "type": "web_search"
            }
            materials.append(material)
        
        logger.info(f"📚 Gathered {len(materials)} materials from web search")
        return materials

# Global instance
_web_search_service = None

def get_web_search_service() -> WebSearchService:
    """Get or create global web search service instance."""
    global _web_search_service
    if _web_search_service is None:
        _web_search_service = WebSearchService()
    return _web_search_service
