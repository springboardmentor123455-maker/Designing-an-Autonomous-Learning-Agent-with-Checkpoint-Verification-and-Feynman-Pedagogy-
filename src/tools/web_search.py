"""
Web search integration for dynamic context retrieval.
Uses DuckDuckGo search API to find relevant educational content.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from requests.sessions import Session
try:
    from ddgs import DDGS
except ImportError:
    # Fallback for old package name
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None
from langchain_core.documents import Document
from src.models import ContextSource
from config.settings import settings

logger = logging.getLogger(__name__)


class SearchResult:
    """Represents a single search result."""
    
    def __init__(self, title: str, url: str, snippet: str, source: str = "web"):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source
        self.timestamp = datetime.now()
    
    def to_context_source(self, relevance_score: Optional[float] = None) -> ContextSource:
        """Convert to ContextSource for the learning system."""
        content = f"Title: {self.title}\n\nContent: {self.snippet}"
        
        metadata = {
            "url": self.url,
            "title": self.title,
            "search_source": self.source,
            "timestamp": self.timestamp.isoformat()
        }
        
        return ContextSource(
            source_type="web_search",
            content=content,
            metadata=metadata,
            relevance_score=relevance_score
        )


class WebSearchService:
    """Service for performing web searches and retrieving content."""
    
    def __init__(self):
        self.max_results = settings.max_search_results
        if DDGS is None:
            raise ImportError("DuckDuckGo search not available. Install with: pip install ddgs")
        self.ddgs = DDGS()
        self._session = None
    
    @property
    def session(self) -> Session:
        """Get or create a requests session."""
        if self._session is None:
            self._session = requests.Session()
        return self._session
    
    def close(self):
        """Close the requests session."""
        if self._session:
            self._session.close()
            self._session = None
    
    async def search_educational_content(
        self,
        queries: List[str],
        max_results_per_query: Optional[int] = None
    ) -> List[SearchResult]:
        """Search for educational content using multiple queries."""
        max_results = max_results_per_query or self.max_results
        all_results = []
        
        for query in queries:
            try:
                logger.info(f"Searching for: {query}")
                results = await self._search_duckduckgo(query, max_results)
                all_results.extend(results)
                
                # Add small delay to be respectful to the API
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Search failed for query '{query}': {e}")
                continue
        
        # Remove duplicates based on URL
        unique_results = self._deduplicate_results(all_results)
        
        logger.info(f"Found {len(unique_results)} unique search results")
        return unique_results
    
    async def _search_duckduckgo(self, query: str, max_results: int) -> List[SearchResult]:
        """Perform a DuckDuckGo search."""
        results = []
        
        try:
            # Add educational keywords to improve result quality
            enhanced_query = f"{query} tutorial explanation guide"
            
            # Perform the search
            search_results = self.ddgs.text(
                enhanced_query,
                max_results=max_results,
                region='us-en',
                safesearch='moderate'
            )
            
            for result in search_results:
                search_result = SearchResult(
                    title=result.get('title', ''),
                    url=result.get('href', ''),
                    snippet=result.get('body', ''),
                    source='duckduckgo'
                )
                results.append(search_result)
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            raise
        
        return results
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results based on URL."""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        return unique_results
    
    async def get_page_content(self, url: str, max_length: int = 3000) -> Optional[str]:
        """Attempt to retrieve full content from a webpage."""
        try:
            # Simple HTTP request to get page content
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Basic text extraction (could be enhanced with BeautifulSoup)
            content = response.text
            
            # Simple cleanup - remove HTML tags (basic)
            import re
            content = re.sub(r'<[^>]+>', ' ', content)
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Truncate if too long
            if len(content) > max_length:
                content = content[:max_length] + "..."
            
            return content
            
        except Exception as e:
            logger.warning(f"Failed to get content from {url}: {e}")
            return None
    
    async def search_and_enhance_content(
        self,
        queries: List[str],
        enhance_with_full_content: bool = False
    ) -> List[ContextSource]:
        """Search and optionally enhance results with full page content."""
        search_results = await self.search_educational_content(queries)
        context_sources = []
        
        for result in search_results:
            content = result.snippet
            
            # Optionally try to get full page content
            if enhance_with_full_content:
                full_content = await self.get_page_content(result.url)
                if full_content and len(full_content) > len(result.snippet):
                    content = full_content
                    result.snippet = content  # Update the snippet
            
            # Create context source
            context_source = result.to_context_source()
            context_sources.append(context_source)
        
        return context_sources


class ContextGatherer:
    """High-level service for gathering context from multiple sources."""
    
    def __init__(self):
        self.web_search = WebSearchService()    
    def close(self):
        """Close all connections and cleanup resources."""
        if self.web_search:
            self.web_search.close()    
    async def gather_context_for_checkpoint(
        self,
        checkpoint_title: str,
        objectives: List[str],
        user_notes: Optional[str] = None,
        prioritize_user_notes: bool = True
    ) -> List[ContextSource]:
        """Gather context from user notes and web search."""
        context_sources = []
        
        # 1. Add user notes if provided
        if user_notes and user_notes.strip():
            user_context = ContextSource(
                source_type="user_notes",
                content=user_notes,
                metadata={"provided_by": "user", "length": len(user_notes)}
            )
            context_sources.append(user_context)
            logger.info("Added user notes as context source")
        
        # 2. Generate search queries
        from src.tools.llm_integration import llm_service
        try:
            search_queries = await llm_service.generate_search_queries(
                checkpoint_title, objectives, max_queries=3
            )
        except Exception as e:
            logger.warning(f"LLM query generation failed, using fallback: {e}")
            search_queries = [
                f"{checkpoint_title} tutorial",
                f"{checkpoint_title} explanation", 
                f"learn {checkpoint_title}"
            ]
        
        # 3. Perform web search
        try:
            web_sources = await self.web_search.search_and_enhance_content(
                search_queries, enhance_with_full_content=False
            )
            context_sources.extend(web_sources)
            logger.info(f"Added {len(web_sources)} web search sources")
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
        
        return context_sources
    
    async def validate_and_score_context(
        self,
        context_sources: List[ContextSource],
        checkpoint_objectives: List[str]
    ) -> List[ContextSource]:
        """Validate context sources and assign relevance scores."""
        from src.tools.llm_integration import llm_service
        
        for source in context_sources:
            try:
                # Skip validation for user notes (assume they're relevant)
                if source.source_type == "user_notes":
                    source.relevance_score = 5.0
                    continue
                
                # Validate web search content
                validation_result = await llm_service.validate_context_relevance(
                    source.content, checkpoint_objectives
                )
                
                source.relevance_score = validation_result["score"]
                
                # Add validation metadata
                source.metadata.update({
                    "validation_reasoning": validation_result["reasoning"],
                    "validation_suggestions": validation_result["suggestions"]
                })
                
            except Exception as e:
                logger.warning(f"Context validation failed for source: {e}")
                source.relevance_score = 2.0  # Default modest score
        
        return context_sources
    
    async def filter_high_quality_context(
        self,
        context_sources: List[ContextSource],
        min_relevance: float = None
    ) -> List[ContextSource]:
        """Filter context sources based on relevance score."""
        min_score = min_relevance or settings.relevance_threshold
        
        high_quality_sources = [
            source for source in context_sources
            if source.relevance_score and source.relevance_score >= min_score
        ]
        
        logger.info(f"Filtered to {len(high_quality_sources)} high-quality sources "
                   f"(min score: {min_score})")
        
        return high_quality_sources


# Global context gatherer instance
context_gatherer = ContextGatherer()