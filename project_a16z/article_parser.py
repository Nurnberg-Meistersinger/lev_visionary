import requests
from bs4 import BeautifulSoup


def extract_article_text(url: str) -> str:
    """
    Парсер статей a16z.news, основанных на Substack.
    Контент находится внутри <div class="body markup">.
    """

    print(f"Загрузка статьи: {url}")

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print("❌ Ошибка загрузки HTML:", e)
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")

    # Находим основной контейнер статьи
    body_div = soup.select_one("div.body.markup")
    if not body_div:
        print("❌ Не найден div.body.markup — структура страницы другая.")
        return ""

    parts = []

    # Собираем содержимое параграфов, списков, подзаголовков
    for el in body_div.find_all(["p", "li", "h2", "h3"], recursive=True):
        text = el.get_text(strip=True)
        if text:
            parts.append(text)

    article_text = "\n".join(parts).strip()

    print("Текст статьи собран, длина:", len(article_text))
    return article_text
