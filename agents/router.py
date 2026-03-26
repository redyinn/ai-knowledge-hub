"""
Query Router — Analyzes query complexity and selects the optimal model.

Classifies queries into three tiers:
    - simple:  Factual, short, direct questions → fast, cheap model
    - medium:  Summaries, moderate reasoning → balanced model
    - complex: Multi-step reasoning, synthesis, comparison → powerful model

Uses heuristics + keyword analysis (no LLM call needed for routing).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from config import MODELS


class QueryComplexity(str, Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


@dataclass
class RoutingDecision:
    """Result of the query routing analysis."""

    complexity: QueryComplexity
    model_id: str
    model_name: str
    reason: str
    confidence: float  # 0-1

    @property
    def tier(self) -> str:
        return self.complexity.value


# Keyword patterns for complexity detection
_COMPLEX_PATTERNS = [
    r"\b(compare|contrast|difference|similarities)\b",
    r"\b(analyze|analyse|evaluate|assess|critique)\b",
    r"\b(how does .+ relate to)\b",
    r"\b(what are the implications|consequences)\b",
    r"\b(pros and cons|advantages and disadvantages)\b",
    r"\b(step[- ]by[- ]step|in detail|comprehensive)\b",
    r"\b(why does|why is|explain why)\b",
    r"\b(synthesize|combine|integrate)\b",
    r"\b(research|investigate|explore)\b",
]

_SIMPLE_PATTERNS = [
    r"\b(what is|who is|when was|where is|define)\b",
    r"\b(list|name|which)\b",
    r"\b(yes or no|true or false)\b",
    r"\b(how many|how much)\b",
]


def _count_pattern_matches(text: str, patterns: list[str]) -> int:
    """Count how many patterns match in the text."""
    text_lower = text.lower()
    return sum(1 for p in patterns if re.search(p, text_lower))


def _estimate_complexity(query: str) -> tuple[QueryComplexity, str, float]:
    """
    Estimate query complexity using heuristics.

    Returns (complexity, reason, confidence).
    """
    words = query.split()
    word_count = len(words)

    complex_matches = _count_pattern_matches(query, _COMPLEX_PATTERNS)
    simple_matches = _count_pattern_matches(query, _SIMPLE_PATTERNS)

    # Multiple questions in one query
    question_marks = query.count("?")

    # Scoring
    score = 0.5  # neutral start

    # Word count factor
    if word_count <= 8:
        score -= 0.2
    elif word_count >= 25:
        score += 0.2
    elif word_count >= 40:
        score += 0.3

    # Pattern matching
    score += complex_matches * 0.15
    score -= simple_matches * 0.15

    # Multiple questions = more complex
    if question_marks >= 2:
        score += 0.2

    # Clamp score
    score = max(0.0, min(1.0, score))

    # Classify
    if score <= 0.35:
        complexity = QueryComplexity.SIMPLE
        reason = "Direct factual question — using fast model"
        confidence = 1.0 - score  # more confident when clearly simple
    elif score >= 0.65:
        complexity = QueryComplexity.COMPLEX
        reason = "Multi-step reasoning required — using powerful model"
        confidence = score
    else:
        complexity = QueryComplexity.MEDIUM
        reason = "Moderate reasoning needed — using balanced model"
        confidence = 0.6  # medium is inherently less certain

    return complexity, reason, confidence


def route_query(query: str) -> RoutingDecision:
    """
    Analyze a query and decide which model to use.

    Parameters
    ----------
    query : str
        The user's question.

    Returns
    -------
    RoutingDecision
        Contains the selected model and reasoning.
    """
    complexity, reason, confidence = _estimate_complexity(query)
    model = MODELS[complexity.value]

    return RoutingDecision(
        complexity=complexity,
        model_id=model["id"],
        model_name=model["name"],
        reason=reason,
        confidence=round(confidence, 2),
    )
