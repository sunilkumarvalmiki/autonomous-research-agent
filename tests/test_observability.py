"""
Unit tests for observability module.
Tests metrics tracking, tracing, and monitoring.
"""

import pytest
from unittest.mock import Mock
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from observability import ObservabilityManager, PerformanceMonitor, MetricType, calculate_quality_score


class TestObservabilityManager:
    """Test ObservabilityManager functionality."""
    
    def test_initialization(self):
        """Test manager initializes correctly."""
        obs = ObservabilityManager()
        assert obs is not None
        assert len(obs.metrics) == 0
        assert len(obs.traces) == 0
    
    def test_start_end_trace(self):
        """Test trace lifecycle."""
        obs = ObservabilityManager()
        
        trace_id = obs.start_trace("test_operation")
        assert trace_id is not None
        assert len(obs.traces) == 1
        
        obs.end_trace(trace_id, status="success")
        
        trace = obs.traces[0]
        assert trace.status == "success"
        assert trace.duration is not None
        assert trace.duration > 0
    
    def test_record_metric(self):
        """Test metric recording."""
        obs = ObservabilityManager()
        
        obs.record_metric(MetricType.LATENCY, 1.5, {"operation": "scraping"})
        
        assert len(obs.metrics) == 1
        assert obs.metrics[0].metric_type == MetricType.LATENCY.value
        assert obs.metrics[0].value == 1.5
    
    def test_get_summary(self):
        """Test summary generation."""
        obs = ObservabilityManager()
        
        trace_id = obs.start_trace("test")
        obs.end_trace(trace_id, status="success")
        obs.record_metric(MetricType.LATENCY, 2.0)
        
        summary = obs.get_summary()
        
        assert summary['total_traces'] == 1
        assert summary['completed_traces'] == 1
        assert summary['success_rate'] == 1.0
        assert summary['avg_latency'] == 2.0


class TestPerformanceMonitor:
    """Test PerformanceMonitor context manager."""
    
    def test_context_manager_success(self):
        """Test context manager with successful operation."""
        obs = ObservabilityManager()
        
        with PerformanceMonitor(obs, "test_op"):
            time.sleep(0.01)  # Simulate work
        
        assert len(obs.traces) == 1
        assert obs.traces[0].status == "success"
        assert len(obs.metrics) == 1  # Latency metric
    
    def test_context_manager_error(self):
        """Test context manager with error."""
        obs = ObservabilityManager()
        
        try:
            with PerformanceMonitor(obs, "test_op"):
                raise ValueError("Test error")
        except ValueError:
            pass
        
        assert len(obs.traces) == 1
        assert obs.traces[0].status == "error"
        assert len(obs.errors) == 1


class TestQualityScore:
    """Test quality score calculation."""
    
    def test_calculate_quality_score_empty(self):
        """Test quality score with empty data."""
        data = {'papers': [], 'repositories': [], 'news': [], 'discussions': []}
        score = calculate_quality_score(data)
        assert score == 0.0
    
    def test_calculate_quality_score_complete(self):
        """Test quality score with complete data."""
        data = {
            'papers': [{'title': 'Test', 'source': 'arXiv'}],
            'repositories': [{'title': 'Repo', 'source': 'GitHub'}],
            'news': [{'title': 'News', 'source': 'HN'}],
            'discussions': [{'title': 'Discussion', 'source': 'Reddit'}]
        }
        score = calculate_quality_score(data)
        assert score > 0.0
        assert score <= 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
