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
    """Fetch news articles for a given search term.
    
    Args:
        term: Search term. Supported values: 'AIML', 'AR-VR', 'blockChain'
        
    Returns:
        JSON response from NewsAPI or error dict
    """
    supported_terms = {"AIML", "AR-VR", "blockChain"}
    if term not in supported_terms:
        return {
            "status": "error",
            "code": "unsupported_term",
            "message": f"Unknown news category '{term}'. Supported categories: {', '.join(sorted(supported_terms))}",
            "articles": [],
        }
    
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
    else:  # blockChain
        date = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime("%Y-%m-%d")
        url = ('https://newsapi.org/v2/everything?'
        f'q={"+".join(term.split())}+("blockchain" OR "cryptocurrency" OR "bitcoin" OR "ethereum OR WEB3")&'
        f'from={date}&'
        'searchIn=title&'
        'language=en&'
        'pageSize=20&'
        f'apiKey={_API_KEY}')

    try:
        response = requests.get(url, timeout=12)
        data = response.json()
        
        # Log API response for debugging
        if data.get("status") == "error":
            print(f"[NewsAPI Error] Category: {term}, Code: {data.get('code')}, Message: {data.get('message')}")
            if _API_KEY == "":
                print("[WARNING] NEWS_API_KEY environment variable is not set!")
        
        return data
    except requests.RequestException as exc:
        print(f"[Request Error] Category: {term}, Exception: {str(exc)}")
        return {
            "status": "error",
            "code": "request_failed",
            "message": str(exc),
            "articles": [],
        }
