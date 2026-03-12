"""
Vector-store builder.
Single responsibility: chunk articles and persist them in ChromaDB
using local sentence-transformer embeddings.
"""
import datetime
import glob
import json
import os
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma.vectorstores import Chroma

from .embeddings_client import get_embeddings
from .config import TEXT_DIR, DB_DIR

_splitter = RecursiveCharacterTextSplitter(chunk_overlap=100, chunk_size=1000)


def _get_most_recent_news_file() -> str:
    """Return the path to the most recently modified news JSON in TEXT_DIR."""
    files = [f for f in glob.glob(str(TEXT_DIR / "*")) if os.path.isfile(f)]
    if not files:
        raise FileNotFoundError(f"No news files found in {TEXT_DIR}")
    return max(files, key=os.path.getmtime)


def _load_articles_as_documents(article_ids: list, news_file: str) -> list:
    """Load articles matching article_ids from news_file as LangChain Documents."""
    with open(news_file) as f:
        data = json.load(f)
    docs = []
    for article in data.get("Articles", []):
        if article["id"] in article_ids:
            content = (article.get("brief", "") + " " + article.get("content", "")).strip()
            docs.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": article.get("urls", ""),
                        "heading": article.get("title", ""),
                    },
                )
            )
    return docs


def convert_db(article_ids: list, persist_directory: str = None) -> str:
    """Embed articles and persist them in a ChromaDB vector store.

    Args:
        article_ids:        List of article IDs to embed.
        persist_directory:  Optional path. Auto-generated from timestamp if omitted.

    Returns:
        Path to the persisted ChromaDB directory.
    """
    news_file = _get_most_recent_news_file()
    docs = _load_articles_as_documents(article_ids, news_file)
    if not docs:
        raise ValueError(f"No articles found for IDs: {article_ids}")

    chunks = _splitter.split_documents(docs)
    DB_DIR.mkdir(parents=True, exist_ok=True)
    if not persist_directory:
        persist_directory = str(DB_DIR / datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))

    Chroma.from_documents(chunks, get_embeddings(), persist_directory=persist_directory)
    return persist_directory
