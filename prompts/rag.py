"""
RAG-specific prompt templates for context-augmented generation.
"""

RAG_PROMPT = """Answer the user's question based ONLY on the following document excerpts.
If the excerpts don't contain enough information, say: "The uploaded documents don't contain sufficient information to answer this question."

## Retrieved Document Excerpts

{context}

## User Question

{question}

## Instructions
- Base your answer strictly on the provided excerpts
- Cite sources using [Source: filename] notation
- If multiple documents are relevant, synthesize information from all of them
- Structure your answer clearly
- If the question asks about something not in the documents, state that explicitly"""


CONTEXT_TEMPLATE = """--- Excerpt {index} (from: {source}, relevance: {score:.0%}) ---
{text}
"""


def build_rag_prompt(question: str, search_results: list) -> str:
    """
    Build a complete RAG prompt from search results.

    Parameters
    ----------
    question : str
        The user's question.
    search_results : list[SearchResult]
        Retrieved chunks from the vector store.

    Returns
    -------
    str
        Complete prompt with context and question.
    """
    context_parts = []
    for i, result in enumerate(search_results, 1):
        context_parts.append(CONTEXT_TEMPLATE.format(
            index=i,
            source=result.source,
            score=result.score,
            text=result.text,
        ))

    context = "\n".join(context_parts)
    return RAG_PROMPT.format(context=context, question=question)
