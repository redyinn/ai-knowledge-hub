"""
Embedding Engine — Generates vector embeddings using sentence-transformers.

Uses the all-MiniLM-L6-v2 model by default (384 dimensions, fast, free).
Runs entirely locally — no API calls needed.
"""
from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL


class EmbeddingEngine:
    """Manages embedding model lifecycle and text-to-vector conversion."""

    _instance: EmbeddingEngine | None = None
    _model: SentenceTransformer | None = None

    def __new__(cls) -> EmbeddingEngine:
        """Singleton — only load the model once to save memory."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(EMBEDDING_MODEL)
        return self._model

    @property
    def dimension(self) -> int:
        """Embedding vector dimension (384 for MiniLM)."""
        return self.model.get_sentence_embedding_dimension()

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed a single text string.

        Returns
        -------
        np.ndarray
            1D vector of shape (dimension,).
        """
        return self.model.encode(text, normalize_embeddings=True)

    def embed_texts(self, texts: list[str], batch_size: int = 64) -> np.ndarray:
        """
        Embed multiple texts in batches.

        Parameters
        ----------
        texts : list[str]
            List of text strings to embed.
        batch_size : int
            Number of texts to process at once.

        Returns
        -------
        np.ndarray
            2D array of shape (len(texts), dimension).
        """
        return self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def similarity(self, text_a: str, text_b: str) -> float:
        """Compute cosine similarity between two texts."""
        vec_a = self.embed_text(text_a)
        vec_b = self.embed_text(text_b)
        return float(np.dot(vec_a, vec_b))
