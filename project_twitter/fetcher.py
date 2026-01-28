from pathlib import Path
from typing import List, Dict
from twikit import Client
from twikit.errors import UserUnavailable

from .config import TWITTER_USERNAME, TWITTER_EMAIL, TWITTER_PASSWORD

# Путь к файлу cookies относительно этого файла
COOKIES_FILE = Path(__file__).parent / "cookies.json"

client = Client("en-US")
_logged_in = False


async def ensure_login():
    """
    Проверяет авторизацию и логинится если нужно.
    Cookies автоматически сохраняются и загружаются из файла.
    """
    global _logged_in

    if _logged_in:
        return

    # Если есть сохранённые cookies — пробуем загрузить
    if COOKIES_FILE.exists():
        try:
            client.load_cookies(str(COOKIES_FILE))
            _logged_in = True
            print("✅ Cookies загружены из файла")
            return
        except Exception as e:
            print(f"⚠️ Не удалось загрузить cookies: {e}")

    # Логинимся через credentials
    if not TWITTER_USERNAME or not TWITTER_EMAIL or not TWITTER_PASSWORD:
        raise ValueError(
            "Twitter credentials не настроены! "
            "Проверь TWITTER_USERNAME, TWITTER_EMAIL, TWITTER_PASSWORD в .env"
        )

    print("🔐 Логинимся в Twitter...")
    try:
        await client.login(
            auth_info_1=TWITTER_USERNAME,
            auth_info_2=TWITTER_EMAIL,
            password=TWITTER_PASSWORD
        )
        # Сохраняем cookies для следующих запусков
        client.save_cookies(str(COOKIES_FILE))
        _logged_in = True
        print("✅ Успешный логин, cookies сохранены")
    except Exception as e:
        raise ValueError(f"Ошибка логина в Twitter: {e}") from e


async def fetch_last_posts_async(username: str, count: int = 5) -> List[Dict]:
    """
    Получает последние посты пользователя.

    Args:
        username: Twitter username (без @)
        count: количество постов

    Returns:
        список словарей с полями id, text, url, date
    """
    await ensure_login()

    try:
        user = await client.get_user_by_screen_name(username)
    except UserUnavailable as e:
        print(f"⚠️  Аккаунт @{username} недоступен (заблокирован/удален): {e}")
        return []

    result = await user.get_tweets(tweet_type="Tweets")

    # Result поддерживает итерацию напрямую
    tweets = list(result)[:count]

    parsed = []
    for t in tweets:
        parsed.append({
            "id": str(t.id),
            "text": t.text or "",
            "url": f"https://x.com/{username}/status/{t.id}",
            "date": str(t.created_at)
        })

    return parsed
