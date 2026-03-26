"""
AI Knowledge Hub — Central Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()


# ── API ──────────────────────────────────────────────────────────────
def get_api_key() -> str:
    """Resolve OpenRouter API key from multiple sources."""
    try:
        import streamlit as st
        key = st.secrets.get("OPENROUTER_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("OPENROUTER_API_KEY", "")


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ── Models (OpenRouter free tier) ────────────────────────────────────
MODELS = {
    "simple": {
        "id": "meta-llama/llama-3.1-8b-instruct:free",
        "name": "Llama 3.1 8B",
        "cost_per_1k": 0.0,
        "description": "Fast, lightweight — ideal for simple factual questions",
    },
    "medium": {
        "id": "mistralai/mistral-7b-instruct:free",
        "name": "Mistral 7B",
        "cost_per_1k": 0.0,
        "description": "Balanced — good for summaries and moderate reasoning",
    },
    "complex": {
        "id": "qwen/qwen3-14b:free",
        "name": "Qwen3 14B",
        "cost_per_1k": 0.0,
        "description": "Powerful — handles multi-step reasoning and synthesis",
    },
}

DEFAULT_MODEL = "medium"

# ── RAG Settings ─────────────────────────────────────────────────────
CHUNK_SIZE = 512          # tokens (approx characters / 4)
CHUNK_OVERLAP = 64        # overlap between consecutive chunks
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_COLLECTION = "knowledge_hub"
TOP_K = 5                 # number of chunks to retrieve

# ── Supported file types ─────────────────────────────────────────────
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}

# ── Agent Settings ───────────────────────────────────────────────────
MAX_AGENT_STEPS = 5       # max sub-questions the research agent will explore
AGENT_MODEL = "complex"   # always use the strongest model for agents
