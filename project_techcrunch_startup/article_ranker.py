import json
import requests

from config import LLM_API_KEY, LLM_ENDPOINT, LLM_MODEL


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
Ты — аналитический ИИ, который изучает статьи о стартапах, технологиях и венчурном капитале.
Тебе дается список статей из TechCrunch Startups. Твоя задача:

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

{
  "top_articles": [
    {
      "slug": "строка",
      "importance": число,
      "reason": "краткое объяснение важности (1-2 предложения на русском)"
    }
  ]
}

Ни комментариев, ни объяснений — только JSON.

Вот статьи для анализа:
###
{}
###
""".format(articles_json)

    headers = {
        "Content-Type": "application/json"
    }
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    response = requests.post(
        LLM_ENDPOINT,
        headers=headers,
        json={
            "model": LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
    )
    response.raise_for_status()

    # Обработка NDJSON (если Ollama вернул несколько строк JSON)
    text_response = response.text.strip()
    if '\n' in text_response:
        lines = [line for line in text_response.split('\n') if line.strip()]
        data = json.loads(lines[-1])
    else:
        data = response.json()

    content = data["choices"][0]["message"]["content"].strip()

    # Удаляем markdown блоки
    content = content.replace("```json", "").replace("```", "").strip()

    # Находим JSON
    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(f"LLM вернул не-JSON:\n{content}")

    json_text = content[start:end+1]

    try:
        result = json.loads(json_text)
        top_articles = result.get("top_articles", [])

        # Возвращаем список slug'ов
        return [article["slug"] for article in top_articles]
    except Exception as e:
        raise ValueError(
            f"Не удалось разобрать JSON.\n\n"
            f"Исходный ответ модели:\n{content}\n\n"
            f"Выделенный JSON:\n{json_text}"
        ) from e
