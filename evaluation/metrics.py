"""
Evaluation Metrics — Measures retrieval quality and answer relevance.

Provides:
    - Retrieval relevance scoring (embedding similarity)
    - Source diversity measurement
    - Context coverage estimation
"""
from __future__ import annotations

from dataclasses import dataclass

from rag.embeddings import EmbeddingEngine
from rag.vectorstore import SearchResult


@dataclass
class RetrievalMetrics:
    """Metrics for a single retrieval operation."""

    avg_relevance: float         # mean similarity score of retrieved chunks
    max_relevance: float         # best chunk score
    min_relevance: float         # worst chunk score
    num_sources: int             # unique source documents used
    source_diversity: float      # ratio of unique sources to total chunks
    coverage_estimate: str       # "high", "medium", "low"

    def to_dict(self) -> dict:
        return {
            "avg_relevance": f"{self.avg_relevance:.1%}",
            "max_relevance": f"{self.max_relevance:.1%}",
            "min_relevance": f"{self.min_relevance:.1%}",
            "num_sources": self.num_sources,
            "source_diversity": f"{self.source_diversity:.1%}",
            "coverage": self.coverage_estimate,
        }


def evaluate_retrieval(results: list[SearchResult]) -> RetrievalMetrics:
    """
    Evaluate the quality of retrieved chunks.

    Parameters
    ----------
    results : list[SearchResult]
        Retrieved chunks from a search query.

    Returns
    -------
    RetrievalMetrics
        Quality metrics for the retrieval.
    """
    if not results:
        return RetrievalMetrics(
            avg_relevance=0.0,
            max_relevance=0.0,
            min_relevance=0.0,
            num_sources=0,
            source_diversity=0.0,
            coverage_estimate="none",
        )

    scores = [r.score for r in results]
    sources = {r.source for r in results}

    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    diversity = len(sources) / len(results)

    # Coverage heuristic based on relevance scores
    if avg_score >= 0.6:
        coverage = "high"
    elif avg_score >= 0.35:
        coverage = "medium"
    else:
        coverage = "low"

    return RetrievalMetrics(
        avg_relevance=round(avg_score, 4),
        max_relevance=round(max_score, 4),
        min_relevance=round(min_score, 4),
        num_sources=len(sources),
        source_diversity=round(diversity, 4),
        coverage_estimate=coverage,
    )


def compute_answer_relevance(question: str, answer: str) -> float:
    """
    Estimate how relevant the answer is to the question using embedding similarity.

    This is a lightweight proxy — not as accurate as LLM-as-judge,
    but doesn't require an additional API call.

    Returns
    -------
    float
        Cosine similarity between question and answer (0-1).
    """
    engine = EmbeddingEngine()
    return engine.similarity(question, answer)
