"""
RAG Pipeline — Orchestrates the full Retrieval-Augmented Generation flow.

Flow: Document Upload → Chunk → Embed → Store → Query → Retrieve → Augment → Generate

This is the central module that ties together all RAG components.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generator

from openai import OpenAI

from config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    DEFAULT_MODEL,
    MODELS,
    OPENROUTER_BASE_URL,
    TOP_K,
    get_api_key,
)
from prompts.rag import build_rag_prompt
from prompts.system import SYSTEM_PROMPT
from rag.chunker import Chunk, ChunkStrategy, chunk_document
from rag.loader import Document, load_document
from rag.vectorstore import SearchResult, VectorStore


@dataclass
class RAGResponse:
    """Complete RAG response with answer, sources, and metadata."""

    answer: str
    sources: list[SearchResult]
    model_used: str
    query: str
    num_chunks_retrieved: int
    metadata: dict = field(default_factory=dict)


class RAGPipeline:
    """
    Full RAG pipeline: ingest documents, query with retrieval-augmented generation.

    Usage:
        pipeline = RAGPipeline()
        pipeline.ingest(document, strategy="recursive")
        response = pipeline.query("What is this document about?")
    """

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        model_tier: str = DEFAULT_MODEL,
    ):
        self._store = vector_store or VectorStore()
        self._model_tier = model_tier

    @property
    def store(self) -> VectorStore:
        return self._store

    @property
    def model_config(self) -> dict:
        return MODELS[self._model_tier]

    def set_model(self, tier: str) -> None:
        """Switch the LLM model tier (simple/medium/complex)."""
        if tier not in MODELS:
            raise ValueError(f"Unknown model tier: {tier}. Choose from: {list(MODELS.keys())}")
        self._model_tier = tier

    # ── Ingestion ────────────────────────────────────────────────────

    def ingest(
        self,
        document: Document,
        strategy: ChunkStrategy | str = ChunkStrategy.RECURSIVE,
        chunk_size: int = CHUNK_SIZE,
        overlap: int = CHUNK_OVERLAP,
    ) -> list[Chunk]:
        """
        Ingest a document: chunk it, embed it, store it.

        Parameters
        ----------
        document : Document
            Loaded document from the loader module.
        strategy : ChunkStrategy or str
            Chunking strategy to use.
        chunk_size : int
            Target chunk size.
        overlap : int
            Overlap between chunks.

        Returns
        -------
        list[Chunk]
            The generated chunks.
        """
        chunks = chunk_document(
            text=document.text,
            source=document.filename,
            strategy=strategy,
            chunk_size=chunk_size,
            overlap=overlap,
        )
        self._store.add_chunks(chunks)
        return chunks

    def ingest_file(
        self,
        source,
        filename: str | None = None,
        strategy: str = "recursive",
    ) -> tuple[Document, list[Chunk]]:
        """
        Load and ingest a file in one step.

        Returns the Document and its Chunks.
        """
        doc = load_document(source, filename=filename)
        chunks = self.ingest(doc, strategy=strategy)
        return doc, chunks

    # ── Query ────────────────────────────────────────────────────────

    def retrieve(self, query: str, top_k: int = TOP_K) -> list[SearchResult]:
        """Retrieve relevant chunks for a query."""
        return self._store.search(query, top_k=top_k)

    def query(
        self,
        question: str,
        top_k: int = TOP_K,
        model_tier: str | None = None,
    ) -> RAGResponse:
        """
        Full RAG query: retrieve context, augment prompt, generate answer.

        Parameters
        ----------
        question : str
            User's question.
        top_k : int
            Number of chunks to retrieve.
        model_tier : str, optional
            Override model tier for this query.

        Returns
        -------
        RAGResponse
            Complete response with answer, sources, and metadata.
        """
        # Retrieve
        results = self.retrieve(question, top_k=top_k)

        if not results:
            return RAGResponse(
                answer="No documents have been uploaded yet. Please upload documents first.",
                sources=[],
                model_used="none",
                query=question,
                num_chunks_retrieved=0,
            )

        # Augment
        prompt = build_rag_prompt(question, results)

        # Generate
        tier = model_tier or self._model_tier
        model_id = MODELS[tier]["id"]

        api_key = get_api_key()
        if not api_key:
            return RAGResponse(
                answer="API key not configured. Please set your OpenRouter API key.",
                sources=results,
                model_used=model_id,
                query=question,
                num_chunks_retrieved=len(results),
            )

        client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)

        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
            )
            answer = response.choices[0].message.content or ""
        except Exception as e:
            answer = f"Error calling model {model_id}: {e}"

        return RAGResponse(
            answer=answer,
            sources=results,
            model_used=MODELS[tier]["name"],
            query=question,
            num_chunks_retrieved=len(results),
            metadata={
                "model_id": model_id,
                "model_tier": tier,
            },
        )

    def query_stream(
        self,
        question: str,
        top_k: int = TOP_K,
        model_tier: str | None = None,
    ) -> Generator[str, None, RAGResponse]:
        """
        Streaming RAG query — yields answer chunks as they arrive.

        Usage:
            gen = pipeline.query_stream("What is X?")
            for chunk in gen:
                print(chunk, end="")
            # After iteration, get the full response:
            response = gen.value  # only available via send/return pattern

        Yields
        ------
        str
            Partial answer text chunks.
        """
        # Retrieve
        results = self.retrieve(question, top_k=top_k)

        if not results:
            yield "No documents have been uploaded yet. Please upload documents first."
            return

        # Augment
        prompt = build_rag_prompt(question, results)

        # Generate with streaming
        tier = model_tier or self._model_tier
        model_id = MODELS[tier]["id"]

        api_key = get_api_key()
        if not api_key:
            yield "API key not configured. Please set your OpenRouter API key."
            return

        client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)

        try:
            stream = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
                stream=True,
            )

            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_answer += delta
                    yield delta
        except Exception as e:
            yield f"\n\nError calling model {model_id}: {e}"
