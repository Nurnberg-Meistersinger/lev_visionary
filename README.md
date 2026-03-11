# The Visionary

The Visionary — это AI-платформа для автоматической агрегации и анализа контента, которая собирает информацию из разных источников, обрабатывает её с помощью Claude API и отправляет дайджесты в Telegram.

## Структура

| Проект | Источник | Что делает |
| --- | --- | --- |
| `project_a16z` | a16z Daily Newsletter | Скачивает свежие статьи и генерирует TL;DR + summary |
| `project_techcrunch_startup` | TechCrunch Startups | TL;DR + summary для публикаций о стартапах |
| `project_techcrunch_venture` | TechCrunch Venture | TL;DR + summary для секции Venture |
| `project_twitter` | X/Twitter | Подбирает важные твиты по группам аккаунтов, анализирует через LLM |

## Быстрый старт

1. Python 3.12+ и виртуальное окружение:

   ```bash
   python -m venv .the_vis && source ./.the_vis/bin/activate
   ```

2. Установка зависимостей:

   ```bash
   pip install -r requirements.txt
   ```

3. Заполните `.env` (см. раздел Конфигурация)

4. Запуск:

   ```bash
   python visionary.py run --all
   ```

## CLI

### Запуск из командной строки

```bash
# Все проекты
python visionary.py run --all

# Twitter по наборам аккаунтов
python visionary.py run --twitter --palantir
python visionary.py run --twitter --cypherpunk
python visionary.py run --twitter --blockchain
python visionary.py run --twitter --venture
python visionary.py run --twitter --entrepreneurs
python visionary.py run --twitter --hackers
python visionary.py run --twitter --lifestyle
python visionary.py run --twitter --protectorium
python visionary.py run --twitter --ycombinator
python visionary.py run --twitter --all  # топ-2 из каждого набора

# Отдельные проекты
python visionary.py run --a16z
python visionary.py run --techcrunch_startup
python visionary.py run --techcrunch_venture
```

### Управление через Telegram-бота

Бот позволяет запускать все проекты удалённо через Telegram (требуется VPS).

**Команды:**

```bash
# Twitter дайджесты
/digest palantir          — дайджест Palantir (топ-10)
/digest blockchain        — дайджест Blockchain
/digest entrepreneurs     — дайджест Entrepreneurs
/digest hackers           — дайджест Hackers
/digest lifestyle         — дайджест Lifestyle
/digest protectorium      — дайджест Protectorium
/digest venture           — дайджест Venture
/digest ycombinator       — дайджест Y Combinator
/digest cypherpunk        — дайджест Cypherpunk
/digest all               — топ-2 из каждой категории Twitter

# Другие проекты
/digest a16z              — запустить a16z Daily Newsletter
/digest techcrunch_startup    — запустить TechCrunch Startups
/digest techcrunch_venture    — запустить TechCrunch Venture

# Кастомные наборы аккаунтов
/newset <name> handle1 handle2 ...  — создать кастомный набор
/addto <name> handle1 handle2 ...   — добавить аккаунты в кастомный набор
/delset <name>                      — удалить кастомный набор

# Информация
/projects                 — список всех проектов (встроенные + кастомные)
/help                     — справка
```

**Запуск бота на VPS:**

```bash
cd the_visionary
source .venv/bin/activate
python -m project_twitter.bot
```

## Конфигурация `.env`

```env
# Claude API (Anthropic)
LLM_MODEL=claude-haiku-4-5-20251001
LLM_API_KEY=sk-ant-api03-...

# Telegram
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=-100xxxxxxxxxx

# Twitter (для project_twitter)
TWITTER_USERNAME=your_twitter_handle
TWITTER_EMAIL=your_email@example.com
TWITTER_PASSWORD=your_password

# Bot admin (для управления через Telegram)
ADMIN_USER_ID=your_telegram_user_id

# Расписание автоматических дайджестов (опционально)
SCHEDULE_ENABLED=true
SCHEDULE_TIME=09:00
SCHEDULE_TIMEZONE=Europe/Moscow
```

Часовые пояса: `Europe/Moscow`, `UTC`, `Europe/Berlin`, `Asia/Tbilisi` и т.д. (стандарт IANA).

## Автозапуск по расписанию

При `SCHEDULE_ENABLED=true` бот каждый день в указанное время автоматически запускает все проекты **последовательно** и присылает тебе в личку отчёт:

```
📅 Плановый дайджест выполнен

✅ a16z
✅ techcrunch_startup
✅ techcrunch_venture
✅ twitter/palantir
✅ twitter/blockchain
...

✅ 12  ❌ 0  ⏱ ~24 мин
```

Порядок запуска: сначала три RSS-проекта (a16z, TechCrunch ×2) с задержкой 60 сек между ними, затем все Twitter-сеты с задержкой 90 сек между каждым. Ручные команды `/digest` работают независимо от расписания.

### Получение ключей

- **Claude API**: Регистрация на [console.anthropic.com](https://console.anthropic.com), пополнение баланса от $5
- **Telegram**:
  - Создать бота через [@BotFather](https://t.me/BotFather), получить `TELEGRAM_TOKEN`
  - Создать канал, добавить бота как админа, получить `TELEGRAM_CHAT_ID` (например, `-100xxxxxxxxxx`)
  - Узнать свой `ADMIN_USER_ID` через [@userinfobot](https://t.me/userinfobot) (для управления через команды бота)
- **Twitter**: Использовать credentials от аккаунта (рекомендуется отдельный аккаунт)

## Наборы аккаунтов Twitter

Файлы в `project_twitter/account_sets/*.json`:

```json
{
  "name": "Palantir",
  "description": "Руководство Palantir и близкие сообщества",
  "accounts": [
    {"handle": "PalantirTech", "name": "Palantir Technologies"},
    {"handle": "ssankar", "name": "Shankar Sankar, Palantir, CTO"}
  ]
}
```

Добавляйте свои файлы вручную — имя файла становится CLI-флагом. Либо используйте команды бота `/newset` / `/addto` / `/delset` для управления кастомными наборами без редактирования файлов.

Кастомные наборы отмечаются флагом `"custom": true` в JSON и отображаются отдельно в `/projects`. Они автоматически участвуют в `/digest all`.

## LLM и промпты

Все проекты используют Claude API (библиотека `anthropic`). Промпты настраиваются в:

- `project_*/summarizer.py` — генерация TL;DR и summary для статей
- `project_twitter/llm_filter.py` — анализ и отбор важных твитов

### Критерии отбора твитов

LLM оценивает твиты по шкале 0-10:

- Конкретные новости: анонсы, сделки, партнёрства
- Инсайдерская информация от руководителей
- Аналитика с цифрами и метриками
- Стратегические прогнозы экспертов

Не выбираются: ретвиты без комментариев, мнения без фактов, мемы.

## Стоимость

Claude Haiku: ~$0.25 за 1M input токенов, ~$1.25 за 1M output токенов.
При типичном использовании (несколько дайджестов в день): **~$3-6/месяц**.
