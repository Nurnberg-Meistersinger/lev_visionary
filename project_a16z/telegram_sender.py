import requests
import html
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, DISCUSSION_GROUP_ID


def escape_for_telegram(text: str) -> str:
    """
    Экранирует HTML-опасные символы, но позволяет использовать <b> и </b>.
    """
    # временно заменяем <b>...</b>, чтобы escape() их не сломал
    text = text.replace("<b>", "§B§").replace("</b>", "§/B§")

    # полностью экранируем весь текст
    text = html.escape(text)

    # возвращаем теги обратно
    text = text.replace("§B§", "<b>").replace("§/B§", "</b>")

    return text


def send_message(text: str):
    """
    Отправляет сообщение в канал.

    Args:
        text: Текст сообщения

    Returns:
        message_id: ID отправленного сообщения
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    safe_text = escape_for_telegram(text)

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": safe_text,
        "parse_mode": "HTML"
    }

    r = requests.post(url, json=payload)
    r.raise_for_status()

    # Возвращаем message_id для дальнейшей работы с комментариями
    return r.json()["result"]["message_id"]


def send_comment(text: str, message_id: int):
    """
    Отправляет комментарий к посту в Discussion Group.

    Args:
        text: Текст комментария
        message_id: ID сообщения в канале, к которому пишем комментарий

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
