import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}

def extract_article_text(url):
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    # Новый контейнер контента TechCrunch
    body = soup.select_one("div.wp-block-post-content")

    if not body:
        print("DEBUG: no wp-block-post-content found")
        return ""

    parts = []

    for tag in body.find_all(["p", "h2", "h3", "blockquote"]):
        text = tag.get_text(" ", strip=True)
        if text:
            parts.append(text)

    return "\n".join(parts)
