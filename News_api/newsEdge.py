
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_news(query):
    # newsEdge (Google Custom Search) is currently disabled.
    # Calls are commented out in fetch_news.py.
    # Re-enable by setting GOOGLE_API_KEY and GOOGLE_CSE_ID in .env
    # and restoring the call in fetch_news.py.
    raise NotImplementedError(
        "newsEdge.get_news is disabled. "
        "Set GOOGLE_API_KEY and GOOGLE_CSE_ID in .env to re-enable."
    )