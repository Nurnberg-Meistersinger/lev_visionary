import json
import traceback
from pathlib import Path

from rss_reader import fetch_rss
from article_parser import extract_article_text
from article_ranker import rank_articles
from summarizer import generate_summary
from telegram_sender import send_message, send_comment

PROCESSED_FILE = Path(__file__).resolve().parent / "processed_news.json"


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


def run(limit=None):
    print("\n=== Запуск мониторинга a16z Daily Newsletter ===")

    entries = fetch_rss()
    print(f"Найдено новостей: {len(entries)}")

    processed = load_processed()
    print("Уже обработано:", processed)

    # 1) Собираем метаданные всех новых статей
    new_articles = []
    entries_map = {}  # slug -> entry для быстрого поиска

    for entry in entries:
        slug = entry.id.strip()

        if not slug:
            print("⚠ Пустой slug — пропуск")
            continue

        if slug in processed:
            print(f"⏭ Уже обработано: {slug}")
            continue

        new_articles.append({
            "slug": slug,
            "title": entry.title,
            "link": entry.link
        })
        entries_map[slug] = entry

    if not new_articles:
        print("\n📭 Нет новых статей для публикации")
        print("\n=== Готово ===")
        return

    print(f"\n📊 Найдено {len(new_articles)} новых статей")

    # 2) Ранжируем статьи через LLM и получаем топ-5
    if len(new_articles) <= 5:
        # Если статей 5 или меньше, берем все без ранжирования
        top_5_slugs = [a["slug"] for a in new_articles]
        print(f"✅ Статей {len(new_articles)} ≤ 5, берём все: {top_5_slugs}")
    else:
        # Если статей больше 5, используем LLM для выбора топ-5
        print("\n🤖 Отправка статей на ранжирование...")
        try:
            top_5_slugs = rank_articles(new_articles)
            print(f"✅ LLM выбрал топ-{len(top_5_slugs)} статей: {top_5_slugs}")
        except Exception as e:
            print(f"❌ Ошибка ранжирования: {e}")
            traceback.print_exc()
            # Fallback: берём первые 5 статей
            top_5_slugs = [a["slug"] for a in new_articles[:5]]
            print(f"⚠️  Используем первые {len(top_5_slugs)} статей: {top_5_slugs}")

    # Валидируем slug и дополняем недостающие
    valid_slugs = [s for s in top_5_slugs if s in entries_map]
    invalid_slugs = [s for s in top_5_slugs if s not in entries_map]

    if invalid_slugs:
        print(f"⚠️  LLM выбрал несуществующие slug: {invalid_slugs}")
        # Добавляем статьи которых нет в выбранных
        available_slugs = [a["slug"] for a in new_articles if a["slug"] not in valid_slugs]
        needed = 5 - len(valid_slugs)
        valid_slugs.extend(available_slugs[:needed])
        print(f"✅ Дополнено до {len(valid_slugs)} статей: {valid_slugs}")

    top_5_slugs = valid_slugs[:5]  # Гарантируем не больше 5

    # 3) Для топ-5 парсим полный текст и генерируем summary
    articles_data = []

    for slug in top_5_slugs:

        entry = entries_map[slug]

        print(f"\n--- Обработка статьи ---")
        print(f"Slug: {slug}")
        print(f"Заголовок: {entry.title}")
        print(f"URL: {entry.link}")

        # Парсим статью
        text = extract_article_text(entry.link)
        print(f"Текст, длина: {len(text)}")

        if not text.strip():
            print("⚠ Пустой текст — пропуск")
            continue

        # Генерируем summary с TLDR и bullet points
        summary_data = generate_summary(text)
        print(f"TLDR: {summary_data.get('tldr', '')[:100]}...")
        print(f"Bullet points: {len(summary_data.get('bullet_points', []))}")

        if not summary_data.get("tldr") or summary_data.get("tldr") == "Недоступно":
            print("⚠ Не удалось сгенерировать summary — пропуск")
            continue

        # Сохраняем данные статьи
        articles_data.append({
            "slug": slug,
            "title": entry.title,
            "link": entry.link,
            "tldr": summary_data.get("tldr", ""),
            "summary": summary_data.get("summary", ""),
            "bullet_points": summary_data.get("bullet_points", [])
        })

    if not articles_data:
        print("\n📭 Не удалось обработать ни одной статьи из топ-5")
        print("\n=== Готово ===")
        return

    print(f"\n📊 Успешно обработано {len(articles_data)} статей из топ-5")

    # 3) Формируем дайджест-пост
    digest_lines = ["📰 <b>a16z Daily Digest</b>\n"]

    for i, article in enumerate(articles_data, 1):
        digest_lines.append(f"\n{i}️⃣ <b>{article['title']}</b>")
        digest_lines.append(f"💡 {article['tldr']}")
        digest_lines.append(f"🔗 {article['link']}\n")

    digest_lines.append("\n━━━━━━━━━━━━━━")
    digest_lines.append("\n💬 Детальные выводы — в группе обсуждения")
    digest_lines.append("\n#a16z #digest")

    digest_message = "\n".join(digest_lines)

    # 4) Отправляем дайджест в канал
    try:
        print("\n📨 Отправка дайджеста в канал...")
        digest_message_id = send_message(digest_message)
        print(f"✅ Дайджест отправлен (message_id: {digest_message_id})")
    except Exception as e:
        print("❌ Ошибка отправки дайджеста:", e)
        traceback.print_exc()
        return

    # 5) Отправляем комментарии к каждой статье в Discussion Group
    print("\n📝 Отправка детальных комментариев в Discussion Group...")
    for i, article in enumerate(articles_data, 1):
        comment_lines = [
            f"<b>{i}. {article['title']}</b>\n",
            f"<b>Ключевые тезисы:</b>\n"
        ]

        if article["bullet_points"]:
            for point in article["bullet_points"]:
                comment_lines.append(f"• {point}")
        else:
            comment_lines.append(f"• {article['summary']}")

        comment_lines.append(f"\n🔗 {article['link']}")

        comment_message = "\n".join(comment_lines)

        try:
            send_comment(comment_message, digest_message_id)
            print(f"  ✅ Комментарий {i}/{len(articles_data)} отправлен")
        except Exception as e:
            print(f"  ❌ Ошибка отправки комментария {i}: {e}")
            traceback.print_exc()

    # 6) Сохраняем обработанные slugs
    for article in articles_data:
        processed.add(article["slug"])

    save_processed(processed)
    print(f"\n✅ Обработано и сохранено {len(articles_data)} статей")
    print("\n=== Готово ===")


if __name__ == "__main__":
    run()
