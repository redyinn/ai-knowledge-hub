"""
Text Chunker — Three strategies for splitting documents into retrievable chunks.

Strategies:
    1. Fixed-Size   — Split by character count with overlap
    2. Recursive    — Split by natural boundaries (paragraphs, sentences, words)
    3. Semantic     — Split by topic shifts using embedding similarity

Each strategy returns a list of Chunk objects with text, index, and metadata.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from config import CHUNK_SIZE, CHUNK_OVERLAP

if TYPE_CHECKING:
    pass


class ChunkStrategy(str, Enum):
    FIXED = "fixed"
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"


@dataclass
class Chunk:
    """A text chunk with metadata for retrieval."""

    text: str
    index: int
    source: str            # filename of the source document
    strategy: str          # which chunking strategy was used
    start_char: int = 0    # character offset in original document
    end_char: int = 0

    @property
    def word_count(self) -> int:
        return len(self.text.split())

    def __repr__(self) -> str:
        preview = self.text[:60].replace("\n", " ")
        return f"Chunk(#{self.index}, words={self.word_count}, '{preview}...')"


# ── Strategy 1: Fixed-Size Chunking ──────────────────────────────────

def chunk_fixed(
    text: str,
    source: str = "",
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    """
    Split text into fixed-size chunks with overlap.

    Simple and predictable. Works well for uniform text like articles.
    Less ideal for structured documents with headings/sections.
    """
    if not text.strip():
        return []

    chunks = []
    start = 0
    idx = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at a word boundary
        if end < len(text):
            last_space = text.rfind(" ", start, end)
            if last_space > start:
                end = last_space

        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(Chunk(
                text=chunk_text,
                index=idx,
                source=source,
                strategy="fixed",
                start_char=start,
                end_char=end,
            ))
            idx += 1

        start = end - overlap if end < len(text) else len(text)

    return chunks


# ── Strategy 2: Recursive Chunking ───────────────────────────────────

_SEPARATORS = [
    "\n\n",    # paragraphs
    "\n",      # lines
    ". ",      # sentences
    "! ",
    "? ",
    "; ",
    ", ",
    " ",       # words (last resort)
]


def _split_by_separator(text: str, separator: str) -> list[str]:
    """Split text and keep the separator at the end of each part."""
    parts = text.split(separator)
    result = []
    for i, part in enumerate(parts):
        if i < len(parts) - 1:
            result.append(part + separator)
        elif part:
            result.append(part)
    return result


def chunk_recursive(
    text: str,
    source: str = "",
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
    _separators: list[str] | None = None,
) -> list[Chunk]:
    """
    Recursively split text using natural boundaries.

    Tries paragraphs first, then sentences, then words.
    Preserves document structure better than fixed-size chunking.
    This is the most commonly used strategy in production RAG systems.
    """
    if not text.strip():
        return []

    separators = _separators or _SEPARATORS

    # Find the best separator that actually splits the text
    chosen_sep = None
    for sep in separators:
        if sep in text:
            chosen_sep = sep
            break

    if chosen_sep is None:
        # No separator found — treat entire text as one chunk
        return [Chunk(
            text=text.strip(),
            index=0,
            source=source,
            strategy="recursive",
            start_char=0,
            end_char=len(text),
        )]

    # Split by chosen separator
    parts = _split_by_separator(text, chosen_sep)
    remaining_seps = separators[separators.index(chosen_sep) + 1:]

    # Merge small parts into chunks
    chunks = []
    current = ""
    current_start = 0
    char_pos = 0

    for part in parts:
        if len(current) + len(part) <= chunk_size:
            if not current:
                current_start = char_pos
            current += part
        else:
            if current.strip():
                chunks.append((current.strip(), current_start, current_start + len(current)))

            # If this single part is too long, recurse with finer separators
            if len(part) > chunk_size and remaining_seps:
                sub_chunks = chunk_recursive(
                    part, source=source, chunk_size=chunk_size,
                    overlap=overlap, _separators=remaining_seps,
                )
                for sc in sub_chunks:
                    sc.start_char += char_pos
                    sc.end_char += char_pos
                    chunks.append((sc.text, sc.start_char, sc.end_char))
                current = ""
            else:
                current = part
                current_start = char_pos

        char_pos += len(part)

    if current.strip():
        chunks.append((current.strip(), current_start, current_start + len(current)))

    # Build Chunk objects with overlap
    result = []
    for i, (chunk_text, start, end) in enumerate(chunks):
        result.append(Chunk(
            text=chunk_text,
            index=i,
            source=source,
            strategy="recursive",
            start_char=start,
            end_char=end,
        ))

    return result


# ── Strategy 3: Semantic Chunking ────────────────────────────────────

def chunk_semantic(
    text: str,
    source: str = "",
    chunk_size: int = CHUNK_SIZE,
    similarity_threshold: float = 0.5,
) -> list[Chunk]:
    """
    Split text by detecting topic shifts using embedding similarity.

    First splits into sentences, then merges consecutive sentences
    that are semantically similar. When similarity drops below
    the threshold, a new chunk begins.

    Requires sentence-transformers to be installed.
    This is the most sophisticated strategy — best for documents
    with distinct topic sections.
    """
    # Split into sentences first
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) <= 1:
        return [Chunk(
            text=text.strip(), index=0, source=source,
            strategy="semantic", start_char=0, end_char=len(text),
        )]

    # Generate embeddings for each sentence
    try:
        from rag.embeddings import EmbeddingEngine
        engine = EmbeddingEngine()
        sentence_embeddings = engine.embed_texts(sentences)
    except ImportError:
        # Fallback to recursive if embeddings not available
        return chunk_recursive(text, source=source, chunk_size=chunk_size)

    # Compute cosine similarity between consecutive sentences
    import numpy as np

    def cosine_sim(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)

    # Group sentences into chunks based on similarity
    chunks = []
    current_group = [sentences[0]]
    current_start = 0
    char_pos = 0

    for i in range(1, len(sentences)):
        sim = cosine_sim(sentence_embeddings[i - 1], sentence_embeddings[i])

        combined = " ".join(current_group + [sentences[i]])

        if sim >= similarity_threshold and len(combined) <= chunk_size:
            current_group.append(sentences[i])
        else:
            chunk_text = " ".join(current_group)
            end_pos = char_pos
            chunks.append(Chunk(
                text=chunk_text,
                index=len(chunks),
                source=source,
                strategy="semantic",
                start_char=current_start,
                end_char=end_pos,
            ))
            current_group = [sentences[i]]
            current_start = end_pos

        char_pos += len(sentences[i]) + 1

    # Final group
    if current_group:
        chunk_text = " ".join(current_group)
        chunks.append(Chunk(
            text=chunk_text,
            index=len(chunks),
            source=source,
            strategy="semantic",
            start_char=current_start,
            end_char=len(text),
        ))

    return chunks


# ── Public API ───────────────────────────────────────────────────────

def chunk_document(
    text: str,
    source: str = "",
    strategy: ChunkStrategy | str = ChunkStrategy.RECURSIVE,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    """
    Chunk a document using the specified strategy.

    Parameters
    ----------
    text : str
        The full document text.
    source : str
        Filename for metadata.
    strategy : ChunkStrategy or str
        One of 'fixed', 'recursive', or 'semantic'.
    chunk_size : int
        Target chunk size in characters.
    overlap : int
        Character overlap between chunks (fixed/recursive only).

    Returns
    -------
    list[Chunk]
        List of text chunks ready for embedding.
    """
    strategy = ChunkStrategy(strategy)

    if strategy == ChunkStrategy.FIXED:
        return chunk_fixed(text, source, chunk_size, overlap)
    elif strategy == ChunkStrategy.RECURSIVE:
        return chunk_recursive(text, source, chunk_size, overlap)
    elif strategy == ChunkStrategy.SEMANTIC:
        return chunk_semantic(text, source, chunk_size)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
