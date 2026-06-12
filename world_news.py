import os
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
import httpx
from config import WORLD_RSS_FEEDS, WORLD_TOPICS, MAX_WORLD_ITEMS_PER_TOPIC, SUMMARY_LANGUAGE
from src.collector import fetch_rss
from src.sender import send

TOPIC_ICONS = {
    "geopolitique":    "🌍",
    "tech_economie":   "💰",
    "societe_culture": "🎭",
    "science":         "🔬",
}

TOPIC_LABELS = {
    "geopolitique":    "Géopolitique",
    "tech_economie":   "Tech & Économie",
    "societe_culture": "Société & Culture",
    "science":         "Science",
}


def _assign_topic(item: dict) -> str | None:
    text = (item["title"] + " " + item["summary"]).lower()
    for topic, keywords in WORLD_TOPICS.items():
        if any(kw in text for kw in keywords):
            return topic
    return None


def _summarize(item: dict) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return item["summary"][:200]
    prompt = f"""You are a world news curator writing for a curious, educated reader.
Summarize this news item in 2 sentences in {SUMMARY_LANGUAGE}.
Be concrete — mention names, places, stakes. Never start with "This article".

Title: {item['title']}
Source: {item['source']}
Content: {item['summary'][:800]}

2-sentence summary:"""
    try:
        r = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "content-type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_completion_tokens": 200,
                "temperature": 0.3,
            },
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        if "choices" not in data:
            return item["summary"][:200]
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[world] LLM failed for '{item['title']}': {e}")
        return item["summary"][:200]


def filter_and_summarize(items: list[dict]) -> dict[str, list]:
    grouped: dict[str, list] = {t: [] for t in WORLD_TOPICS}
    for item in items:
        topic = _assign_topic(item)
        if topic and len(grouped[topic]) < MAX_WORLD_ITEMS_PER_TOPIC:
            grouped[topic].append(item)

    matched = sum(len(v) for v in grouped.values())
    print(f"[world] {matched}/{len(items)} items matched a topic")

    for bucket in grouped.values():
        for item in bucket:
            item["ai_summary"] = _summarize(item)

    return {t: b for t, b in grouped.items() if b}


def build_email(digest: dict[str, list]) -> tuple[str, str]:
    date_str = datetime.now().strftime("%A %d %B %Y")
    total = sum(len(v) for v in digest.values())
    subject = f"World Brief — {date_str} — {total} stories to know"

    sections = ""
    for topic, items in digest.items():
        label = TOPIC_LABELS.get(topic, topic)
        icon = TOPIC_ICONS.get(topic, "•")
        cards = ""
        for item in items:
            badge = f'<span style="background:#f0f0f0;padding:2px 8px;border-radius:12px;font-size:12px;color:#666">{item["source"]}</span>'
            cards += f"""
            <div style="border:1px solid #eee;border-radius:10px;padding:16px 20px;margin-bottom:12px;background:#fff">
                <div style="margin-bottom:8px">{badge}</div>
                <a href="{item['url']}" style="font-size:16px;font-weight:600;color:#111;text-decoration:none;line-height:1.4">
                    {item['title']}
                </a>
                <p style="margin:10px 0 0;font-size:14px;color:#444;line-height:1.6">
                    {item.get('ai_summary') or item.get('summary', '')[:200]}
                </p>
            </div>"""
        sections += f"""
        <div style="margin-bottom:32px">
            <h2 style="font-size:18px;font-weight:700;color:#111;margin:0 0 14px;padding-bottom:8px;border-bottom:2px solid #f0f0f0">
                {icon} {label}
            </h2>
            {cards}
        </div>"""

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f6f6f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
    <div style="max-width:640px;margin:0 auto;padding:24px 16px">
        <div style="background:#1a3a5c;border-radius:14px;padding:28px 32px;margin-bottom:24px">
            <div style="font-size:12px;color:#8ab4d4;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px">
                Daily digest
            </div>
            <h1 style="margin:0;font-size:26px;font-weight:700;color:#fff">
                World Brief
            </h1>
            <div style="margin-top:8px;font-size:14px;color:#aac8e0">
                {date_str} &nbsp;·&nbsp; {total} stories
            </div>
        </div>
        {sections}
        <div style="text-align:center;padding:24px 0;font-size:12px;color:#aaa">
            Generated by ai-brief &nbsp;·&nbsp;
            <a href="https://github.com/linou12/ai-brief" style="color:#aaa">GitHub</a>
        </div>
    </div>
</body>
</html>"""
    return subject, html


def main():
    print("--- world-brief starting ---")
    print("collecting world news...")
    items = fetch_rss(feeds=WORLD_RSS_FEEDS)
    print(f"collected {len(items)} items")

    digest = filter_and_summarize(items)
    print("summarization done")

    subject, html = build_email(digest)
    print(f"subject: {subject}")

    send(subject, html)
    print("--- world-brief done ---")


if __name__ == "__main__":
    main()
