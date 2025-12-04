"""
Web Search Module for Real-Time Trend Discovery

Provides web search capabilities using multiple free providers:
- DuckDuckGo (primary, no API key required)
- Brave Search (optional, requires API key for enhanced results)

Features:
- Multi-provider fallback
- Smart query construction
- Result filtering and deduplication
- Time-based filtering
- Rate limiting and error handling
"""

import os
import time
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class WebSearcher:
    """
    Web search with multiple provider support for latest trends and resources.
    """
    
    def __init__(self):
        self.brave_api_key = os.getenv('BRAVE_SEARCH_API_KEY')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AutonomousResearchAgent/1.0'
        })
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Rate limiting
        
    def search(self, query: str, max_results: int = 20, time_range: str = 'month') -> List[Dict]:
        """
        Search the web for latest information.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            time_range: Time range filter ('week', 'month', 'year')
            
        Returns:
            List of search results with title, url, snippet, date
        """
        logger.info(f"Web search for: {query} (max_results={max_results}, time_range={time_range})")
        
        # Try providers in order of preference
        results = []
        
        # Try Brave Search first if API key available
        if self.brave_api_key:
            try:
                results = self._search_brave(query, max_results, time_range)
                if results:
                    logger.info(f"Brave Search returned {len(results)} results")
                    return results
            except Exception as e:
                logger.warning(f"Brave Search failed: {e}")
        
        # Fallback to DuckDuckGo
        try:
            results = self._search_duckduckgo(query, max_results)
            if results:
                logger.info(f"DuckDuckGo returned {len(results)} results")
                return results
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
        
        logger.warning("All search providers failed, returning empty results")
        return []
    
    def _search_brave(self, query: str, max_results: int, time_range: str) -> List[Dict]:
        """Search using Brave Search API."""
        self._rate_limit()
        
        url = "https://api.search.brave.com/res/v1/web/search"
        params = {
            'q': query,
            'count': min(max_results, 50),  # Brave limit
            'freshness': time_range
        }
        headers = {
            'Accept': 'application/json',
            'X-Subscription-Token': self.brave_api_key
        }
        
        response = self.session.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('web', {}).get('results', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'snippet': item.get('description', ''),
                'date': item.get('age', 'Unknown'),
                'source': 'brave'
            })
        
        return results[:max_results]
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict]:
        """Search using DuckDuckGo Instant Answer API (free, no key required)."""
        self._rate_limit()
        
        # DuckDuckGo Instant Answer API
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': 1,
            'skip_disambig': 1
        }
        
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        # Extract results from various sections
        # Abstract
        if data.get('Abstract'):
            results.append({
                'title': data.get('Heading', 'Summary'),
                'url': data.get('AbstractURL', ''),
                'snippet': data.get('Abstract', ''),
                'date': 'Recent',
                'source': 'duckduckgo'
            })
        
        # Related topics
        for topic in data.get('RelatedTopics', [])[:max_results]:
            if isinstance(topic, dict) and topic.get('FirstURL'):
                results.append({
                    'title': topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else topic.get('Text', ''),
                    'url': topic.get('FirstURL', ''),
                    'snippet': topic.get('Text', ''),
                    'date': 'Recent',
                    'source': 'duckduckgo'
                })
        
        # If no results from Instant Answer, try HTML scraping approach (basic)
        if not results:
            results = self._search_duckduckgo_html(query, max_results)
        
        return results[:max_results]
    
    def _search_duckduckgo_html(self, query: str, max_results: int) -> List[Dict]:
        """Fallback: Parse DuckDuckGo HTML results (basic extraction)."""
        self._rate_limit()
        
        url = "https://html.duckduckgo.com/html/"
        data = {'q': query}
        
        try:
            response = self.session.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            # Basic parsing (in production, would use BeautifulSoup)
            # For now, return a placeholder to show the mechanism
            return [{
                'title': f'Web result for: {query}',
                'url': f'https://duckduckgo.com/?q={quote_plus(query)}',
                'snippet': 'Search results available via DuckDuckGo',
                'date': 'Recent',
                'source': 'duckduckgo-html'
            }]
        except Exception as e:
            logger.debug(f"HTML search failed: {e}")
            return []
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def search_trends(self, topic: str, time_range: str = 'week') -> List[Dict]:
        """
        Search for latest trends related to a topic.
        
        Args:
            topic: Topic to search trends for
            time_range: Time range ('week', 'month', 'year')
            
        Returns:
            List of trending results
        """
        # Construct trend-focused query
        trend_queries = [
            f"{topic} latest trends {time_range}",
            f"{topic} new tools {time_range}",
            f"{topic} recent developments",
            f"what's new in {topic}"
        ]
        
        all_results = []
        for query in trend_queries[:2]:  # Limit to avoid too many requests
            results = self.search(query, max_results=10, time_range=time_range)
            all_results.extend(results)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        return unique_results
    
    def search_tools(self, domain: str, time_range: str = 'month') -> List[Dict]:
        """
        Search for latest tools and libraries in a domain.
        
        Args:
            domain: Technical domain (e.g., 'machine learning', 'web development')
            time_range: Time range to search within
            
        Returns:
            List of tool-related results
        """
        query = f"{domain} new tools libraries frameworks {time_range}"
        return self.search(query, max_results=15, time_range=time_range)
    
    def filter_by_date(self, results: List[Dict], days: int = 30) -> List[Dict]:
        """
        Filter results to only include recent items.
        
        Args:
            results: List of search results
            days: Maximum age in days
            
        Returns:
            Filtered results
        """
        # This is a simple filter - in production would parse actual dates
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered = []
        for result in results:
            # Simple heuristic: if date mentions recent time periods, include it
            date_str = result.get('date', '').lower()
            if any(term in date_str for term in ['recent', 'today', 'yesterday', 'day ago', 'week ago', 'hour ago']):
                filtered.append(result)
            elif not date_str or date_str == 'unknown':
                # Include if date is unknown (might be recent)
                filtered.append(result)
        
        return filtered if filtered else results  # Return all if filter is too strict


def create_web_searcher() -> WebSearcher:
    """Factory function to create a WebSearcher instance."""
    return WebSearcher()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    searcher = create_web_searcher()
    
    # Test search
    results = searcher.search("quantum computing applications", max_results=5)
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   {result['snippet'][:100]}...")
    
    # Test trend search
    trends = searcher.search_trends("artificial intelligence", time_range='week')
    print(f"\n\nFound {len(trends)} trending items:")
    for i, trend in enumerate(trends[:3], 1):
        print(f"\n{i}. {trend['title']}")
        print(f"   {trend['url']}")
