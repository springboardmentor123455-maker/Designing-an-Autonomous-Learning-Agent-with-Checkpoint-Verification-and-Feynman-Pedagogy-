"""Search tools for gathering learning content."""
import os
from typing import List, Dict, Any

# Try to import search libraries
try:
    from googlesearch import search as google_search
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False

try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False


class SerpAPISearch:
    """Wrapper for SerpAPI Google search."""
    
    def __init__(self):
        """Initialize SerpAPI search."""
        api_key = os.getenv("SERP_API_KEY")
        if not api_key:
            raise ValueError("SERP_API_KEY not found in environment")
        
        try:
            from serpapi import GoogleSearch
            self.GoogleSearch = GoogleSearch
            self.api_key = api_key
        except ImportError:
            raise ImportError(
                "google-search-results not installed. Install it with: pip install google-search-results"
            )
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search using SerpAPI.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, link, and snippet
        """
        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": max_results,
                "engine": "google"
            }
            
            search = self.GoogleSearch(params)
            results = search.get_dict()
            
            organic_results = results.get("organic_results", [])
            
            formatted_results = []
            for result in organic_results[:max_results]:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"SerpAPI search error: {e}")
            return []


class DuckDuckGoSearch:
    """Wrapper for DuckDuckGo search (free, no API key needed)."""
    
    def __init__(self):
        """Initialize DuckDuckGo search."""
        if not DUCKDUCKGO_AVAILABLE:
            raise ImportError(
                "duckduckgo-search not installed. Install it with: pip install duckduckgo-search"
            )
        self.ddgs = DDGS()
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search using DuckDuckGo.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, link, and snippet
        """
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", "")
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []


def search_for_learning_content(
    topic: str,
    objectives: List[str],
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for learning content using multiple diverse queries.
    
    Uses 3 different query formulations to get diverse results:
    1. "{topic} tutorial guide"
    2. "{topic} explained with examples"
    3. "{topic} {first_objective}"
    
    Args:
        topic: The learning topic
        objectives: List of learning objectives
        max_results: Maximum total results to return
        
    Returns:
        List of search results with title, url, and snippet
    """
    # Create 3 diverse queries
    queries = [
        f"{topic} tutorial guide",
        f"{topic} explained with examples",
        f"{topic} {objectives[0] if objectives else 'basics'}",
    ]
    
    # Try SerpAPI first (best quality, 100 free searches/month)
    try:
        search_tool = SerpAPISearch()
        print("Using SerpAPI search (recommended)")
    except (ValueError, ImportError) as e:
        print(f"SerpAPI not available: {e}")
        # Fallback to DuckDuckGo (free, unlimited)
        try:
            search_tool = DuckDuckGoSearch()
            print("Using DuckDuckGo search (free fallback)")
        except ImportError:
            print("No search tools available. Install serpapi or duckduckgo-search")
            return []
    
    all_results = []
    seen_urls = set()
    
    # Execute all queries and collect unique results
    for query in queries:
        print(f"Searching for: {query}")
        results = search_tool.search(query, max_results=max(2, max_results // len(queries)))
        
        # Add unique results only
        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_results.append(result)
                
                if len(all_results) >= max_results:
                    break
        
        if len(all_results) >= max_results:
            break
    
    print(f"Found {len(all_results)} unique results")
    return all_results[:max_results]
