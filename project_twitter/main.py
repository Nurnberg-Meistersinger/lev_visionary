import argparse
import asyncio
import random

from accounts_loader import (
    load_accounts,
    list_available_sets,
    selected_sets,
)
from daily_digest import build_digest
from fetcher import fetch_last_posts_async
from post_tracker import filter_new_posts, mark_as_processed
from telegram_sender import send_message


def normalize_set_label(name: str) -> str:
    return name.replace("_", " ").title()


def list_sets_message(sets: list[str]) -> str:
    return "Наборы аккаунтов: " + ", ".join(normalize_set_label(name) for name in sets)


async def process_set_async(set_name: str) -> None:
    print(f"\n=== Набор: {normalize_set_label(set_name)} ===")
    accounts = load_accounts(set_name)
    total_posts = 0
    total_new_posts = 0
    all_collected = {}

    for acc in accounts:
        username = acc["handle"]
        name = acc["name"]
        print(f"\n🔍 Проверяем аккаунт: {name} (@{username})")

        posts = await fetch_last_posts_async(username, count=5)
        all_collected[username] = posts
        total_posts += len(posts)

        new_posts = filter_new_posts(posts)
        total_new_posts += len(new_posts)

        if new_posts:
            print(f"Найдено новых постов: {len(new_posts)}")
            for p in new_posts:
                print("🆕 Новый пост:", p["id"])
                print(p["text"])
                print("URL:", p["url"])
                mark_as_processed(p["id"])
        else:
            print("Нет новых постов.")

        delay = random.uniform(1.5, 3.0)
        print(f"⏳ Задержка {delay:.1f} сек...")
        await asyncio.sleep(delay)

    summary_text = (
        "<b>📊 Сводка за сегодня</b>\n"
        f"Всего постов собрано: <b>{total_posts}</b>\n"
        f"Новых постов: <b>{total_new_posts}</b>\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    print("\n" + summary_text)
    send_message(summary_text)

    digest = build_digest(all_collected)
    print("\n=== DAILY DIGEST ===\n", digest)
    send_message(f"<b>{normalize_set_label(set_name)}</b>\n{digest}")


async def run_async(args: argparse.Namespace) -> None:
    if args.per_set:
        sets = [s for s in list_available_sets() if s != "all"]
        print(list_sets_message(sets))
        for set_name in sets:
            await process_set_async(set_name)
        return

    target_set = args.set or selected_sets()[0]
    print(list_sets_message([target_set]))
    await process_set_async(target_set)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Собирает дайджест по Twitter/X-аккаунтам"
    )
    parser.add_argument(
        "--set",
        help="использовать только один набор из account_sets (по умолчанию берётся PROJECT_TWITTER_ACCOUNT_SETS или all)",
    )
    parser.add_argument(
        "--per-set",
        action="store_true",
        help="по очереди обрабатывать каждый набор (без объединения)",
    )
    return parser


def main() -> None:
    print(">>> project_twitter/main.py started")
    args = build_parser().parse_args()
    asyncio.run(run_async(args))


if __name__ == "__main__":
    main()
