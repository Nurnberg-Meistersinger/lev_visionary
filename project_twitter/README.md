X DAILY DIGEST — Автоматический AI-дайджест важных постов из X

Этот проект автоматически:

Парсит последние посты из указанных X-аккаунтов

Отбирает только важные и содержательные посты (через LLM)

Создаёт структурированный ежедневный дайджест

Отправляет итоговый текст в Telegram-канал

Запоминает обработанные посты, чтобы не повторяться

Проект полностью автономный и может запускаться вручную или по расписанию.

PIPELINE

X (Twitter)
→ Twikit (scraping)
→ LLM анализ важности
→ Формирование дайджеста
→ Telegram публикация

ТРЕБОВАНИЯ

Python 3.10+

Установить зависимости:
pip install -r requirements.txt

Аккаунт X (для получения cookies)

Telegram Bot Token

Telegram Chat ID (канал или личный чат)

LLM endpoint (`LLM_ENDPOINT`) и модель (`LLM_MODEL`). Запускайте локальный Ollama (`ollama serve`) или указывайте удалённый сервис.

СТРУКТУРА ПРОЕКТА

- `project_twitter/`
- `main.py` — основной pipeline: сбор → анализ → дайджест → Telegram
- `fetcher.py` — парсер X через Twikit
- `llm_filter.py` — LLM-анализ и выбор важных постов
- `daily_digest.py` — генерация итогового текста
- `telegram_sender.py` — отправка сообщений в Telegram
- `post_tracker.py` — хранение обработанных tweet_id
- `accounts_loader.py` — загрузка списка отслеживаемых аккаунтов по выбранным наборам
- `account_sets/` — JSON-файлы с группами аккаунтов (по направлениям)
- `processed_posts.json` — база обработанных постов
- `cookies.json` — cookies Twitter
- `config.py` — ключи и параметры

config.py (пример)

```python
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
LLM_ENDPOINT = os.getenv(
    "LLM_ENDPOINT",
    "http://127.0.0.1:11434/api/chat/completions"
)
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-oss:20b")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
```

Токены/ключи задаются через `.env` или экспортом: `LLM_ENDPOINT`, `LLM_MODEL`, `LLM_API_KEY`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`.

## Наборы аккаунтов

Папка `account_sets/` содержит JSON-файлы с группами аккаунтов (по направлениям). Каждая запись описывает, какие `handle` включены в набор. Список всех доступных наборов можно получить, вызвав:

```bash
python - <<'PY'
from project_twitter.accounts_loader import list_available_sets
print(list_available_sets())
PY
```

По умолчанию используется `PROJECT_TWITTER_ACCOUNT_SETS=all`. Чтобы собирать только конкретные направления, задайте окружение:

```
PROJECT_TWITTER_ACCOUNT_SETS=palantir,cypherpunk_progcrypto python project_twitter/main.py
```

Можно создавать собственные файлы в `account_sets/`, главное — сохранить структуру `{"name": "...", "accounts": [{"handle": "...", "name": "..."}]}`.

Новая команда `python project_twitter/main.py` поддерживает аргументы:

- `--set <имя>` — обработать только один набор из `account_sets` (игнорирует ENV).
- `--per-set` — пройтись по каждому набору по очереди и отправить отдельный дайджест для каждого.

Примеры:

```
python project_twitter/main.py --set palantir
python project_twitter/main.py --per-set
```

Совет: вместо прямого вызова `project_twitter/main.py` используйте глобальный CLI `visionary run`:

```
python visionary.py run --palantir
python visionary.py run --project twitter --per-set
```

cookies.json (пример)

{
"auth_token": "value",
"ct0": "value",
"twid": "u%3D123456789",
"gt": "123456789"
}

Cookies копируются из браузера.
Минимально необходимы: auth_token, ct0, twid, gt.

АЛГОРИТМ РАБОТЫ

Загрузка аккаунтов из выбранных JSON-наборов (`account_sets/`)

Получение последних постов каждого аккаунта (Twikit)

Фильтрация уже обработанных постов через processed.json

Передача новых постов в LLM для анализа важности

Генерация кратких резюме и инсайтов

Формирование красивого форматированного дайджеста

Отправка в Telegram

Сохранение tweet_id как обработанных

ФОРМАТ ДАЙДЖЕСТА

🔥 Ключевые посты за сегодня
━━━━━━━━━━━━━━━━━━

• Заголовок / краткое резюме
URL
Инсайты:
— insight 1
— insight 2
— insight 3

━━━━━━━━━━━━━━━━━━
Автоматический AI-дайджест по X

ЗАПУСК

Разовый запуск:
python main.py

Режим через cron / планировщик:
python main.py каждые N часов
