import json
import anthropic

from config import LLM_API_KEY, LLM_MODEL


def rank_articles(articles):
    """
    Ранжирует статьи по важности и возвращает топ-5.

    Args:
        articles: список словарей [{"slug": ..., "title": ..., "link": ...}]

    Returns:
        список slug'ов топ-5 статей
    """
    articles_json = json.dumps(articles, ensure_ascii=False, indent=2)

    prompt = """
Ты — аналитический ИИ, который изучает статьи о технологиях, стартапах, венчурном капитале и ИИ.
Тебе дается список статей из a16z Daily Newsletter. Твоя задача:

1. Оценить важность каждой статьи по шкале 0–10
   Критерии оценки:
   • Новаторство идей и концепций
   • Влияние на технологическую индустрию
   • Стратегическая значимость для бизнеса и венчура
   • Глубина анализа и практическая польза
   • Актуальность для читателей, интересующихся технологиями

2. Выбрать ровно 5 самых важных статей (топ-5 по оценке).
   Если статей меньше 5, вернуть все доступные.

3. Вернуть строго JSON следующего вида:

{{
  "top_articles": [
    {{
      "slug": "строка",
      "importance": число,
      "reason": "краткое объяснение важности (1-2 предложения на русском)"
    }}
  ]
}}

Ни комментариев, ни объяснений — только JSON.

Вот статьи для анализа:
###
{articles}
###
""".format(articles=articles_json)

    content = None
    try:
        # Создаем клиент Claude
        client = anthropic.Anthropic(api_key=LLM_API_KEY)

        # Отправляем запрос к Claude API
        message = client.messages.create(
            model=LLM_MODEL,
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Извлекаем текст ответа
        content = message.content[0].text.strip()

        # Удаляем markdown блоки
        content = content.replace("```json", "").replace("```", "").strip()

        # Находим JSON
        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(f"LLM вернул не-JSON:\n{content}")

        json_text = content[start:end+1]

        result = json.loads(json_text)
        top_articles = result.get("top_articles", [])

        # Возвращаем список slug'ов
        return [article["slug"] for article in top_articles]
    except Exception as e:
        raise ValueError(
            f"Не удалось разобрать JSON.\n\n"
            f"Исходный ответ модели:\n{content if content else 'N/A'}\n\n"
            f"Ошибка: {e}"
        ) from e
