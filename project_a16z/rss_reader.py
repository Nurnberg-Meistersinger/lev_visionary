import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List
import re
from config import A16Z_DAILY_URL


@dataclass
class NewsEntry:
    id: str     # slug
    title: str
    link: str


def extract_slug(url: str) -> str:
    """
    Из URL вида /p/the-state-of-ai вынимаем slug: the-state-of-ai
    """
    match = re.search(r"/p/([a-zA-Z0-9\-]+)", url)
    return match.group(1) if match else None


def fetch_rss(limit: int | None = None) -> List[NewsEntry]:
    resp = requests.get(A16Z_DAILY_URL, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    links = soup.find_all("a", href=True)
    articles = {}

    for a in links:
        href = a["href"]

        # Ищем только статьи Substack
        if "/p/" not in href:
            continue

        # Абсолютный URL
        if href.startswith("/"):
            url = "https://www.a16z.news" + href
        else:
            url = href

        slug = extract_slug(url)
        if not slug:
            print("⚠ Не удалось извлечь slug для URL:", url)
            continue

        title = a.get_text(strip=True)
        if not title:
            # резерв – хедер
            title = url

        # ключ = slug → уникальность гарантирована
        articles[slug] = (title, url)

    entries = [
        NewsEntry(id=slug, title=title, link=url)
        for slug, (title, url) in articles.items()
    ]

    if limit:
        entries = entries[:limit]

    return entries
