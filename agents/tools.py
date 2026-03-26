"""
Agent Tools — Actions the research agent can perform.

Each tool is a callable that takes parameters and returns a result string.
The agent selects and chains these tools to answer complex questions.
"""
from __future__ import annotations

from dataclasses import dataclass

from rag.vectorstore import VectorStore


@dataclass
class ToolResult:
    """Result of a tool execution."""

    tool_name: str
    input_text: str
    output: str
    success: bool = True


def vector_search(store: VectorStore, query: str, top_k: int = 3) -> ToolResult:
    """
    Search the vector store for relevant chunks.

    Used by the agent to gather evidence for sub-questions.
    """
    results = store.search(query, top_k=top_k)

    if not results:
        return ToolResult(
            tool_name="vector_search",
            input_text=query,
            output="No relevant documents found.",
            success=False,
        )

    output_parts = []
    for i, r in enumerate(results, 1):
        output_parts.append(
            f"[{i}] (relevance: {r.score:.0%}, source: {r.source})\n{r.text}"
        )

    return ToolResult(
        tool_name="vector_search",
        input_text=query,
        output="\n\n".join(output_parts),
    )


def summarize_results(results: list[ToolResult]) -> ToolResult:
    """
    Combine multiple search results into a structured context block.

    Used before the final synthesis step.
    """
    if not results:
        return ToolResult(
            tool_name="summarize_results",
            input_text="",
            output="No results to summarize.",
            success=False,
        )

    parts = []
    for r in results:
        if r.success:
            parts.append(f"## Research: {r.input_text}\n{r.output}")

    output = "\n\n---\n\n".join(parts) if parts else "No successful results found."

    return ToolResult(
        tool_name="summarize_results",
        input_text=f"{len(results)} results",
        output=output,
    )


def compare_sources(store: VectorStore, topic: str) -> ToolResult:
    """
    Find and compare what different source documents say about a topic.

    Useful for cross-document analysis.
    """
    results = store.search(topic, top_k=10)

    if not results:
        return ToolResult(
            tool_name="compare_sources",
            input_text=topic,
            output="No documents found for comparison.",
            success=False,
        )

    # Group by source
    by_source: dict[str, list] = {}
    for r in results:
        by_source.setdefault(r.source, []).append(r)

    if len(by_source) < 2:
        return ToolResult(
            tool_name="compare_sources",
            input_text=topic,
            output=f"Only one source found ({list(by_source.keys())[0]}). Need multiple sources for comparison.",
            success=False,
        )

    parts = []
    for source, chunks in by_source.items():
        best = max(chunks, key=lambda c: c.score)
        parts.append(f"### {source} (relevance: {best.score:.0%})\n{best.text}")

    return ToolResult(
        tool_name="compare_sources",
        input_text=topic,
        output="\n\n".join(parts),
    )
