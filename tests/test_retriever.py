"""Tests for the vector store retrieval."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.chunker import Chunk
from rag.vectorstore import VectorStore, SearchResult


def _make_chunks() -> list[Chunk]:
    """Create test chunks about different topics."""
    return [
        Chunk(text="Python is a programming language used for AI and data science.",
              index=0, source="tech.txt", strategy="fixed"),
        Chunk(text="Machine learning models learn patterns from training data.",
              index=1, source="tech.txt", strategy="fixed"),
        Chunk(text="ChromaDB is a vector database for storing embeddings.",
              index=2, source="tech.txt", strategy="fixed"),
        Chunk(text="The weather in Berlin is often cold and rainy in winter.",
              index=0, source="weather.txt", strategy="fixed"),
        Chunk(text="Mediterranean cuisine features olive oil, fresh vegetables, and seafood.",
              index=0, source="cooking.txt", strategy="fixed"),
    ]


class TestVectorStore:
    _counter = 0

    def setup_method(self):
        TestVectorStore._counter += 1
        self.store = VectorStore(
            collection_name=f"test_collection_{self._counter}",
            ephemeral=True,
        )

    def test_add_chunks(self):
        chunks = _make_chunks()
        added = self.store.add_chunks(chunks)
        assert added == 5
        assert self.store.count == 5

    def test_search_returns_results(self):
        self.store.add_chunks(_make_chunks())
        results = self.store.search("What is Python?")
        assert len(results) > 0
        assert all(isinstance(r, SearchResult) for r in results)

    def test_search_relevance(self):
        self.store.add_chunks(_make_chunks())
        results = self.store.search("programming language for AI")
        # The Python chunk should rank highest
        assert "Python" in results[0].text or "programming" in results[0].text

    def test_search_with_source_filter(self):
        self.store.add_chunks(_make_chunks())
        results = self.store.search("what is this about?", source_filter="cooking.txt")
        assert len(results) >= 1
        assert all(r.source == "cooking.txt" for r in results)

    def test_sources_list(self):
        self.store.add_chunks(_make_chunks())
        sources = self.store.sources
        assert "tech.txt" in sources
        assert "weather.txt" in sources
        assert "cooking.txt" in sources

    def test_delete_source(self):
        self.store.add_chunks(_make_chunks())
        deleted = self.store.delete_source("weather.txt")
        assert deleted == 1
        assert self.store.count == 4
        assert "weather.txt" not in self.store.sources

    def test_clear(self):
        self.store.add_chunks(_make_chunks())
        cleared = self.store.clear()
        assert cleared == 5
        assert self.store.count == 0

    def test_get_stats(self):
        self.store.add_chunks(_make_chunks())
        stats = self.store.get_stats()
        assert stats["total_chunks"] == 5
        assert stats["num_sources"] == 3
        assert stats["total_words"] > 0

    def test_empty_store_search(self):
        results = self.store.search("anything")
        assert results == []

    def test_score_range(self):
        self.store.add_chunks(_make_chunks())
        results = self.store.search("Python AI")
        for r in results:
            assert -0.5 <= r.score <= 1.0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
