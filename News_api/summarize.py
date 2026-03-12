"""
News summariser.
Single responsibility: produce a structured markdown summary for a set of
article IDs, with transparent caching to avoid redundant LLM calls.
"""
import datetime
import json
from pathlib import Path

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .llm_client import get_llm
from .config import SUMMARIZATION_DIR, TEXT_DIR

_SUMMARIZATION_PROMPT = PromptTemplate(
    input_variables=["context"],
    template="""You are an expert news analyst. Create a comprehensive, well-structured summary.

Guidelines:
1. Begin with a concise overview of the main topic.
2. Organise into clear sections covering all major points.
3. Include key facts, figures, quotes, and implications.
4. Highlight controversies and differing viewpoints.
5. Cite each major point: [Source: <name>, Author: <author>]
6. End with a brief conclusion of key takeaways.

Context:
{context}

Summary:""",
)

class NewsSummarizer:
    """Summarise selected news articles using AWS Bedrock (Claude)."""

    def __init__(self) -> None:
        SUMMARIZATION_DIR.mkdir(parents=True, exist_ok=True)
        history_path = SUMMARIZATION_DIR / "history.json"
        if not history_path.exists():
            history_path.write_text(json.dumps({"history": []}))
        self._chain = _SUMMARIZATION_PROMPT | get_llm(temperature=0.4) | StrOutputParser()

    # ── private helpers ──────────────────────────────────────────────────────

    def _get_cached_summary(self, urls: list) -> str | None:
        history = json.loads((SUMMARIZATION_DIR / "history.json").read_text())
        for entry in history["history"]:
            if entry["urls"] == urls:
                return Path(entry["path"]).read_text()
        return None

    def _save_summary(self, summary: str, urls: list) -> None:
        path = SUMMARIZATION_DIR / f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}.txt"
        path.write_text(summary)
        history_path = SUMMARIZATION_DIR / "history.json"
        history = json.loads(history_path.read_text())
        history["history"].append({"path": str(path), "urls": urls})
        history_path.write_text(json.dumps(history, indent=2))

    def _build_context(self, urls: list, query_news: str, query_edge: str) -> str:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        file_path = TEXT_DIR / f"{today}_{query_news}_{query_edge}.json"
        if not file_path.exists():
            # Fall back to the most recently modified matching file
            candidates = sorted(TEXT_DIR.glob(f"*_{query_news}_{query_edge}.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            if not candidates:
                raise FileNotFoundError(f"No news data found for query '{query_news}'/'{query_edge}'. Fetch news first.")
            file_path = candidates[0]
        with open(file_path) as f:
            data = json.load(f)
        parts = []
        for article in data.get("Articles", []):
            if article["id"] in urls:
                parts.append(
                    f"Title: {article['title']}\n\n"
                    f"Content: {article['content']}\n\n"
                    f"[Source: {article['title']}, Author: {article.get('author', 'Unknown')}]"
                )
        return "\n\n---\n\n".join(parts)

    # ── public API ───────────────────────────────────────────────────────────

    def summarize(self, urls: list, query_news: str, query_edge: str) -> str:
        """Return a cached or freshly generated summary for the given article IDs."""
        urls = sorted(urls)
        cached = self._get_cached_summary(urls)
        if cached:
            return cached
        context = self._build_context(urls, query_news, query_edge)

        summary = self._chain.invoke({"context": context})
        self._save_summary(summary, urls)
        return summary
        with open(path, "w") as f:
            f.writelines(summary)

        return summary 

