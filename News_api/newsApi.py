import os
from pathlib import Path
import requests
import datetime
from dotenv import load_dotenv

# Always load .env from the project root regardless of working directory
load_dotenv(Path(__file__).parent.parent / ".env")
_API_KEY = os.getenv("NEWS_API_KEY", "")
yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

def get_news(term):
    if term == "AIML":
        term = "AI"
        url = ('https://newsapi.org/v2/everything?'
        f'q={"+".join(term.split())}+("AI" OR "ML" OR "artificial intelligence" OR "machine learning")&'
        f'from={yesterday}&'
        'searchIn=title&'
        'language=en&'
        'pageSize=20&'
        f'apiKey={_API_KEY}')
    elif term == "AR-VR":
        date = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        term = "AR"
        url = ('https://newsapi.org/v2/everything?'
        f'q={"+".join(term.split())}+("AR" AND "VR" OR "augmented reality" OR "virtual reality" OR "AR VR" OR "ARVR")&'
        f'from={date}&'
        'searchIn=title&'
        'language=en&'
        'pageSize=20&'
        f'apiKey={_API_KEY}')
    else:
        date = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime("%Y-%m-%d")
        term = "blockChain"
        url = ('https://newsapi.org/v2/everything?'
        f'q={"+".join(term.split())}+("blockchain" OR "cryptocurrency" OR "bitcoin" OR "ethereum OR WEB3")&'
        f'from={date}&'
        'searchIn=title&'
        'language=en&'
        'pageSize=20&'
        f'apiKey={_API_KEY}')

    try:
        response = requests.get(url, timeout=12)
        return response.json()
    except requests.RequestException as exc:
        return {
            "status": "error",
            "code": "request_failed",
            "message": str(exc),
            "articles": [],
        }
