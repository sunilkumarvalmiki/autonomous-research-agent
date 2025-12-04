"""Evaluation metrics for the autonomous research agent."""

from typing import List, Dict, Any, Optional
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class EvaluationMetrics:
    """Metrics for evaluating agent performance."""
    
    @staticmethod
    def calculate_relevance_score(
        query: str,
        response: str,
        keywords: Optional[List[str]] = None
    ) -> float:
        """
        Calculate relevance score based on keyword matching.
        
        Args:
            query: Original query
            response: Agent response
            keywords: Optional list of expected keywords
        
        Returns:
            Relevance score between 0 and 1
        """
        if keywords is None:
            # Extract keywords from query
            keywords = [word.lower() for word in query.split() if len(word) > 3]
        
        if not keywords:
            return 0.5  # Neutral score
        
        response_lower = response.lower()
        matches = sum(1 for keyword in keywords if keyword in response_lower)
        
        return matches / len(keywords)
    
    @staticmethod
    def calculate_coherence_score(text: str) -> float:
        """
        Calculate coherence score based on simple heuristics.
        
        Args:
            text: Text to evaluate
        
        Returns:
            Coherence score between 0 and 1
        """
        if not text:
            return 0.0
        
        score = 1.0
        
        # Check for reasonable sentence length
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if sentences:
            avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_length < 3 or avg_length > 50:
                score -= 0.2
        
        # Check for repeated phrases (indication of poor generation)
        words = text.lower().split()
        if len(words) > 10:
            word_counts = Counter(words)
            most_common_count = word_counts.most_common(1)[0][1]
            if most_common_count > len(words) * 0.1:
                score -= 0.3
        
        # Check for proper capitalization
        if not any(c.isupper() for c in text):
            score -= 0.1
        
        return max(0.0, score)
    
    @staticmethod
    def calculate_completeness_score(
        response: str,
        min_length: int = 50
    ) -> float:
        """
        Calculate completeness score based on response length.
        
        Args:
            response: Response to evaluate
            min_length: Minimum expected length
        
        Returns:
            Completeness score between 0 and 1
        """
        length = len(response.split())
        
        if length >= min_length:
            return 1.0
        elif length == 0:
            return 0.0
        else:
            return length / min_length
    
    @staticmethod
    def evaluate_response(
        query: str,
        response: str,
        expected_keywords: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Comprehensive evaluation of a response.
        
        Args:
            query: Original query
            response: Agent response
            expected_keywords: Optional list of expected keywords
        
        Returns:
            Dictionary of evaluation metrics
        """
        metrics = {
            'relevance': EvaluationMetrics.calculate_relevance_score(
                query, response, expected_keywords
            ),
            'coherence': EvaluationMetrics.calculate_coherence_score(response),
            'completeness': EvaluationMetrics.calculate_completeness_score(response)
        }
        
        # Calculate overall score
        metrics['overall'] = sum(metrics.values()) / len(metrics)
        
        return metrics
    
    @staticmethod
    def compare_responses(
        responses: List[Dict[str, Any]],
        query: str
    ) -> Dict[str, Any]:
        """
        Compare multiple responses to the same query.
        
        Args:
            responses: List of response dicts with 'response' and 'model' keys
            query: Original query
        
        Returns:
            Comparison results
        """
        comparisons = []
        
        for resp_dict in responses:
            metrics = EvaluationMetrics.evaluate_response(query, resp_dict['response'])
            comparisons.append({
                'model': resp_dict.get('model', 'unknown'),
                'response': resp_dict['response'],
                'metrics': metrics
            })
        
        # Sort by overall score
        comparisons.sort(key=lambda x: x['metrics']['overall'], reverse=True)
        
        return {
            'query': query,
            'comparisons': comparisons,
            'best_model': comparisons[0]['model'] if comparisons else None
        }
