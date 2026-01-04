import json
from typing import List, Dict
from twikit import Client

client = Client("en-US")


async def fetch_last_posts_async(username: str, count: int = 5) -> List[Dict]:
    with open("cookies.json", "r", encoding="utf-8") as f:
        cookies = json.load(f)
    client.set_cookies(cookies)

    user = await client.get_user_by_screen_name(username)

    result = await user.get_tweets(tweet_type="Tweets")

    tweets = result._Result__results  # список Tweet объектов
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

