# The Visionary

The Visionary — это AI-платформа для автоматической агрегации и анализа контента, которая собирает информацию из разных источников, обрабатывает её с помощью больших языковых моделей (LLM) и отправляет автоматические дайджесты в Telegram. Проект помогает оставаться в курсе событий в технологиях, стартапах, венчурном капитале и блокчейне.

Оркестратор и набор самостоятельных скриптов, которые собирают тексты из `project_a16z`, `project_techcrunch_*` и `project_twitter`, пропускают через LLM и отсылают дайджесты в Telegram. Все LLM-запросы идут через настраиваемый endpoint (по умолчанию локальный Ollama), так что можно использовать собственную модель.

## Структура

| Проект | Источник | Что делает |
| --- | --- | --- |
| `project_a16z` | a16z Daily Newsletter | Скачивает свежие статьи и генерирует TL;DR + summary по заданному prompt’у. |
| `project_techcrunch_startup` | TechCrunch Startups | Тоже делает TL;DR + summary для нескольких публикаций. |
| `project_techcrunch_venture` | TechCrunch Venture | Аналогично, но для секции Venture. |
| `project_twitter` | X/Twitter | Подбирает важные твиты по группам аккаунтов, передаёт их в LLM и формирует структурированный дайджест. |

## Быстрый старт

1. Python 3.12+ и виртуальное окружение в корне:  
   - PowerShell: `python -m venv .the_vis; .\.the_vis\Scripts\Activate.ps1`  
   - macOS/Linux: `python -m venv .the_vis && source ./.the_vis/bin/activate`
2. `pip install -r requierements.txt`
3. Заполните `.env` (см. ниже) и `source .env`
4. Запускайте нужный проект через CLI `visionary.py run` (ниже).

`run_all.py` по-прежнему полезен для массового прогонки всех проектов: `python run_all.py`.

## CLI `visionary run`

```
python visionary.py run --all
python visionary.py run --twitter --palantir
python visionary.py run --twitter --cypherpunk
python visionary.py run --twitter --blockchain
python visionary.py run --twitter --venture
python visionary.py run --twitter --lifestyle
python visionary.py run --twitter --entrepreneurs
python visionary.py run --twitter --protectorium
python visionary.py run --twitter --hackers
python visionary.py run --twitter --all
python visionary.py run --a16z
python visionary.py run --techcrunch_startup
python visionary.py run --techcrunch_venture
```

- `--all` запускает `python run_all.py`, обходит все проекты один за другим.
- `--twitter --all` запускает `project_twitter` по всем наборам (аналогично `--per-set` ранее).
- `--twitter` требует указать один из наборов (`--palantir`, `--cypherpunk`, `--blockchain`, `--venture`, `--lifestyle`, `--entrepreneurs`, `--protectorium`, `--hackers`). Каждый флаг соответствует JSON-файлу в `project_twitter/account_sets`.
- `--a16z`, `--techcrunch_startup`, `--techcrunch_venture` запускают соответствующие скрипты.

## Наборы аккаунтов (`project_twitter/account_sets`)

Каждый JSON в этой директории описывает группу аккаунтов. Пример:

```json
{
  "name": "Palantir cluster",
  "description": "Руководство Palantir и близкие сообщества",
  "accounts": [
    {"handle": "PalantirTech", "name": "Palantir Technologies"},
    {"handle": "PalantirPrivacy", "name": "Palantir Privacy"}
  ]
}
```

Добавляй собственные файлы, чтобы расширить наборы (имена файлов привязаны к CLI-флагам).

### cookies для project_twitter

`project_twitter` использует JSON `cookies.json` (в корне `project_twitter`), чтобы получить доступ к X через Twikit. Перед запуском `visionary.py run --twitter …` положи туда значения `auth_token`, `ct0`, `twid`, `gt` из своего аккаунта. Без этого fetcher выдаст `FileNotFoundError` или ошибки аутентификации.

Пример:

```json
{
  "auth_token": "value",
  "ct0": "value",
  "twid": "u%3D123456789",
  "gt": "123456789"
}
```

Убедись, что файл не коммитишь (он уже в `.gitignore`).

## Ollama / LLM

1. Запусти Ollama (или другой совместимый HTTP API):
   ```bash
   ollama pull gpt-oss:20b
   ollama serve
   ```
2. Укажи точку доступа и модель в `.env`. Все сериализованные запросы отправляются как POST с `model` и `messages`.
3. LLM занимается только форматированием/резюмированием; сбор контента делается Python-скриптами.

## Конфигурация и `.env`

```
LLM_ENDPOINT=http://127.0.0.1:11434/api/chat/completions
LLM_MODEL=gpt-oss:20b
LLM_API_KEY=

TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
```

`LLM_API_KEY` нужен только при вызовах внешнего сервиса. Telegram-данные получаются через BotFather (`/newbot`) и `getUpdates`.

## Контроль над промптами

- `project_a16z/summarizer.py`, `project_techcrunch_startup/summarizer.py`, `project_techcrunch_venture/summarizer.py` задают prompt “Ты — профессиональный редактор…” и рендерят TLDR/summary в HTML для Telegram.
- `project_twitter/llm_filter.py` формирует prompt “Ты — аналитический ИИ…” и возвращает JSON с `important`, `insights`. Именно от него зависит текст итогового дайджеста Twitter.

Изменяй эти промпты, если хочешь другой тон, формат или структуру сообщений.
