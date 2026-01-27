import json
import anthropic

from config import LLM_API_KEY, LLM_MODEL

def generate_summary(text):
    prompt = f"""
КРИТИЧЕСКИ ВАЖНО: Твой ответ должен быть ТОЛЬКО валидным JSON объектом, без текста до или после!

Ты — профессиональный редактор технологических новостей. Проанализируй статью и верни ТОЛЬКО JSON:

{{
  "tldr": "2 предложения на русском (макс 200 символов)",
  "summary": "5-7 предложений на русском с ключевыми идеями",
  "bullet_points": [
    "Пункт 1 (макс 100 символов)",
    "Пункт 2 (макс 100 символов)",
    "Пункт 3 (макс 100 символов)",
    "Пункт 4 (макс 100 символов)"
  ]
}}

ТРЕБОВАНИЯ:
- TLDR: ровно 2 предложения, максимум 200 символов
- Summary: 5-7 предложений с ключевыми идеями
- Bullet points: строго 4-5 пунктов, каждый до 100 символов
- Весь текст ТОЛЬКО на русском языке
- БЕЗ markdown блоков (```json)
- БЕЗ комментариев или пояснений
- ТОЛЬКО валидный JSON объект!

ARTICLE:
{text}
"""

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

        # Удаляем markdown блоки ```json ... ```
        content = content.replace("```json", "").replace("```", "").strip()

        # Пытаемся найти JSON объект в тексте
        start = content.find("{")
        end = content.rfind("}")

        if start != -1 and end != -1:
            json_text = content[start:end+1]

            # Пробуем распарсить как есть
            try:
                parsed = json.loads(json_text)
            except json.JSONDecodeError:
                # Если не получилось, пытаемся починить типичные ошибки
                import re
                # Заменяем \" <пробел> " на ","
                json_text = re.sub(r'\\"\\s+"', '","', json_text)
                # Заменяем \\" на "," если после идет имя поля
                json_text = re.sub(r'\\"\\s+([a-z_]+)\\"\\s*:', r'","\1":', json_text)
                parsed = json.loads(json_text)

            # Возвращаем словарь с данными
            return {
                "tldr": parsed.get("tldr", ""),
                "summary": parsed.get("summary", ""),
                "bullet_points": parsed.get("bullet_points", [])
            }
        else:
            raise ValueError("No JSON found in content")

    except Exception as e:
        print("LLM PARSE ERROR:", e)
        if content:
            print("RAW CONTENT:", content)
        else:
            print("RAW CONTENT: N/A (error before response)")
        return {
            "tldr": "Недоступно",
            "summary": "Недоступно",
            "bullet_points": []
        }
