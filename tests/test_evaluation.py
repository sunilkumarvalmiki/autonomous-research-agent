"""Unit tests for evaluation metrics."""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from autonomous_agent.evaluation.metrics import EvaluationMetrics


class TestEvaluationMetrics(unittest.TestCase):
    """Test evaluation metrics."""
    
    def test_relevance_score_high(self):
        """Test high relevance score."""
        query = "machine learning algorithms"
        response = "Machine learning algorithms include neural networks and decision trees."
        
        score = EvaluationMetrics.calculate_relevance_score(query, response)
        
        self.assertGreater(score, 0.5)
    
    def test_relevance_score_low(self):
        """Test low relevance score."""
        query = "machine learning algorithms"
        response = "The weather is nice today."
        
        score = EvaluationMetrics.calculate_relevance_score(query, response)
        
        self.assertLess(score, 0.5)
    
    def test_relevance_score_with_keywords(self):
        """Test relevance with custom keywords."""
        query = "test"
        response = "This contains important and relevant keywords."
        keywords = ["important", "relevant"]
        
        score = EvaluationMetrics.calculate_relevance_score(query, response, keywords)
        
        self.assertEqual(score, 1.0)
    
    def test_coherence_score(self):
        """Test coherence scoring."""
        text = "This is a well-formed sentence. It has proper structure."
        
        score = EvaluationMetrics.calculate_coherence_score(text)
        
        self.assertGreater(score, 0.5)
    
    def test_coherence_score_poor(self):
        """Test coherence with poorly formed text."""
        text = "word word word word " * 100  # Highly repetitive
        
        score = EvaluationMetrics.calculate_coherence_score(text)
        
        self.assertLess(score, 1.0)
    
    def test_completeness_score_complete(self):
        """Test completeness with adequate response."""
        response = " ".join(["word"] * 100)  # 100 words
        
        score = EvaluationMetrics.calculate_completeness_score(response, min_length=50)
        
        self.assertEqual(score, 1.0)
    
    def test_completeness_score_incomplete(self):
        """Test completeness with short response."""
        response = "short"
        
        score = EvaluationMetrics.calculate_completeness_score(response, min_length=50)
        
        self.assertLess(score, 1.0)
    
    def test_evaluate_response(self):
        """Test comprehensive response evaluation."""
        query = "Explain neural networks"
        response = "Neural networks are computational models inspired by biological neurons. " * 10
        
        metrics = EvaluationMetrics.evaluate_response(query, response)
        
        self.assertIn('relevance', metrics)
        self.assertIn('coherence', metrics)
        self.assertIn('completeness', metrics)
        self.assertIn('overall', metrics)
        
        # All scores should be between 0 and 1
        for key, value in metrics.items():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)
    
    def test_compare_responses(self):
        """Test comparing multiple responses."""
        query = "What is AI?"
        responses = [
            {"model": "model1", "response": "AI is artificial intelligence."},
            {"model": "model2", "response": "Artificial intelligence (AI) is the simulation of human intelligence."},
            {"model": "model3", "response": "Short."}
        ]
        
        comparison = EvaluationMetrics.compare_responses(responses, query)
        
        self.assertEqual(comparison['query'], query)
        self.assertEqual(len(comparison['comparisons']), 3)
        self.assertIsNotNone(comparison['best_model'])
        
        # Comparisons should be sorted by overall score
        scores = [c['metrics']['overall'] for c in comparison['comparisons']]
        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == '__main__':
    unittest.main()
