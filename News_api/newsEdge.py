

import json
import os 

import requests
from dotenv import load_dotenv
import json
load_dotenv()
def get_news(query):
    ## query= ai research papers , ml , .....
    api_key = os.environ['GOOGLE_API_KEY']
    cse_id = os.environ['GOOGLE_CSE_ID']
    search_url = "https://www.googleapis.com/customsearch/v1"

    params = {
        'q': query,
        'key': api_key,
        'cx': cse_id,
        'num': 10  # Number of results, adjust as needed
    }
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()

        print("Headers:")
        print(response.headers)

        print("JSON Response:")

    except Exception as ex:
        raise ex
    return response.json() 