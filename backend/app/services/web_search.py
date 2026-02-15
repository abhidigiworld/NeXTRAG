"""
Web search service for retrieving information from the web
"""
import requests
from typing import List, Dict
from bs4 import BeautifulSoup
from app.config import settings
from app.utils.logger import logger
import time
from datetime import datetime, timedelta


class WebSearchService:
    """Web search and content extraction"""
    
    def __init__(self):
        self.provider = settings.search_provider
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 3600  # 1 hour
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search the web for a query
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results with URL, title, and snippet
        """
        # Check cache
        cache_key = f"{query}_{num_results}"
        if cache_key in self.cache:
            cached_time, cached_results = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                logger.info(f"Returning cached results for: {query}")
                return cached_results
        
        # Perform search based on provider
        if self.provider == "duckduckgo":
            results = self._search_duckduckgo(query, num_results)
        elif self.provider == "tavily":
            results = self._search_tavily(query, num_results)
        elif self.provider == "serpapi":
            results = self._search_serpapi(query, num_results)
        else:
            raise ValueError(f"Unsupported search provider: {self.provider}")
        
        # Cache results
        self.cache[cache_key] = (time.time(), results)
        
        return results
    
    def _search_duckduckgo(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """Search using DuckDuckGo"""
        try:
            from duckduckgo_search import DDGS
            
            # Perform search
            with DDGS() as ddgs:
                search_results_raw = list(ddgs.text(
                    query,
                    max_results=num_results,
                    backend="html"  # Use HTML backend to avoid rate limits
                ))
                
                results = []
                for result in search_results_raw:
                    results.append({
                        'url': result.get('href', ''),
                        'title': result.get('title', ''),
                        'snippet': result.get('body', '')
                    })
            
            logger.info(f"DuckDuckGo search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {str(e)}")
            return []
    
    def _search_tavily(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """Search using Tavily API"""
        try:
            url = "https://api.tavily.com/search"
            headers = {"Content-Type": "application/json"}
            payload = {
                "api_key": settings.tavily_api_key,
                "query": query,
                "max_results": num_results
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for result in data.get('results', []):
                results.append({
                    'url': result.get('url', ''),
                    'title': result.get('title', ''),
                    'snippet': result.get('content', '')
                })
            
            logger.info(f"Tavily search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Tavily search error: {str(e)}")
            return []
    
    def _search_serpapi(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """Search using SerpAPI"""
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": settings.serpapi_key,
                "num": num_results
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for result in data.get('organic_results', []):
                results.append({
                    'url': result.get('link', ''),
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', '')
                })
            
            logger.info(f"SerpAPI search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"SerpAPI search error: {str(e)}")
            return []
    
    def extract_content_from_url(self, url: str) -> str:
        """
        Extract main content from a URL
        
        Args:
            url: URL to extract content from
            
        Returns:
            Extracted text content
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            logger.info(f"Extracted {len(text)} characters from {url}")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return ""
    
    def rewrite_query(self, query: str) -> str:
        """
        Rewrite user query for better search results
        
        Args:
            query: Original query
            
        Returns:
            Rewritten query
        """
        # Simple query enhancement
        # In production, you might use an LLM for this
        query = query.strip()
        
        # Add context keywords if query is too short
        if len(query.split()) < 3:
            return query
        
        return query


# Global instance
web_search_service = WebSearchService()
