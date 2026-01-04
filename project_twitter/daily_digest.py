from llm_filter import analyze_tweets

def build_digest(all_posts):
    merged = []
    for acc, posts in all_posts.items():
        for p in posts:
            merged.append({
                "id": p["id"],
                "url": p["url"],
                "text": p["text"],
                "account": acc
            })

    analysis = analyze_tweets(merged)
    important = analysis["important"]

    text = "<b>Ключевые посты X за сегодня</b>\n"
    text += "━━━━━━━━━━━━━━━━━━\n\n"

    for item in important:
        text += f"• <b>{item['summary']}</b>\n"
        text += f"{item['url']}\n"
        text += "Инсайты:\n"
        for ins in item["insights"]:
            text += f"  – {ins}\n"
        text += "\n"

    text += "━━━━━━━━━━━━━━━━━━\n"
    text += "<i>Автоматический AI-дайджест по X</i>\n"
    text += "#x_digest\n\n"

    return text
