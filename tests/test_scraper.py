"""
Unit tests for the scraper module.
Tests data collection from various sources.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper import DataScraper, ArxivScraper, GitHubScraper


class TestArxivScraper:
    """Test ArxivScraper functionality."""
    
    def test_initialization(self):
        """Test scraper initializes correctly."""
        scraper = ArxivScraper()
        assert scraper is not None
    
    @patch('requests.get')
    def test_search_success(self, mock_get):
        """Test successful arXiv search."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''<?xml version="1.0"?>
        <feed>
            <entry>
                <title>Test Paper</title>
                <summary>Test summary</summary>
                <author><name>Test Author</name></author>
                <link href="http://arxiv.org/abs/1234.5678"/>
                <published>2024-01-01</published>
                <category term="cs.AI"/>
            </entry>
        </feed>'''
        mock_get.return_value = mock_response
        
        scraper = ArxivScraper()
        results = scraper.search("machine learning", max_results=10)
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert results[0]['title'] == 'Test Paper'
        assert results[0]['source'] == 'arXiv'


class TestGitHubScraper:
    """Test GitHubScraper functionality."""
    
    def test_initialization(self):
        """Test scraper initializes correctly."""
        scraper = GitHubScraper()
        assert scraper is not None


class TestDataScraper:
    """Test main DataScraper orchestrator."""
    
    def test_initialization(self):
        """Test DataScraper initializes all sub-scrapers."""
        scraper = DataScraper()
        
        assert scraper.arxiv is not None
        assert scraper.github is not None
        assert scraper.hackernews is not None
        assert scraper.reddit is not None
        assert scraper.devto is not None
        assert scraper.rss is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
