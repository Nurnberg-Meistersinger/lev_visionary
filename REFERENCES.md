# Обзор литературы и аналогов

## 1. Научные работы

### 1.1 Автоматическое реферирование текста с помощью LLM

- **Jin et al. (2024)** — *"A Comprehensive Survey on Process-Oriented Automatic Text Summarization with Exploration of LLM-Based Methods"*
  Обзор методов автоматического реферирования текста, включая подходы на основе LLM: in-context learning, prompt engineering, few-shot learning. Показано, что LLM способны гибко переключаться между экстрактивным и абстрактивным реферированием без дообучения.
  [arxiv.org/abs/2403.02901](https://arxiv.org/abs/2403.02901)

- **ACM Computing Surveys (2025)** — *"A Systematic Survey of Text Summarization: From Statistical Methods to Large Language Models"*
  Систематический обзор эволюции методов суммаризации: от статистических подходов через нейросети к современным LLM. Релевантно для нашего проекта, так как The Visionary использует абстрактивное реферирование через Claude API.
  [dl.acm.org/doi/10.1145/3731445](https://dl.acm.org/doi/10.1145/3731445)

- **Abstractive Text Summarization: State of the Art, Challenges, and Improvements (2024)**
  Обзор текущего состояния абстрактивного реферирования, проблем (галлюцинации, потеря фактов) и путей улучшения. Мы решаем проблему галлюцинаций через строгий JSON-формат вывода и ограничения в промптах.
  [arxiv.org/html/2409.02413v1](https://arxiv.org/html/2409.02413v1)

### 1.2 Prompt Engineering и фильтрация контента

- **Sahoo et al. (2024)** — *"A Systematic Survey of Prompt Engineering in Large Language Models: Techniques and Applications"*
  Систематизация техник prompt engineering. В The Visionary применяются zero-shot промпты с жёстким JSON-форматом, few-shot примеры (в модуле анализа твитов) и детерминированная генерация (temperature=0).
  [arxiv.org/abs/2402.07927](https://arxiv.org/abs/2402.07927)

- **Li et al. (2025)** — *"A Comprehensive Taxonomy of Prompt Engineering Techniques for Large Language Models"*
  Таксономия техник промпт-инжиниринга. Наш проект реализует: constraint prompting (ограничения на длину, язык, формат), role prompting (роль "профессиональный tech-редактор"), structured output prompting (JSON-схемы).
  [link.springer.com/article/10.1007/s11704-025-50058-z](https://link.springer.com/article/10.1007/s11704-025-50058-z)

### 1.3 AI-агенты для журналистики

- **TeleFlash (2025)** — *"How can AI agents support journalists' work? An experiment with designing an LLM-driven intelligent reporting system"*
  Исследователи разработали систему, агрегирующую и анализирующую посты из Telegram-каналов с помощью LLM. Концептуально близка к The Visionary — оба проекта решают задачу автоматической фильтрации и суммаризации потока информации из социальных медиа.
  [arxiv.org/html/2510.01193v1](https://arxiv.org/html/2510.01193v1)

---

## 2. Аналоги на рынке

### 2.1 Open-source проекты

| Проект | Стек | Отличия от The Visionary |
| --- | --- | --- |
| [ai-news-bot](https://github.com/giftedunicorn/ai-news-bot) | Claude/DeepSeek + RSS + GitHub Actions | Только RSS, нет Twitter; доставка через email, нет Telegram-бота с управлением |
| [ai-news-aggregator](https://github.com/fanitarantsopoulou/ai-news-aggregator) | FastAPI + LangChain + ChromaDB + Ollama + Vue 3 | RAG-архитектура, локальные модели; веб-интерфейс вместо Telegram; нет соцсетей |
| [gpt-digest](https://github.com/zmactep/gpt-digest) | GPT + RSS | Только RSS → дайджест; нет ранжирования по важности, нет Twitter |
| [summary-gpt-bot](https://github.com/tpai/summary-gpt-bot) | GPT + Telegram | Суммаризация по запросу (URL/PDF/YouTube); не агрегатор, а on-demand инструмент |

### 2.2 No-code платформы (n8n workflows)

| Решение | Описание | Отличия |
| --- | --- | --- |
| [RSS + Claude → Discord/Slack](https://n8n.io/workflows/13527) | Claude Haiku для скоринга, Claude Sonnet для дайджеста | No-code; нет кастомизации Twitter-сетов; зависимость от n8n |
| [GPT-4o + DALL-E → Telegram](https://n8n.io/workflows/12048) | Дайджест с AI-иллюстрациями | Визуальный контент, но дороже и без Twitter-аналитики |
| [Llama 3.2 + RSS → Telegram](https://n8n.io/workflows/6011) | Локальная модель, privacy-first | Бесплатно, но качество суммаризации ниже Claude |

### 2.3 Коммерческие продукты

| Продукт | Что делает | Отличия |
| --- | --- | --- |
| [Feedly AI](https://feedly.com) | RSS-агрегатор с AI-фильтрацией (Leo AI) | $6–18/мес; нет Twitter-интеграции в бесплатном тарифе; нет Telegram-доставки |
| [Tweetsmash](https://www.tweetsmash.com) | Дайджесты Twitter-списков на email | Только Twitter, только email; нет LLM-ранжирования; платная подписка |
| [Tweet Hunter](https://tweethunter.io) | AI для создания и курирования контента в X | Ориентирован на создание контента, не на аналитику; $49+/мес |
| Telegram AI Summaries | Встроенная суммаризация чатов | Работает только внутри чатов Telegram, не агрегирует внешние источники |

---

## 3. Позиционирование The Visionary

### Ключевые отличия от аналогов

**Мультиисточниковая агрегация.** Большинство аналогов работают либо только с RSS, либо только с Twitter. The Visionary объединяет оба типа источников (a16z, TechCrunch, X/Twitter) в единый пайплайн.

**LLM-ранжирование по важности.** Вместо keyword-фильтрации или хронологической сортировки проект использует Claude для скоринга каждого материала по шкале 0–10 с обоснованием. Это снижает информационный шум.

**Кастомные Twitter-сеты.** Уникальная функция — создание и управление наборами аккаунтов прямо через Telegram-бота (`/newset`, `/addto`, `/delset`).

**Экономичность.** Использование Claude Haiku (~$0.02 за запуск) делает решение доступным: ~$3–7/мес включая VPS, против $6–49/мес у коммерческих аналогов.

**Автономность.** Полностью автоматический цикл: сбор → фильтрация → анализ → доставка, с ежедневным расписанием и Telegram-управлением.

---

## 4. Используемые технологии (документация)

| Технология | Назначение в проекте | Ссылка |
| --- | --- | --- |
| Anthropic Claude API | LLM для суммаризации и ранжирования | [docs.anthropic.com](https://docs.anthropic.com/) |
| python-telegram-bot | Telegram-бот и планировщик | [docs.python-telegram-bot.org](https://docs.python-telegram-bot.org/) |
| twikit | Парсинг Twitter/X без API | [github.com/d60/twikit](https://github.com/d60/twikit) |
| feedparser | Парсинг RSS/Atom | [feedparser.readthedocs.io](https://feedparser.readthedocs.io/) |
| BeautifulSoup4 | Извлечение текста из HTML | [crummy.com/software/BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) |
| Pydantic | Валидация данных | [docs.pydantic.dev](https://docs.pydantic.dev/) |
| tiktoken | Подсчёт токенов | [github.com/openai/tiktoken](https://github.com/openai/tiktoken) |
