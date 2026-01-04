import json

import requests

from config import LLM_API_KEY, LLM_ENDPOINT, LLM_MODEL


def analyze_tweets(tweets):
    import json
    import requests

    tweets_json = json.dumps(tweets, ensure_ascii=False, indent=2)

    prompt = """
Ты — аналитический ИИ, который изучает твиты в области технологий, стартапов и блокчейна.
Тебе дается список твитов за день. Твоя задача:

1. Оценить важность каждого твита по шкале 0–10
   (учитывай новаторство идей, влияние на индустрию, стратегическую значимость, глубину мысли, практическую пользу).

2. Выбрать только те твиты, чья важность >= 6. Если твитов слишком много, выбери не более 10 самых важных.

3. По каждому выбранному твиту выдать:
   • краткое резюме (2-3 предложения, по-русски)
   • список ключевых идей / инсайтов (кратко, буллетами, по-русски)

4. Вернуть строго JSON следующего вида:

{{
  "important": [
    {{
      "id": "строка",
      "url": "строка",
      "importance": число,
      "summary": "краткое описание на русском",
      "insights": ["идея 1", "идея 2"]
    }}
  ]
}}

Ни комментариев, ни объяснений — только JSON.

Вот твиты для анализа:
###
{}
###
""".format(tweets_json)

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
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()

    # --------------------------
    # Удаляем markdown блоки ```json ... ```
    # --------------------------
    content = content.replace("```json", "").replace("```", "").strip()

    # --------------------------
    # Находим JSON: от первой { до последней }
    # --------------------------
    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(f"LLM вернул не-JSON:\n{content}")

    json_text = content[start:end+1]

    # --------------------------
    # Пробуем разобрать JSON
    # --------------------------
    try:
        return json.loads(json_text)
    except Exception as e:
        raise ValueError(
            f"Не удалось разобрать JSON.\n\n"
            f"Исходный ответ модели:\n{content}\n\n"
            f"Выделенный JSON:\n{json_text}"
        ) from e
