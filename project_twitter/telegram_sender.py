import requests
import html
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

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
    Отправляет сообщение в Telegram.
    Автоматически разбивает, если длина > 4096 символов.
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

    for part in parts:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": part,
            "parse_mode": "HTML"
        }

        r = requests.post(url, json=payload)
        r.raise_for_status()
