import json
import traceback

from rss_reader import fetch_rss
from article_parser import extract_article_text
from summarizer import generate_summary
from telegram_sender import send_message

PROCESSED_FILE = "processed_news.json"


def load_processed():
    try:
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()


def save_processed(ids):
    try:
        with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(list(ids)), f, ensure_ascii=False, indent=2)
        print("✔ processed обновлён:", ids)
    except Exception as e:
        print("❌ Ошибка сохранения processed:", e)


def run():
    print("\n=== Запуск мониторинга a16z Daily Newsletter ===")

    entries = fetch_rss()
    print(f"Найдено новостей: {len(entries)}")

    processed = load_processed()
    print("Уже обработано:", processed)

    for entry in entries:

        slug = entry.id.strip()
        print("\n--- Новая проверка ---")
        print("Slug:", slug)

        if not slug:
            print("⚠ Пустой slug — пропуск")
            continue

        if slug in processed:
            print("⏭ Уже обработано:", slug)
            continue

        print("Заголовок:", entry.title)
        print("URL:", entry.link)

        # 1) Парсим статью
        text = extract_article_text(entry.link)
        print("Текст, длина:", len(text))

        if not text.strip():
            print("⚠ Пустой текст — пропуск")
            continue

        # 2) Summary (одна строка с TLDR + Summary)
        summary = generate_summary(text)
        print("SUMMARY:", repr(summary))

        if not summary.strip():
            print("⚠ Пустое summary — пропуск")
            continue

        # 3) Telegram сообщение
        message = (
            f"📰 <b>a16z Daily News</b>\n\n"
            f"📌 <b>{entry.title}</b>\n"
            f"🔗 {entry.link}\n\n"
            f"━━━━━━━━━━━━━━\n\n"
            f"{summary}\n\n"
            f"━━━━━━━━━━━━━━\n"
            f"#a16z #news"
        )

        try:
            send_message(message)
            print("📨 Отправлено в Telegram.")
        except Exception as e:
            print("❌ Telegram ошибка:", e)
            traceback.print_exc()
            continue

        # 4) Сохраняем slug
        processed.add(slug)
        save_processed(processed)

    print("\n=== Готово ===")


if __name__ == "__main__":
    run()
