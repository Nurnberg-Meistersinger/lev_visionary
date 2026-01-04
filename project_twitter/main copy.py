from daily_digest import build_digest
from fetcher import fetch_last_posts_async
from accounts_loader import load_accounts
from post_tracker import filter_new_posts, mark_as_processed
from telegram_sender import send_message
import asyncio

print(">>> main.py started")


async def process_all_accounts_async():
    accounts = load_accounts()
    print("Аккаунты загружены:", accounts)

    all_collected = {}
    total_posts = 0
    total_new_posts = 0

    for acc in accounts:
        username = acc["handle"]
        name = acc["name"]

        print(f"\n🔍 Проверяем аккаунт: {name} (@{username})")

        posts = await fetch_last_posts_async(username, count=5)

        # сохраняем все посты
        all_collected[username] = posts
        total_posts += len(posts)

        # фильтруем по processed.json
        new_posts = filter_new_posts(posts)
        total_new_posts += len(new_posts)

        if not new_posts:
            print("Нет новых постов.")
            continue

        print(f"Найдено новых постов: {len(new_posts)}\n")

        for p in new_posts:
            print("🆕 Новый пост:")
            print(p["text"])
            print("URL:", p["url"])
            print("ID:", p["id"])
            print("-----------")

            mark_as_processed(p["id"])

    # --- SUMMARY BLOCK → отправляем в Telegram ---
    summary_text = (
        "<b>📊 Сводка за сегодня</b>\n"
        f"Всего постов собрано: <b>{total_posts}</b>\n"
        f"Новых постов: <b>{total_new_posts}</b>\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    print(summary_text)
    send_message(summary_text)

    # --- BUILD DIGEST ---
    digest = build_digest(all_collected)

    print("\n=== DAILY DIGEST ===\n")
    print(digest)

    print("\n📤 Отправляем дайджест в Telegram...")
    send_message(digest)
    print("Готово! 🚀")


# run
asyncio.run(process_all_accounts_async())
