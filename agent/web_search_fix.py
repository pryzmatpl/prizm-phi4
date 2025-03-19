from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

@staticmethod
def search_web(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """Search the web for the given query using Google and Bing."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    google_url = f"https://www.google.com/search?q={quote(query)}&num={num_results}"
    bing_url = f"https://www.bing.com/search?q={quote(query)}&count={num_results}"
    results = []

    for url, source in [(google_url, "Google"), (bing_url, "Bing")]:
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('div.g' if source == "Google" else 'li.b_algo')[:num_results]
            for item in items:
                link = item.find('a', href=True)
                title = item.find('h3' if source == "Google" else 'h2')
                if link and title:
                    results.append({'title': title.text, 'url': link['href'], 'source': source})
        except Exception as e:
            print(f"{source} search failed: {e}")
    return results[:num_results * 2] 