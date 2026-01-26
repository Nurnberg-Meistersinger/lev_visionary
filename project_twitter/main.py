import argparse
import asyncio
import random

from accounts_loader import (
    load_accounts,
    list_available_sets,
    selected_sets,
)
from fetcher import fetch_last_posts_async
from llm_filter import analyze_tweets
from post_tracker import filter_new_posts, mark_as_processed
from telegram_sender import send_message, send_comment


def normalize_set_label(name: str) -> str:
    return name.replace("_", " ").title()


def list_sets_message(sets: list[str]) -> str:
    return "Наборы аккаунтов: " + ", ".join(normalize_set_label(name) for name in sets)


async def collect_posts_from_set(set_name: str) -> list:
    """
    Собирает все новые посты из набора аккаунтов.

    Returns:
        список новых постов
    """
    print(f"\n=== Набор: {normalize_set_label(set_name)} ===")
    accounts = load_accounts(set_name)
    all_new_posts = []

    for acc in accounts:
        username = acc["handle"]
        name = acc["name"]
        print(f"\n🔍 Проверяем аккаунт: {name} (@{username})")

        posts = await fetch_last_posts_async(username, count=5)

        new_posts = filter_new_posts(posts)

        if new_posts:
            print(f"Найдено новых постов: {len(new_posts)}")
            for p in new_posts:
                print("🆕 Новый пост:", p["id"])
                # Добавляем метаинформацию о категории и авторе
                p["category"] = set_name
                p["author"] = {
                    "name": acc["name"],
                    "organization": acc["organization"],
                    "title": acc["title"],
                    "handle": acc["handle"]
                }
                all_new_posts.append(p)
                mark_as_processed(p["id"])
        else:
            print("Нет новых постов.")

        delay = random.uniform(1.5, 3.0)
        print(f"⏳ Задержка {delay:.1f} сек...")
        await asyncio.sleep(delay)

    return all_new_posts


async def process_set_async(set_name: str, top_n: int = 10) -> None:
    """
    Обрабатывает один набор аккаунтов: собирает посты, фильтрует через LLM, публикует.

    Args:
        set_name: название набора
        top_n: количество лучших твитов для отбора (по умолчанию 10)
    """
    all_new_posts = await collect_posts_from_set(set_name)

    if not all_new_posts:
        print("\n📭 Нет новых постов для публикации")
        return

    print(f"\n📊 Всего собрано новых постов: {len(all_new_posts)}")

    # Фильтруем через LLM
    print(f"\n🤖 Отправка постов на LLM-анализ (топ-{top_n})...")
    try:
        result = analyze_tweets(all_new_posts, top_n=top_n)
        important_tweets = result.get("important", [])
        print(f"✅ LLM выбрал {len(important_tweets)} важных твитов")
    except Exception as e:
        print(f"❌ Ошибка LLM-анализа: {e}")
        # Fallback: берём первые top_n постов
        important_tweets = [
            {
                "id": p["id"],
                "url": p["url"],
                "importance": 6,
                "summary": p["text"][:200],
                "insights": [],
                "category": p.get("category", set_name)
            }
            for p in all_new_posts[:top_n]
        ]
        print(f"⚠️ Используем первые {len(important_tweets)} постов")

    if not important_tweets:
        print("\n📭 LLM не выбрал ни одного важного твита")
        return

    # Формируем дайджест
    digest_lines = [f"<b>📰 Digest: {normalize_set_label(set_name)}</b>\n"]

    for i, tweet in enumerate(important_tweets, 1):
        author = tweet.get("author", {})
        author_line = f"{author.get('name', 'Unknown')}, {author.get('organization', 'Unknown')}, {author.get('title', 'Unknown')} (@{author.get('handle', 'unknown')})"

        digest_lines.append(f"\n{i}️⃣ {author_line}")
        digest_lines.append(f"🔗 {tweet['url']}")
        digest_lines.append(f"📋 {tweet.get('short_tldr', 'Нет темы')}\n")

    digest_lines.append("\n━━━━━━━━━━━━━━")
    digest_lines.append("\n💬 Детальные инсайты в комментариях")
    digest_lines.append(f"\n#{set_name} #digest")

    digest_message = "\n".join(digest_lines)

    # Отправляем дайджест в канал
    digest_message_id = None
    try:
        print("\n📨 Отправка дайджеста в канал...")
        digest_message_id = send_message(digest_message)
        print(f"✅ Дайджест отправлен (message_id: {digest_message_id})")
    except Exception as e:
        print(f"❌ Ошибка отправки дайджеста: {e}")
        return

    if not digest_message_id:
        print("❌ Не удалось получить message_id дайджеста")
        return

    # Отправляем комментарии с инсайтами
    print("\n📝 Отправка комментариев в Discussion Group...")
    for i, tweet in enumerate(important_tweets, 1):
        author = tweet.get("author", {})
        author_line = f"{author.get('name', 'Unknown')}, {author.get('organization', 'Unknown')}, {author.get('title', 'Unknown')} (@{author.get('handle', 'unknown')})"

        comment_lines = [
            f"<b>{i}. {author_line}</b>\n",
            f"<b>Summary:</b>",
            f"{tweet.get('summary', 'Нет резюме')}\n",
            f"<b>Ключевые инсайты:</b>"
        ]

        insights = tweet.get("insights", [])
        if insights:
            for insight in insights:
                comment_lines.append(f"• {insight}")
        else:
            comment_lines.append("• Нет инсайтов")

        comment_lines.append(f"\n🔗 {tweet['url']}")

        comment_message = "\n".join(comment_lines)

        try:
            send_comment(comment_message, digest_message_id)
            print(f"  ✅ Комментарий {i}/{len(important_tweets)} отправлен")
        except Exception as e:
            print(f"  ❌ Ошибка отправки комментария {i}: {e}")


