import json
import requests

from config import LLM_API_KEY, LLM_ENDPOINT, LLM_MODEL

def generate_summary(text):
    prompt = f"""
Ты — профессиональный редактор технологических новостей.

Сделай два результата по тексту статьи на русском:

1) TL;DR — 2-3 предложения, максимально кратко и ёмко.
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
        ]
    }

    r = requests.post(LLM_ENDPOINT, headers=headers, json=payload)

    raw = r.json()

    # Универсальный парсер ответа LLM
    try:
        content = raw["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return parsed.get("tldr", ""), parsed.get("summary", "")
    except Exception as e:
        print("LLM PARSE ERROR:", e)
        print("RAW OUTPUT:", raw)
        return "TLDR unavailable", "Summary unavailable"
