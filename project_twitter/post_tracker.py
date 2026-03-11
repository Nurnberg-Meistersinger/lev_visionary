import json
from pathlib import Path
from typing import List

FILE_PATH = Path(__file__).resolve().parent / "processed_posts.json"


def load_processed() -> List[str]:
    """Загружает список обработанных твитов."""
    if not FILE_PATH.exists():
        return []
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("processed", [])
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_processed(processed_ids: List[str]):
    """Сохраняет список обработанных твитов."""
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump({"processed": processed_ids}, f, ensure_ascii=False, indent=2)


def mark_as_processed(tweet_id: str):
    """Добавляет твит в список обработанных."""
    processed = load_processed()
    if tweet_id not in processed:
        processed.append(tweet_id)
        save_processed(processed)


def filter_new_posts(posts: List[dict]) -> List[dict]:
    """Убирает твиты, которые уже были обработаны."""
    processed = load_processed()
    new_posts = [p for p in posts if p["id"] not in processed]
    return new_posts
