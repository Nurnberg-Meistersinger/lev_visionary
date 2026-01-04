import asyncio
import json
from typing import List, Dict
from twikit import Client

client = Client("en-US")


async def fetch_last_posts_async(username: str, count: int = 5) -> List[Dict]:
    """
    Работает точно с твоей версией twikit:
    - user.get_tweets() -> Result
    - твиты лежат в Result._Result__results
    """

    # Загружаем cookies
    with open("cookies.json", "r", encoding="utf-8") as f:
        cookies = json.load(f)
    client.set_cookies(cookies)

    # Загружаем пользователя
    user = await client.get_user_by_screen_name(username)

    # Получаем объект Result
    result = await user.get_tweets(tweet_type="Tweets")

    # ВАЖНО: список твитов тут
    tweets = result._Result__results

    # Берём первые N
    tweets = tweets[:count]

    parsed = []
    for t in tweets:
        parsed.append({
            "id": str(t.id),
            "text": t.text or "",
            "url": f"https://x.com/{username}/status/{t.id}",
            "date": str(t.created_at)
        })

    return parsed


def fetch_last_posts(username: str, count: int = 5) -> List[Dict]:
    return asyncio.run(fetch_last_posts_async(username, count))


if __name__ == "__main__":
    posts = fetch_last_posts("gonka_ai", 5)
    for p in posts:
        print("---")
        print(p["text"])
        print(p["url"])


