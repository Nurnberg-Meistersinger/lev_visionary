import json
import requests

from config import LLM_API_KEY, LLM_ENDPOINT, LLM_MODEL

def generate_summary(text):
    prompt = f"""
Ты — профессиональный редактор технологических новостей.

ВАЖНО: Весь ответ должен быть ТОЛЬКО на русском языке!

Проанализируй статью и создай три вида резюме:

1) TLDR — СТРОГО 2 предложения (максимум 200 символов)
   • Максимально ёмко передай суть статьи
   • Без вводных слов и воды
   • Только русский язык!

2) Summary — 5-7 предложений
   • Развернутое описание ключевых идей
   • Только русский язык!

3) Bullet Points — СТРОГО 4-5 пунктов
   • Каждый пункт: одна конкретная мысль
   • Максимум 100 символов на пункт
   • Без вводных слов
   • Только русский язык!

Верни строго JSON формата (без markdown блоков):
{{
  "tldr": "Краткое описание на русском, максимум 2 предложения",
  "summary": "Развернутое описание на русском, 5-7 предложений",
  "bullet_points": [
    "Первый ключевой тезис на русском",
    "Второй ключевой тезис на русском",
    "Третий ключевой тезис на русском",
    "Четвёртый ключевой тезис на русском"
  ]
}}

КРИТИЧЕСКИ ВАЖНО: ВСЁ НА РУССКОМ ЯЗЫКЕ!
"""

    headers = {
        "Content-Type": "application/json"
    }
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "user", "content": prompt + "\n\nARTICLE:\n" + text}
        ],
        "stream": False
    }

    r = requests.post(LLM_ENDPOINT, headers=headers, json=payload)
    r.raise_for_status()

    # Обработка NDJSON (если Ollama вернул несколько строк JSON)
    text_response = r.text.strip()
    if '\n' in text_response:
        # Берем последнюю строку (финальный ответ)
        lines = [line for line in text_response.split('\n') if line.strip()]
        raw = json.loads(lines[-1])
    else:
        raw = r.json()

    try:
        content = raw["choices"][0]["message"]["content"]

        # Удаляем markdown блоки ```json ... ```
        content = content.replace("```json", "").replace("```", "").strip()

        # Пытаемся найти JSON объект в тексте
        start = content.find("{")
        end = content.rfind("}")

        if start != -1 and end != -1:
            json_text = content[start:end+1]
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
        print("RAW OUTPUT:", raw)
        return {
            "tldr": "Недоступно",
            "summary": "Недоступно",
            "bullet_points": []
        }
