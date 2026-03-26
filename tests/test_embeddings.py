"""Tests for the embedding engine."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from rag.embeddings import EmbeddingEngine


class TestEmbeddingEngine:
    def setup_method(self):
        self.engine = EmbeddingEngine()

    def test_singleton(self):
        engine2 = EmbeddingEngine()
        assert self.engine is engine2

    def test_embed_text_returns_vector(self):
        vec = self.engine.embed_text("Hello world")
        assert isinstance(vec, np.ndarray)
        assert vec.ndim == 1
        assert len(vec) == self.engine.dimension

    def test_embed_texts_batch(self):
        texts = ["Hello", "World", "AI is great"]
        vecs = self.engine.embed_texts(texts)
        assert vecs.shape == (3, self.engine.dimension)

    def test_similar_texts_high_score(self):
        sim = self.engine.similarity(
            "Machine learning is a subset of AI",
            "ML is part of artificial intelligence",
        )
        assert sim > 0.5

    def test_different_texts_lower_score(self):
        sim = self.engine.similarity(
            "Machine learning and neural networks",
            "Cooking recipes for Italian pasta",
        )
        assert sim < 0.5

    def test_normalized_embeddings(self):
        vec = self.engine.embed_text("Test normalization")
        norm = np.linalg.norm(vec)
        assert abs(norm - 1.0) < 0.01, f"Expected unit norm, got {norm}"

    def test_dimension_is_384(self):
        assert self.engine.dimension == 384


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
