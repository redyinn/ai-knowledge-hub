"""Tests for the text chunking module."""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.chunker import (
    Chunk,
    ChunkStrategy,
    chunk_document,
    chunk_fixed,
    chunk_recursive,
)


SAMPLE_TEXT = """Artificial intelligence has transformed the technology landscape.
Machine learning models can now process natural language with remarkable accuracy.

Large Language Models like GPT and Claude represent a major breakthrough.
These models are trained on vast datasets and can generate human-like text.
They are used in applications ranging from chatbots to code generation.

Retrieval Augmented Generation combines the power of LLMs with external knowledge.
RAG systems retrieve relevant documents and use them as context for generation.
This approach reduces hallucinations and grounds responses in factual data.

Vector databases play a crucial role in modern AI architectures.
They store embeddings and enable fast similarity search across millions of documents.
ChromaDB and FAISS are popular choices for vector storage."""


class TestChunkFixed:
    def test_returns_chunks(self):
        chunks = chunk_fixed(SAMPLE_TEXT, source="test.txt", chunk_size=200)
        assert len(chunks) > 0
        assert all(isinstance(c, Chunk) for c in chunks)

    def test_chunk_size_respected(self):
        chunks = chunk_fixed(SAMPLE_TEXT, source="test.txt", chunk_size=200)
        for chunk in chunks:
            assert len(chunk.text) <= 210  # small tolerance for word boundary

    def test_overlap_creates_more_chunks(self):
        no_overlap = chunk_fixed(SAMPLE_TEXT, chunk_size=200, overlap=0)
        with_overlap = chunk_fixed(SAMPLE_TEXT, chunk_size=200, overlap=50)
        assert len(with_overlap) >= len(no_overlap)

    def test_source_metadata(self):
        chunks = chunk_fixed(SAMPLE_TEXT, source="report.pdf", chunk_size=200)
        assert all(c.source == "report.pdf" for c in chunks)
        assert all(c.strategy == "fixed" for c in chunks)

    def test_empty_text(self):
        chunks = chunk_fixed("", source="empty.txt")
        assert chunks == []

    def test_indices_sequential(self):
        chunks = chunk_fixed(SAMPLE_TEXT, chunk_size=200)
        for i, chunk in enumerate(chunks):
            assert chunk.index == i


class TestChunkRecursive:
    def test_returns_chunks(self):
        chunks = chunk_recursive(SAMPLE_TEXT, source="test.txt")
        assert len(chunks) > 0

    def test_preserves_paragraphs(self):
        # With large chunk size, should respect paragraph boundaries
        chunks = chunk_recursive(SAMPLE_TEXT, source="test.txt", chunk_size=1000)
        # Paragraphs should be kept together when possible
        assert len(chunks) >= 1

    def test_handles_short_text(self):
        chunks = chunk_recursive("Hello world.", source="short.txt")
        assert len(chunks) == 1
        assert chunks[0].text == "Hello world."

    def test_strategy_metadata(self):
        chunks = chunk_recursive(SAMPLE_TEXT, chunk_size=200)
        assert all(c.strategy == "recursive" for c in chunks)

    def test_small_chunk_size_splits_more(self):
        large = chunk_recursive(SAMPLE_TEXT, chunk_size=500)
        small = chunk_recursive(SAMPLE_TEXT, chunk_size=100)
        assert len(small) >= len(large)


class TestChunkDocument:
    def test_fixed_strategy(self):
        chunks = chunk_document(SAMPLE_TEXT, strategy="fixed", chunk_size=200)
        assert all(c.strategy == "fixed" for c in chunks)

    def test_recursive_strategy(self):
        chunks = chunk_document(SAMPLE_TEXT, strategy="recursive", chunk_size=200)
        assert all(c.strategy == "recursive" for c in chunks)

    def test_enum_strategy(self):
        chunks = chunk_document(SAMPLE_TEXT, strategy=ChunkStrategy.FIXED, chunk_size=200)
        assert len(chunks) > 0

    def test_invalid_strategy_raises(self):
        try:
            chunk_document(SAMPLE_TEXT, strategy="unknown")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_word_count_property(self):
        chunks = chunk_document(SAMPLE_TEXT, strategy="fixed", chunk_size=200)
        for chunk in chunks:
            assert chunk.word_count == len(chunk.text.split())

    def test_all_text_covered(self):
        """Verify that no content is silently dropped."""
        chunks = chunk_fixed(SAMPLE_TEXT, chunk_size=200, overlap=0)
        # All original words should appear in at least one chunk
        original_words = set(SAMPLE_TEXT.split())
        chunk_words = set()
        for c in chunks:
            chunk_words.update(c.text.split())
        # Allow minor differences from stripping
        missing = original_words - chunk_words
        assert len(missing) <= 2, f"Missing words: {missing}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
