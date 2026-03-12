from bs4 import BeautifulSoup
import json
import requests


def get_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    heading = soup.find("h1").get_text()
    image = soup.find("img").get("src")
    main_content = soup.find('main') or soup.find('article') or soup.find('div', class_="content")
    context = main_content.get_text().replace("\n", "").replace("\t", "")
    
    content = {
        "heading": heading,
        "image": image,
        "content": context
    }
    
    return json.dumps(content, ensure_ascii=False, indent=2)