import re
import requests
from bs4 import BeautifulSoup

def getSeriesList(url) -> list:
    seriesList = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    }

    Client = requests.get(url, headers=headers)
    html = Client.text
    if not html:
        print('Error: html is empty')
        return seriesList

    Soup = BeautifulSoup(html, 'html.parser')
    for item in Soup.select('.article_name h2'):
        matches = re.search(r'(\d+)\s+серия\s+(.+)', item.text, re.IGNORECASE)
        if not matches:
            continue
        data = {
            'name': matches[2],
            'number': matches[1],
        }

        seriesList.append(data)

    return seriesList

if __name__ == '__main__':
    pass
