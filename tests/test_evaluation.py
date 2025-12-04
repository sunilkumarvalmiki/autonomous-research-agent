"""
Unit tests for evaluation module.
Tests quality assessment functionality.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from evaluation import ResearchEvaluator


class TestResearchEvaluator:
    """Test ResearchEvaluator functionality."""
    
    def test_initialization(self):
        """Test evaluator initializes correctly."""
        evaluator = ResearchEvaluator()
        assert evaluator is not None
    
    def test_evaluate_comprehensiveness(self):
        """Test comprehensiveness evaluation."""
        evaluator = ResearchEvaluator()
        
        data = {
            'papers': [{'title': 'Test', 'source': 'arXiv'}],
            'repositories': [{'title': 'Repo', 'source': 'GitHub'}],
            'news': [],
            'discussions': []
        }
        
        score, details = evaluator.evaluate_comprehensiveness(data)
        
        assert 0 <= score <= 1
        assert 'source_coverage' in details
        assert 'quantity' in details
    
    def test_evaluate_analysis_quality(self):
        """Test analysis quality evaluation."""
        evaluator = ResearchEvaluator()
        
        analysis = {
            'key_findings': ['Finding 1', 'Finding 2', 'Finding 3'],
            'summary': 'This is a comprehensive summary of findings.',
            'recommendations': ['Rec 1', 'Rec 2']
        }
        
        score, details = evaluator.evaluate_analysis_quality(analysis)
        
        assert 0 <= score <= 1
        assert 'completeness' in details
        assert 'depth' in details
    
    def test_comprehensive_evaluation(self):
        """Test full comprehensive evaluation."""
        evaluator = ResearchEvaluator()
        
        data = {
            'papers': [{'title': 'Test', 'source': 'arXiv', 'url': 'http://test'}],
            'repositories': [],
            'news': [],
            'discussions': []
        }
        
        analysis = {
            'key_findings': ['Finding 1'],
            'summary': 'Summary text here.',
            'recommendations': ['Recommendation']
        }
        
        outputs = {
            'markdown': '## Test\nContent',
            'json': '{"test": "data"}',
            'html': '<!DOCTYPE html><html></html>',
            'bibtex': '@article{test}',
            'csv': 'Type,Title',
            'mermaid': 'graph TD'
        }
        
        report = evaluator.comprehensive_evaluation("test query", data, analysis, outputs)
        
        assert 'overall_score' in report
        assert 'rating' in report
        assert 'scores' in report
        assert 'recommendations' in report
        assert 0 <= report['overall_score'] <= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
