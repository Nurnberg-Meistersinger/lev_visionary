import json
import os

from tc_reader import fetch_latest_articles
from article_parser import extract_article_text
from summarizer import generate_summary
from telegram_sender import send_message
from config import MAX_ITEMS


PROCESSED_FILE = "processed_news.json"


# -------------------------
# Загрузка обработанных slug
# -------------------------
def load_processed():
    if not os.path.exists(PROCESSED_FILE):
        return set()
    with open(PROCESSED_FILE, "r") as f:
        return set(json.load(f))


# -------------------------
# Сохранение обработанных slug
# -------------------------
def save_processed(processed):
    with open(PROCESSED_FILE, "w") as f:
        json.dump(sorted(list(processed)), f, indent=2)


# -------------------------
# Основная логика
# -------------------------
def main():
    processed = load_processed()
    print("Processed loaded:", processed)

    items = fetch_latest_articles(limit=MAX_ITEMS)
    print(f"Fetched {len(items)} latest TechCrunch articles")

    for item in items:
        slug = item["slug"]

        # Пропустить уже обработанные
        if slug in processed:
            print(f"Skip already processed: {slug}")
            continue

        print("\n--- Processing:", slug)

        # Извлечение текста статьи
        text = extract_article_text(item["link"])
        print("Article length:", len(text))

        if not text:
            print("No article text — skipping")
            continue

        # Генерация TL;DR + Summary
        tldr, summary = generate_summary(text)

        # Формирование сообщения
        message = f"""
📰 TechCrunch Venture

📌 {item['title']}
🔗 {item['link']}

━━━━━━━━━━━━━━

⚡ TL;DR:
{tldr}

━━━━━━━━━━━━━━

🧠 Summary:
{summary}

━━━━━━━━━━━━━━
#techcrunch #venture
"""

        # Отправка сообщения
        send_message(message)
        print("📨 Sent to Telegram")

        # Обновление списка обработанных
        processed.add(slug)
        save_processed(processed)
        print("✔ Processed updated:", processed)


# -------------------------
# Точка входа
# -------------------------
if __name__ == "__main__":
    main()
