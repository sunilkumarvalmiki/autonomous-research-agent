"""
Data scraper module for collecting research information from multiple sources.
Supports arXiv, GitHub, HackerNews, Reddit, Dev.to, and RSS feeds.
"""

import requests
import feedparser
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArxivScraper:
    """Scraper for arXiv academic papers."""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    def search(self, query: str, max_results: int = 50, time_range: str = "month") -> List[Dict[str, Any]]:
        """Search arXiv for papers matching query."""
        logger.info(f"Searching arXiv for: {query}")
        
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            papers = []
            root = ET.fromstring(response.content)
            
            # Parse Atom namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                paper = {
                    'title': entry.find('atom:title', ns).text.strip().replace('\n', ' '),
                    'summary': entry.find('atom:summary', ns).text.strip().replace('\n', ' ')[:500],
                    'authors': [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)],
                    'published': entry.find('atom:published', ns).text,
                    'link': entry.find('atom:id', ns).text,
                    'categories': [cat.attrib['term'] for cat in entry.findall('atom:category', ns)],
                    'source': 'arXiv'
                }
                
                # Filter by time range
                pub_date = datetime.fromisoformat(paper['published'].replace('Z', '+00:00'))
                if self._is_within_range(pub_date, time_range):
                    papers.append(paper)
            
            logger.info(f"Found {len(papers)} papers on arXiv")
            return papers
            
        except Exception as e:
            logger.error(f"Error scraping arXiv: {e}")
            return []
    
    def _is_within_range(self, date: datetime, time_range: str) -> bool:
        """Check if date is within specified time range."""
        now = datetime.now(date.tzinfo)
        if time_range == "week":
            return date > now - timedelta(days=7)
        elif time_range == "month":
            return date > now - timedelta(days=30)
        elif time_range == "year":
            return date > now - timedelta(days=365)
        return True


class GitHubScraper:
    """Scraper for GitHub repositories and trends."""
    
    BASE_URL = "https://api.github.com"
    
    def search_repositories(self, query: str, max_results: int = 30, time_range: str = "month") -> List[Dict[str, Any]]:
        """Search GitHub repositories."""
        logger.info(f"Searching GitHub for: {query}")
        
        # Build date filter
        date_filter = ""
        if time_range == "week":
            date_filter = f"created:>{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}"
        elif time_range == "month":
            date_filter = f"created:>{(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')}"
        elif time_range == "year":
            date_filter = f"created:>{(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')}"
        
        search_query = f"{query} {date_filter}".strip()
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/search/repositories",
                params={
                    "q": search_query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": min(max_results, 100)
                },
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=30
            )
            response.raise_for_status()
            
            repos = []
            for item in response.json().get('items', [])[:max_results]:
                repos.append({
                    'title': item['full_name'],
                    'description': item['description'] or '',
                    'url': item['html_url'],
                    'stars': item['stargazers_count'],
                    'language': item['language'],
                    'created_at': item['created_at'],
                    'source': 'GitHub'
                })
            
            logger.info(f"Found {len(repos)} repositories on GitHub")
            return repos
            
        except Exception as e:
            logger.error(f"Error scraping GitHub: {e}")
            return []


class HackerNewsScraper:
    """Scraper for HackerNews stories."""
    
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    
    def get_top_stories(self, query: str = "", max_results: int = 20) -> List[Dict[str, Any]]:
        """Get top stories from HackerNews."""
        logger.info("Fetching HackerNews top stories")
        
        try:
            # Get top story IDs
            response = requests.get(f"{self.BASE_URL}/topstories.json", timeout=30)
            response.raise_for_status()
            story_ids = response.json()[:max_results]
            
            stories = []
            for story_id in story_ids:
                story_response = requests.get(f"{self.BASE_URL}/item/{story_id}.json", timeout=30)
                if story_response.ok:
                    item = story_response.json()
                    if item and item.get('type') == 'story':
                        # Filter by query if provided
                        if not query or query.lower() in (item.get('title', '').lower() + ' ' + item.get('text', '').lower()):
                            stories.append({
                                'title': item.get('title', ''),
                                'url': item.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                                'score': item.get('score', 0),
                                'time': datetime.fromtimestamp(item.get('time', 0)).isoformat(),
                                'source': 'HackerNews'
                            })
                time.sleep(0.1)  # Rate limiting
            
            logger.info(f"Found {len(stories)} stories on HackerNews")
            return stories
            
        except Exception as e:
            logger.error(f"Error scraping HackerNews: {e}")
            return []


class RedditScraper:
    """Scraper for Reddit posts."""
    
    def search(self, query: str, subreddit: str = "all", max_results: int = 20) -> List[Dict[str, Any]]:
        """Search Reddit for posts."""
        logger.info(f"Searching Reddit r/{subreddit} for: {query}")
        
        try:
            url = f"https://www.reddit.com/r/{subreddit}/search.json"
            params = {
                "q": query,
                "sort": "relevance",
                "limit": max_results,
                "t": "month"
            }
            headers = {"User-Agent": "ResearchAgent/1.0"}
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            posts = []
            for item in response.json().get('data', {}).get('children', []):
                data = item['data']
                posts.append({
                    'title': data['title'],
                    'url': f"https://reddit.com{data['permalink']}",
                    'score': data['score'],
                    'subreddit': data['subreddit'],
                    'created': datetime.fromtimestamp(data['created_utc']).isoformat(),
                    'source': 'Reddit'
                })
            
            logger.info(f"Found {len(posts)} posts on Reddit")
            return posts
            
        except Exception as e:
            logger.error(f"Error scraping Reddit: {e}")
            return []


