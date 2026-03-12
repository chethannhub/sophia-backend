"""
Local embeddings client using sentence-transformers.
Single responsibility: provide a singleton HuggingFaceEmbeddings instance.
No external API calls — runs fully offline on CPU.
"""
from langchain_huggingface import HuggingFaceEmbeddings

from .config import EMBEDDING_MODEL_NAME

_instance: HuggingFaceEmbeddings | None = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a singleton local HuggingFace embeddings model.

    Model: BAAI/bge-base-en-v1.5
        - 768-dimensional embeddings
        - Excellent retrieval quality for RAG
        - Runs on CPU without any API credentials

    Returns:
        A ready-to-use HuggingFaceEmbeddings instance.
    """
    global _instance
    if _instance is None:
        _instance = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _instance
