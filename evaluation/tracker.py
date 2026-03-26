"""
Performance Tracker — Records token usage, latency, and costs per query.

Stores metrics in session state for dashboard visualization.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class QueryMetric:
    """Metrics for a single query."""

    timestamp: str
    query: str
    model_name: str
    model_tier: str
    latency_ms: float
    num_chunks_retrieved: int
    num_sources: int
    query_complexity: str = "medium"

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "query": self.query[:80],
            "model": self.model_name,
            "tier": self.model_tier,
            "latency_ms": round(self.latency_ms),
            "chunks": self.num_chunks_retrieved,
            "sources": self.num_sources,
            "complexity": self.query_complexity,
        }


class PerformanceTracker:
    """
    Tracks query performance metrics for the evaluation dashboard.

    Stores metrics in-memory (session-scoped).
    """

    def __init__(self):
        self._metrics: list[QueryMetric] = []
        self._active_timer: float | None = None

    def start_timer(self) -> None:
        """Start timing a query."""
        self._active_timer = time.perf_counter()

    def stop_timer(self) -> float:
        """Stop timing and return elapsed milliseconds."""
        if self._active_timer is None:
            return 0.0
        elapsed = (time.perf_counter() - self._active_timer) * 1000
        self._active_timer = None
        return elapsed

    def record(
        self,
        query: str,
        model_name: str,
        model_tier: str,
        latency_ms: float,
        num_chunks: int,
        num_sources: int,
        complexity: str = "medium",
    ) -> QueryMetric:
        """Record metrics for a completed query."""
        metric = QueryMetric(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            query=query,
            model_name=model_name,
            model_tier=model_tier,
            latency_ms=latency_ms,
            num_chunks_retrieved=num_chunks,
            num_sources=num_sources,
            query_complexity=complexity,
        )
        self._metrics.append(metric)
        return metric

    @property
    def metrics(self) -> list[QueryMetric]:
        return self._metrics

    @property
    def total_queries(self) -> int:
        return len(self._metrics)

    @property
    def avg_latency(self) -> float:
        if not self._metrics:
            return 0.0
        return sum(m.latency_ms for m in self._metrics) / len(self._metrics)

    def get_model_distribution(self) -> dict[str, int]:
        """Count queries per model tier."""
        dist: dict[str, int] = {}
        for m in self._metrics:
            dist[m.model_tier] = dist.get(m.model_tier, 0) + 1
        return dist

    def get_complexity_distribution(self) -> dict[str, int]:
        """Count queries per complexity level."""
        dist: dict[str, int] = {}
        for m in self._metrics:
            dist[m.query_complexity] = dist.get(m.query_complexity, 0) + 1
        return dist

    def to_dataframe_data(self) -> list[dict]:
        """Convert all metrics to a list of dicts for DataFrame display."""
        return [m.to_dict() for m in self._metrics]