class DevToScraper:
    """Scraper for Dev.to articles."""
    
    BASE_URL = "https://dev.to/api/articles"
    
    def search(self, query: str = "", max_results: int = 20) -> List[Dict[str, Any]]:
        """Search Dev.to for articles."""
        logger.info(f"Searching Dev.to for: {query}")
        
        try:
            params = {
                "per_page": max_results,
                "tag": query if query else None
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            articles = []
            for item in response.json():
                if not query or query.lower() in item['title'].lower() or query.lower() in item.get('description', '').lower():
                    articles.append({
                        'title': item['title'],
                        'description': item.get('description', ''),
                        'url': item['url'],
                        'published_at': item['published_at'],
                        'tags': item.get('tag_list', []),
                        'source': 'Dev.to'
                    })
            
            logger.info(f"Found {len(articles)} articles on Dev.to")
            return articles[:max_results]
            
        except Exception as e:
            logger.error(f"Error scraping Dev.to: {e}")
            return []


class RSSFeedScraper:
    """Scraper for RSS feeds from tech blogs."""
    
    FEEDS = [
        "https://news.ycombinator.com/rss",
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
    ]
    
    def scrape(self, query: str = "", max_results: int = 30) -> List[Dict[str, Any]]:
        """Scrape RSS feeds for articles."""
        logger.info("Scraping RSS feeds")
        
        all_entries = []
        for feed_url in self.FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:
                    if not query or query.lower() in entry.get('title', '').lower() or query.lower() in entry.get('summary', '').lower():
                        all_entries.append({
                            'title': entry.get('title', ''),
                            'summary': entry.get('summary', '')[:300],
                            'url': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'source': f"RSS-{feed.feed.get('title', 'Unknown')}"
                        })
            except Exception as e:
                logger.error(f"Error parsing feed {feed_url}: {e}")
                continue
        
        logger.info(f"Found {len(all_entries)} RSS entries")
        return all_entries[:max_results]


class DataScraper:
    """Main scraper orchestrator."""
    
    def __init__(self):
        self.arxiv = ArxivScraper()
        self.github = GitHubScraper()
        self.hackernews = HackerNewsScraper()
        self.reddit = RedditScraper()
        self.devto = DevToScraper()
        self.rss = RSSFeedScraper()
        # Import web search module
        try:
            from web_search import create_web_searcher
            self.web_search = create_web_searcher()
            logger.info("Web search enabled")
        except ImportError:
            self.web_search = None
            logger.warning("Web search module not available")
    
    def scrape_all(self, query: str, focus: str = "all", time_range: str = "month", depth: str = "standard") -> Dict[str, List[Dict[str, Any]]]:
        """Scrape all configured data sources including web search."""
        results = {
            'papers': [],
            'repositories': [],
            'news': [],
            'discussions': [],
            'web_results': []  # New: web search results
        }
        
        # Adjust limits based on depth
        limits = {
            'quick': {'papers': 20, 'repos': 15, 'news': 10, 'web': 5},
            'standard': {'papers': 50, 'repos': 30, 'news': 20, 'web': 15},
            'deep': {'papers': 100, 'repos': 50, 'news': 40, 'web': 30}
        }
        
        limit = limits.get(depth, limits['standard'])
        
        # Scrape based on focus
        if focus in ['papers', 'all']:
            results['papers'] = self.arxiv.search(query, max_results=limit['papers'], time_range=time_range)
        
        if focus in ['tools', 'all']:
            results['repositories'] = self.github.search_repositories(query, max_results=limit['repos'], time_range=time_range)
            # Web search for tools
            if self.web_search and depth in ['standard', 'deep']:
                try:
                    tool_results = self.web_search.search_tools(query, time_range=time_range)
                    results['web_results'].extend(tool_results[:limit['web'] // 2])
                except Exception as e:
                    logger.warning(f"Web tool search failed: {e}")
        
        if focus in ['trends', 'all']:
            results['news'].extend(self.hackernews.get_top_stories(query, max_results=limit['news'] // 3))
            results['news'].extend(self.devto.search(query, max_results=limit['news'] // 3))
            results['news'].extend(self.rss.scrape(query, max_results=limit['news'] // 3))
            results['discussions'] = self.reddit.search(query, max_results=limit['news'])
            # Web search for trends
            if self.web_search and depth in ['standard', 'deep']:
                try:
                    trend_results = self.web_search.search_trends(query, time_range=time_range)
                    results['web_results'].extend(trend_results[:limit['web'] // 2])
                except Exception as e:
                    logger.warning(f"Web trend search failed: {e}")
        
        # General web search for comprehensive research
        if self.web_search and depth == 'deep':
            try:
                general_results = self.web_search.search(query, max_results=limit['web'], time_range=time_range)
                results['web_results'].extend(general_results)
                # Deduplicate web results by URL
                seen_urls = set()
                unique_web_results = []
                for result in results['web_results']:
                    if result['url'] not in seen_urls:
                        seen_urls.add(result['url'])
                        unique_web_results.append(result)
                results['web_results'] = unique_web_results
            except Exception as e:
                logger.warning(f"General web search failed: {e}")
        
        return results
