"""
Vector Store — ChromaDB wrapper for storing and retrieving document chunks.

Handles collection management, adding chunks with embeddings,
and semantic similarity search.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import chromadb
from chromadb.config import Settings

from config import CHROMA_COLLECTION, TOP_K
from rag.chunker import Chunk
from rag.embeddings import EmbeddingEngine


@dataclass
class SearchResult:
    """A single search result with text, score, and metadata."""

    text: str
    score: float           # similarity score (0-1, higher = more similar)
    source: str            # original filename
    chunk_index: int       # chunk position in source document
    metadata: dict         # all stored metadata

    def __repr__(self) -> str:
        preview = self.text[:50].replace("\n", " ")
        return f"SearchResult(score={self.score:.3f}, '{preview}...')"


class VectorStore:
    """
    ChromaDB-based vector store for document chunks.

    Stores chunk text, embeddings, and metadata.
    Supports add, search, delete, and collection management.
    """

    def __init__(
        self,
        collection_name: str = CHROMA_COLLECTION,
        persist_dir: str = "./chroma_data",
        ephemeral: bool = False,
    ):
        if ephemeral:
            self._client = chromadb.EphemeralClient(
                settings=Settings(anonymized_telemetry=False),
            )
        else:
            self._client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(anonymized_telemetry=False),
            )
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self._embedder = EmbeddingEngine()

    @property
    def count(self) -> int:
        """Number of chunks stored."""
        return self._collection.count()

    @property
    def sources(self) -> list[str]:
        """List of unique source documents in the store."""
        if self.count == 0:
            return []
        result = self._collection.get(include=["metadatas"])
        sources = {m.get("source", "unknown") for m in result["metadatas"]}
        return sorted(sources)

    def add_chunks(self, chunks: list[Chunk]) -> int:
        """
        Add chunks to the vector store.

        Generates embeddings and stores them alongside chunk text and metadata.

        Parameters
        ----------
        chunks : list[Chunk]
            Chunks to add (from the chunker module).

        Returns
        -------
        int
            Number of chunks added.
        """
        if not chunks:
            return 0

        texts = [c.text for c in chunks]
        embeddings = self._embedder.embed_texts(texts).tolist()

        ids = [f"{c.source}_{c.index}" for c in chunks]
        metadatas = [
            {
                "source": c.source,
                "chunk_index": c.index,
                "strategy": c.strategy,
                "start_char": c.start_char,
                "end_char": c.end_char,
                "word_count": c.word_count,
            }
            for c in chunks
        ]

        self._collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(chunks)

    def search(
        self,
        query: str,
        top_k: int = TOP_K,
        source_filter: str | None = None,
    ) -> list[SearchResult]:
        """
        Semantic search for chunks similar to the query.

        Parameters
        ----------
        query : str
            The search query.
        top_k : int
            Number of results to return.
        source_filter : str, optional
            Only search within chunks from this source document.

        Returns
        -------
        list[SearchResult]
            Ranked list of matching chunks.
        """
        query_embedding = self._embedder.embed_text(query).tolist()

        where_filter = None
        if source_filter:
            where_filter = {"source": source_filter}

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.count) if self.count > 0 else top_k,
            where=where_filter,
            include=["documents", "distances", "metadatas"],
        )

        search_results = []
        if results["documents"] and results["documents"][0]:
            for doc, dist, meta in zip(
                results["documents"][0],
                results["distances"][0],
                results["metadatas"][0],
            ):
                # ChromaDB returns distances; convert to similarity
                # For cosine space: similarity = 1 - distance
                similarity = 1.0 - dist

                search_results.append(SearchResult(
                    text=doc,
                    score=round(similarity, 4),
                    source=meta.get("source", "unknown"),
                    chunk_index=meta.get("chunk_index", 0),
                    metadata=meta,
                ))

        return search_results

    def delete_source(self, source: str) -> int:
        """
        Delete all chunks from a specific source document.

        Returns the number of chunks deleted.
        """
        if self.count == 0:
            return 0

        # Get IDs for this source
        result = self._collection.get(
            where={"source": source},
            include=[],
        )

        if result["ids"]:
            self._collection.delete(ids=result["ids"])
            return len(result["ids"])
        return 0

    def clear(self) -> int:
        """Delete all chunks from the store."""
        count = self.count
        if count > 0:
            # Get all IDs and delete
            result = self._collection.get(include=[])
            if result["ids"]:
                self._collection.delete(ids=result["ids"])
        return count

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the vector store."""
        stats = {
            "total_chunks": self.count,
            "sources": self.sources,
            "num_sources": len(self.sources),
        }

        if self.count > 0:
            result = self._collection.get(include=["metadatas"])
            total_words = sum(
                m.get("word_count", 0) for m in result["metadatas"]
            )
            strategies = {m.get("strategy", "unknown") for m in result["metadatas"]}
            stats["total_words"] = total_words
            stats["strategies_used"] = sorted(strategies)

        return stats
