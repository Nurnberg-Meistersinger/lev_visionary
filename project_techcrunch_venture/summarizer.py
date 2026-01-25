import json
import requests

from config import LLM_API_KEY, LLM_ENDPOINT, LLM_MODEL

def generate_summary(text):
    prompt = f"""
Ты — профессиональный редактор технологических новостей.

Сделай два результата по тексту статьи на русском:

1) TLDR — 1–2 предложения, максимально кратко и ёмко.
2) Summary — 5–7 предложений, развернутое, но компактное резюме.

Верни строго JSON формата:
{{
  "tldr": "...",
  "summary": "..."
}}
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

    # Универсальный парсер ответа LLM
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
            return parsed.get("tldr", ""), parsed.get("summary", "")
        else:
            raise ValueError("No JSON found in content")
    except Exception as e:
        print("LLM PARSE ERROR:", e)
        print("RAW OUTPUT:", raw)
        return "TLDR unavailable", "Summary unavailable"
