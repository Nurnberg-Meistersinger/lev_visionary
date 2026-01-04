import json
import requests

from config import LLM_API_KEY, LLM_ENDPOINT, LLM_MODEL

def generate_summary(text):
    prompt = f"""
Ты — профессиональный редактор технологических новостей.

Сделай два результата по тексту статьи:

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
        ]
    }

    r = requests.post(LLM_ENDPOINT, headers=headers, json=payload)

    raw = r.json()

    try:
        content = raw["choices"][0]["message"]["content"]
        parsed = json.loads(content)

        tldr = parsed.get("tldr", "")
        summary = parsed.get("summary", "")

        # Возвращаем ОДНУ строку — готовую для отправки в Telegram
        return f"🔥 <b>TLDR:</b> {tldr}\n\n<b>Summary:</b> {summary}"

    except Exception as e:
        print("LLM PARSE ERROR:", e)
        print("RAW OUTPUT:", raw)
        return "🔥 <b>TLDR:</b> недоступно\n\n<b>Summary:</b> недоступно"