async def process_all_sets_async() -> None:
    """
    Обрабатывает все категории: берёт топ-2 из каждой, объединяет в один дайджест.
    """
    print("\n=== Режим ALL: топ-2 из каждой категории ===")

    all_sets = [s for s in list_available_sets() if s != "all"]
    all_important_tweets = []

    # Собираем топ-2 из каждой категории
    for set_name in all_sets:
        all_new_posts = await collect_posts_from_set(set_name)

        if not all_new_posts:
            print(f"\n📭 Нет новых постов в {set_name}")
            continue

        print(f"\n📊 Собрано {len(all_new_posts)} постов из {set_name}")

        # Берём топ-2 из категории
        print(f"\n🤖 LLM-анализ {set_name} (топ-2)...")
        try:
            result = analyze_tweets(all_new_posts, top_n=2)
            important_tweets = result.get("important", [])

            # Добавляем метку категории
            for tweet in important_tweets:
                tweet["category"] = set_name

            all_important_tweets.extend(important_tweets)
            print(f"✅ Выбрано {len(important_tweets)} твитов из {set_name}")
        except Exception as e:
            print(f"❌ Ошибка LLM-анализа для {set_name}: {e}")
            # Fallback: берём первые 2 поста
            fallback_tweets = [
                {
                    "id": p["id"],
                    "url": p["url"],
                    "importance": 6,
                    "summary": p["text"][:200],
                    "insights": [],
                    "category": set_name
                }
                for p in all_new_posts[:2]
            ]
            all_important_tweets.extend(fallback_tweets)
            print(f"⚠️ Используем первые 2 поста из {set_name}")

    if not all_important_tweets:
        print("\n📭 Нет твитов для публикации")
        return

    print(f"\n📊 Всего отобрано {len(all_important_tweets)} твитов из всех категорий")

    # Формируем единый дайджест с группировкой по категориям
    digest_lines = ["<b>📰 Digest: All Categories</b>\n"]

    # Группируем твиты по категориям
    tweets_by_category = {}
    for tweet in all_important_tweets:
        category = tweet.get("category", "unknown")
        if category not in tweets_by_category:
            tweets_by_category[category] = []
        tweets_by_category[category].append(tweet)

    # Формируем дайджест с заголовками категорий
    counter = 1
    for category, tweets in tweets_by_category.items():
        category_label = normalize_set_label(category)
        digest_lines.append(f"\n<b>Topic: {category_label}</b>")

        for tweet in tweets:
            author = tweet.get("author", {})
            author_line = f"{author.get('name', 'Unknown')}, {author.get('organization', 'Unknown')}, {author.get('title', 'Unknown')} (@{author.get('handle', 'unknown')})"

            digest_lines.append(f"{counter}️⃣ {author_line}")
            digest_lines.append(f"🔗 {tweet['url']}")
            digest_lines.append(f"📋 {tweet.get('short_tldr', 'Нет темы')}\n")
            counter += 1

    digest_lines.append("\n━━━━━━━━━━━━━━")
    digest_lines.append("\n💬 Детальные инсайты в комментариях")
    digest_lines.append("\n#all #digest")

    digest_message = "\n".join(digest_lines)

    # Отправляем дайджест
    digest_message_id = None
    try:
        print("\n📨 Отправка дайджеста в канал...")
        digest_message_id = send_message(digest_message)
        print(f"✅ Дайджест отправлен (message_id: {digest_message_id})")
    except Exception as e:
        print(f"❌ Ошибка отправки дайджеста: {e}")
        return

    if not digest_message_id:
        print("❌ Не удалось получить message_id дайджеста")
        return

    # Отправляем комментарии
    print("\n📝 Отправка комментариев в Discussion Group...")
    for i, tweet in enumerate(all_important_tweets, 1):
        author = tweet.get("author", {})
        author_line = f"{author.get('name', 'Unknown')}, {author.get('organization', 'Unknown')}, {author.get('title', 'Unknown')} (@{author.get('handle', 'unknown')})"
        category_label = normalize_set_label(tweet.get("category", "unknown"))

        comment_lines = [
            f"<b>{i}. [{category_label}] {author_line}</b>\n",
            f"<b>Summary:</b>",
            f"{tweet.get('summary', 'Нет резюме')}\n",
            f"<b>Ключевые инсайты:</b>"
        ]

        insights = tweet.get("insights", [])
        if insights:
            for insight in insights:
                comment_lines.append(f"• {insight}")
        else:
            comment_lines.append("• Нет инсайтов")

        comment_lines.append(f"\n🔗 {tweet['url']}")

        comment_message = "\n".join(comment_lines)

        try:
            send_comment(comment_message, digest_message_id)
            print(f"  ✅ Комментарий {i}/{len(all_important_tweets)} отправлен")
        except Exception as e:
            print(f"  ❌ Ошибка отправки комментария {i}: {e}")


async def run_async(args: argparse.Namespace) -> None:
    if args.per_set:
        # Обрабатываем каждый набор отдельно (топ-10 из каждого)
        sets = [s for s in list_available_sets() if s != "all"]
        print(list_sets_message(sets))
        for set_name in sets:
            await process_set_async(set_name, top_n=10)
        return

    target_set = args.set or selected_sets()[0]

    if target_set == "all":
        # Режим "all": топ-2 из каждой категории в один дайджест
        await process_all_sets_async()
    else:
        # Одна категория: топ-10 твитов
        print(list_sets_message([target_set]))
        await process_set_async(target_set, top_n=10)


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
