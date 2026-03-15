import requests
import html
from .config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, DISCUSSION_GROUP_ID


def escape_for_telegram(text: str) -> str:
    """
    Экранирует HTML-опасные символы, но сохраняет <b>, <i>, <u>.
    """

    replacements = {
        "<b>": "§B§", "</b>": "§/B§",
        "<i>": "§I§", "</i>": "§/I§",
        "<u>": "§U§", "</u>": "§/U§"
    }

    # временно убираем форматирование
    for k, v in replacements.items():
        text = text.replace(k, v)

    # экранируем HTML
    text = html.escape(text)

    # возвращаем форматирование
    for k, v in replacements.items():
        text = text.replace(v, k)

    return text


def send_message(text: str):
    """
    Отправляет сообщение в канал.
    Автоматически разбивает, если длина > 4096 символов.

    Args:
        text: Текст сообщения

    Returns:
        message_id: ID последнего отправленного сообщения (для комментариев)
    """

    MAX_LENGTH = 4096
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    safe_text = escape_for_telegram(text)

    # разбиваем длинные сообщения
    if len(safe_text) > MAX_LENGTH:
        parts = [
            safe_text[i:i+MAX_LENGTH]
            for i in range(0, len(safe_text), MAX_LENGTH)
        ]
    else:
        parts = [safe_text]

    last_message_id = None
    for part in parts:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": part,
            "parse_mode": "HTML"
        }

        r = requests.post(url, json=payload)
        r.raise_for_status()
        last_message_id = r.json()["result"]["message_id"]

    return last_message_id


def send_comment(text: str, message_id: int | None = None):
    """
    Отправляет комментарий к посту в Discussion Group.

    ВАЖНО: message_id игнорируется, т.к. Telegram не поддерживает reply между каналом и группой.
    Комментарии отправляются как обычные сообщения в группу.

    Args:
        text: Текст комментария
        message_id: Игнорируется (оставлен для обратной совместимости)

    Returns:
        message_id: ID отправленного комментария
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    safe_text = escape_for_telegram(text)

    payload = {
        "chat_id": DISCUSSION_GROUP_ID,
        "text": safe_text,
        "parse_mode": "HTML"
        # НЕ используем reply_to_message_id - он не работает между каналом и группой
    }

    r = requests.post(url, json=payload)
    r.raise_for_status()

    return r.json()["result"]["message_id"]
