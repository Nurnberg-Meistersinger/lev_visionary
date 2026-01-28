import json
import anthropic

from .config import LLM_API_KEY, LLM_MODEL


def analyze_tweets(tweets, top_n=10):
    """
    Анализирует твиты и возвращает топ-N самых важных.

    Args:
        tweets: список твитов для анализа
        top_n: количество твитов для отбора (по умолчанию 10)

    Returns:
        dict с ключом "important" - список отобранных твитов
    """
    tweets_json = json.dumps(tweets, ensure_ascii=False, indent=2)

    prompt = """
Ты — аналитический ИИ, который изучает твиты в области технологий, стартапов и блокчейна.
Тебе дается список твитов за день. Твоя задача:

1. Оценить важность каждого твита по шкале 0–10
   Критерии важности (в порядке приоритета):
   - Конкретные новости: анонсы продуктов, сделки, партнёрства, релизы
   - Инсайдерская информация: данные из первых рук от руководителей компаний
   - Аналитика с цифрами: статистика, метрики, финансовые показатели
   - Стратегические прогнозы от экспертов индустрии

   НЕ выбирай: ретвиты без комментариев, личные мнения без фактов, шутки, мемы.

2. Выбрать ровно {top_n} самых важных твитов (importance >= 6).

3. По каждому выбранному твиту выдать (ВСЁ НА РУССКОМ ЯЗЫКЕ):
   • summary: Развёрнутое описание на русском (2-3 предложения, до 300 символов). Конкретика: имена, цифры, даты.
   • insights: 2-3 ключевых факта на русском (каждый до 100 символов)
   • short_tldr: ГЛАВНАЯ СУТЬ твита НА РУССКОМ в одной фразе (до 100 символов).
     Должен отвечать на вопрос "Что случилось?" или "О чём речь?"

     ПЛОХИЕ примеры (не делай так):
     - "About AI development" (на английском — НЕЛЬЗЯ)
     - "О развитии ИИ" (слишком абстрактно)
     - "Интересные мысли о технологиях" (ничего не говорит)

     ХОРОШИЕ примеры (на русском!):
     - "Контракт Palantir с NATO на $500M"
     - "Запуск AIP для коммерческих клиентов в Европе"
     - "Критика регулирования ИИ в ЕС: затормозит инновации"
     - "Прогноз: рынок enterprise AI вырастет в 3 раза к 2027"

4. Вернуть строго JSON:

{{
  "important": [
    {{
      "id": "строка",
      "url": "строка",
      "importance": число,
      "summary": "развёрнутое описание",
      "insights": ["факт 1", "факт 2"],
      "short_tldr": "главная суть в одной фразе"
    }}
  ]
}}

Ни комментариев, ни объяснений — только JSON.

Вот твиты для анализа:
###
{tweets}
###
""".format(top_n=top_n, tweets=tweets_json)

    content = None
    try:
        # Создаем клиент Claude
        client = anthropic.Anthropic(api_key=LLM_API_KEY)

        # Отправляем запрос к Claude API
        message = client.messages.create(
            model=LLM_MODEL,
            max_tokens=4096,
            temperature=0,  # Детерминированный результат
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Извлекаем текст ответа
        content = message.content[0].text.strip()

        # Удаляем markdown блоки ```json ... ```
        content = content.replace("```json", "").replace("```", "").strip()

        # Находим JSON: от первой { до последней }
        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(f"LLM вернул не-JSON:\n{content}")

        json_text = content[start:end+1]

        # Пробуем разобрать JSON
        return json.loads(json_text)
    except Exception as e:
        print("LLM PARSE ERROR:", e)
        if content:
            print("RAW CONTENT:", content)
        else:
            print("RAW CONTENT: N/A (error before response)")
        raise ValueError(
            f"Не удалось разобрать JSON.\n\n"
            f"Исходный ответ модели:\n{content if content else 'N/A'}\n\n"
            f"Ошибка: {e}"
        ) from e
