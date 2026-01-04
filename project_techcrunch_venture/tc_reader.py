import requests
from bs4 import BeautifulSoup

def fetch_latest_articles(limit=5):
    url = "https://techcrunch.com/category/venture/feed/"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "xml")

    items = soup.find_all("item")[:limit]
    articles = []

    for item in items:
        title = item.title.get_text(strip=True)
        link = item.link.get_text(strip=True)
        slug = link.rstrip("/").split("/")[-1]

        articles.append({
            "slug": slug,
            "title": title,
            "link": link
        })

    print("DEBUG: found articles:", len(articles))
    return articles
