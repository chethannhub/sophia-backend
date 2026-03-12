import json
import os
import datetime
from . import newsApi
from . import newsEdge
import requests
from bs4 import BeautifulSoup

_HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"}

def get_unified_news(query_news=None, query_edge=None):
    article_id = 0
    final = {"Articles": []}

    news_categories = ["AIML", "AR-VR", "Block Chain"]
    for category in news_categories:
        print(f"compiling {category}...")
        response_news = newsApi.get_news(category)
        for article in response_news.get("articles", []):
            # Prefer scraped full content; fall back to API-provided snippet
            scraped = fetch_full_content(article["url"])
            if scraped:
                content = scraped
            else:
                # Strip the "[+N chars]" truncation marker from the API content
                api_content = article.get("content") or ""
                content = api_content.split("[+")[0].strip()

            temp = {
                "id": article_id,
                "urls": article["url"],
                "title": article["title"],
                "brief": article.get("description") or "",
                "image": article.get("urlToImage"),
                "content": content,
                "label": category,
                "author": article.get("author"),
                "publishedAt": article.get("publishedAt"),
                "source": (article.get("source") or {}).get("name"),
            }
            final["Articles"].append(temp)
            article_id += 1

    print(f"compiled — {article_id} articles total")
    return final


def fetch_full_content(url: str) -> str:
    """Scrape paragraph text from a URL. Returns empty string on any failure."""
    try:
        response = requests.get(url, timeout=6, headers=_HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find_all("p")
        content = " ".join(p.get_text() for p in paragraphs)
        return content[:4000]  # cap to keep payloads manageable
    except Exception:
        return ""