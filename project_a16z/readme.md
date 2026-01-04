README — a16z Daily Newsletter Auto Monitor

Этот проект автоматически:

Сканирует ленту новостей a16z Daily Newsletter

Извлекает текст статьи напрямую из HTML (Substack)

Создаёт краткое summary при помощи локального или удалённого LLM

Публикует summary в Telegram-канал

Запоминает обработанные статьи, чтобы не отправлять их повторно

Проверяет только последние 2–3 статьи для оптимальной производительности

🚀 Функциональные возможности

Полностью автоматическая работа без RSS

Корректное извлечение содержания статей

Универсальный парсер ответов LLM (поддерживает любую модель, которая возвращает JSON)

Экономный режим: проверяет только последние N статей

Гарантированное сохранение обработанных slug’ов

Надёжная отправка в Telegram (HTML-safe)

Логи для отладки (включая сырые ответы LLM)

🧩 Структура проекта
project_a16z/
│
├── main.py                  # главный запуск бота
├── rss_reader.py            # парсер списка новостей со страницы
├── article_parser.py        # извлечение текста статьи
├── summarizer.py            # генерация summary через LLM
├── telegram_sender.py       # отправка сообщений в Telegram
├── config.py                # ключи и настройки
├── processed_news.json      # список обработанных статей (slug)
└── README.md                # документация

🔧 Установка и запуск
1. Клонирование проекта
git clone <repo-url>
cd project_a16z

2. Создание виртуального окружения
python -m venv .the_vis
source .the_vis/bin/activate   # macOS/Linux
.the_vis\Scripts\activate      # Windows PowerShell

3. Установка зависимостей
pip install requests beautifulsoup4


(при необходимости: pip install lxml)

🔑 Настройка — переменные окружения

Создайте `.env` в корне (`.gitignore` уже исключает его) или экспортируйте значения вручную.
Определите в нём:

```
LLM_ENDPOINT=http://127.0.0.1:11434/api/chat/completions
LLM_MODEL=gpt-oss:20b
LLM_API_KEY=                 # необязательно, если движок закрыт
TELEGRAM_TOKEN=82015...
TELEGRAM_CHAT_ID=@your_channel
```

`config.py` автоматически читает эти переменные, поэтому дополнительных изменений не требуется.

A16Z_DAILY_URL = "https://www.a16z.news/t/daily-newsletter"

▶ Запуск
python main.py


После первого запуска появятся:

processed_news.json — список обработанных slug’ов

summary в Telegram

логи в консоли

🔁 Как это работает
1. rss_reader.py

Загружает HTML список статей

Находит все ссылки вида /p/<slug>

Возвращает список объектов: slug, title, link

2. article_parser.py

Открывает страницу статьи

Находит <div class="body markup">

Извлекает текст абзацев и заголовков

3. summarizer.py

Отправляет текст на LLM endpoint

Универсально парсит JSON

Возвращает краткое summary

4. telegram_sender.py

Экранирует спецсимволы

Отправляет сообщение в HTML-формате

5. main.py

Проверяет только последние 3 статьи

Пропускает уже обработанные

После каждой публикации добавляет slug в JSON

Работает надёжно даже при обрывах

🔒 Processed Logic

Файл:

processed_news.json


пример:

[
  "charts-of-the-week-if-you-cant-join",
  "the-state-of-ai"
]


Если slug уже в списке — статья не будет отправлена повторно.

🔧 Изменение количества проверяемых статей

В main.py:

MAX_ITEMS = 3


Можно поставить:

1 — только самая свежая статья

3 — оптимум

5 — если хочешь проверять чуть глубже

🛠 Рекомендованные модели LLM
Название	Комментарий
google/gemma-2-27b-it	Лучшее качество резюме
qwen/qwen2.5-32b-instruct	Очень хорошее качество + дешево
openai/gpt-4.1-mini	Сбалансировано
gpt-oss:20b (Ollama)	Хороший компромисс для локального сервера
🧪 Типичный вывод программы
Найдено новостей: 12
Проверяем последние 3 статьи
---
Slug: the-state-of-ai
Текст, длина: 6751
SUMMARY: "Краткое описание ..."
📨 Отправлено в Telegram
✔ processed обновлён: {'the-state-of-ai'}

🧵 Автоматизация

Можно поставить cron / Windows Task Scheduler:

Linux:
*/20 * * * * /usr/bin/python3 /path/project_a16z/main.py

Windows:

Запускаем Task Scheduler → Create Task → Trigger: every 30 min.


— просто напиши!
