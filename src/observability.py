"""
Observability and monitoring module for production-grade agent deployment.
Tracks metrics, logs, and traces for agent operations.
"""

import time
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics tracked by the agent."""
    LATENCY = "latency"
    COST = "cost"
    ACCURACY = "accuracy"
    DATA_QUALITY = "data_quality"
    ERROR_RATE = "error_rate"
    TASK_COMPLETION = "task_completion"


@dataclass
class AgentMetric:
    """Represents a single metric measurement."""
    metric_type: str
    value: float
    timestamp: str
    context: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AgentTrace:
    """Represents a trace of agent execution."""
    trace_id: str
    operation: str
    start_time: float
    end_time: Optional[float] = None
    status: str = "running"
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate duration if trace is complete."""
        if self.end_time:
            return self.end_time - self.start_time
        return None


class ObservabilityManager:
    """Manages observability for the research agent."""
    
    def __init__(self):
        self.metrics: List[AgentMetric] = []
        self.traces: List[AgentTrace] = []
        self.errors: List[Dict[str, Any]] = []
        self.session_start = time.time()
        
    def start_trace(self, operation: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start a new trace for an operation."""
        trace_id = f"{operation}_{int(time.time() * 1000)}"
        trace = AgentTrace(
            trace_id=trace_id,
            operation=operation,
            start_time=time.time(),
            metadata=metadata or {}
        )
        self.traces.append(trace)
        logger.debug(f"Started trace: {trace_id} for operation: {operation}")
        return trace_id
    
    def end_trace(self, trace_id: str, status: str = "success", error: Optional[str] = None):
        """End a trace."""
        for trace in self.traces:
            if trace.trace_id == trace_id:
                trace.end_time = time.time()
                trace.status = status
                trace.error = error
                logger.debug(f"Ended trace: {trace_id} with status: {status}, duration: {trace.duration:.2f}s")
                return
        logger.warning(f"Trace not found: {trace_id}")
    
    def record_metric(self, metric_type: MetricType, value: float, context: Optional[Dict[str, Any]] = None):
        """Record a metric."""
        metric = AgentMetric(
            metric_type=metric_type.value,
            value=value,
            timestamp=datetime.now().isoformat(),
            context=context or {}
        )
        self.metrics.append(metric)
        logger.info(f"Metric recorded: {metric_type.value}={value}")
    
    def record_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None):
        """Record an error."""
        error = {
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        self.errors.append(error)
        logger.error(f"Error recorded: {error_type} - {error_message}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all observability data."""
        total_duration = time.time() - self.session_start
        
        # Calculate aggregated metrics
        latencies = [m.value for m in self.metrics if m.metric_type == MetricType.LATENCY.value]
        costs = [m.value for m in self.metrics if m.metric_type == MetricType.COST.value]
        
        completed_traces = [t for t in self.traces if t.status == "success"]
        failed_traces = [t for t in self.traces if t.status == "error"]
        
        return {
            "session_duration": total_duration,
            "total_traces": len(self.traces),
            "completed_traces": len(completed_traces),
            "failed_traces": len(failed_traces),
            "success_rate": len(completed_traces) / len(self.traces) if self.traces else 0,
            "total_metrics": len(self.metrics),
            "total_errors": len(self.errors),
            "avg_latency": sum(latencies) / len(latencies) if latencies else 0,
            "total_cost": sum(costs),
            "trace_details": [t.to_dict() for t in self.traces],
            "recent_errors": self.errors[-10:]  # Last 10 errors
        }
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file."""
        data = {
            "metrics": [m.to_dict() for m in self.metrics],
            "traces": [t.to_dict() for t in self.traces],
            "errors": self.errors,
            "summary": self.get_summary()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Metrics exported to {filepath}")


class PerformanceMonitor:
    """Context manager for monitoring operation performance."""
    
    def __init__(self, obs_manager: ObservabilityManager, operation: str, metadata: Optional[Dict[str, Any]] = None):
        self.obs_manager = obs_manager
        self.operation = operation
        self.metadata = metadata
        self.trace_id = None
        self.start_time = None
    
    def __enter__(self):
        """Start monitoring."""
        self.trace_id = self.obs_manager.start_trace(self.operation, self.metadata)
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End monitoring and record metrics."""
        duration = time.time() - self.start_time
        
        if exc_type is None:
            self.obs_manager.end_trace(self.trace_id, status="success")
            self.obs_manager.record_metric(MetricType.LATENCY, duration, {"operation": self.operation})
        else:
            self.obs_manager.end_trace(self.trace_id, status="error", error=str(exc_val))
            self.obs_manager.record_error(
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                context={"operation": self.operation}
            )
        
        return False  # Don't suppress exceptions


def calculate_quality_score(data: Dict[str, List[Dict[str, Any]]]) -> float:
    """Calculate data quality score based on completeness and diversity."""
    total_items = sum(len(v) for v in data.values())
    
    if total_items == 0:
        return 0.0
    
    # Check diversity across sources
    source_count = sum(1 for v in data.values() if len(v) > 0)
    diversity_score = source_count / 4  # 4 main categories
    
    # Check completeness of data
    completeness_scores = []
    for category, items in data.items():
        if items:
            # Sample first item to check completeness
            item = items[0]
            required_fields = ['title', 'source']
            present_fields = sum(1 for f in required_fields if item.get(f))
            completeness_scores.append(present_fields / len(required_fields))
    
    completeness_score = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
    
    # Combined score (weighted)
    quality_score = (diversity_score * 0.4 + completeness_score * 0.6)
    
    return round(quality_score, 2)
