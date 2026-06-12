from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
from config import WORLD_TOPICS, MAX_WORLD_ITEMS_PER_TOPIC
from src.collector import collect_all_world
from src.sender import send
from src.summarizer import deduplicate, score_and_select, _call_groq

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

PROMPT_BY_TOPIC = {
    "geopolitique": """You are a world news curator writing for someone who wants to understand global news deeply.
Assume the reader may not have background context on this conflict or region.
Summarize in 4 sentences in English.
Sentence 1: what happened today concretely (who, where, what).
Sentence 2: the historical or political context needed to understand why this matters.
Sentence 3: who are the key actors and what are their interests.
Sentence 4: what to watch next.""",

    "tech_economie": """You are a tech and economics journalist writing for a smart generalist reader.
Summarize in 3 sentences in English.
Sentence 1: what happened (company, deal, number, product).
Sentence 2: the broader economic or industry context — why now, why this matters.
Sentence 3: who wins, who loses, or what shifts as a result.""",

    "societe_culture": """You are a progressive journalist writing for a curious, open-minded reader.
Summarize in 3 sentences in English.
Sentence 1: what happened concretely.
Sentence 2: the deeper social or structural issue behind this news.
Sentence 3: different perspectives or the ongoing debate around this.""",

    "science": """You are a science communicator writing for a curious non-expert.
Summarize in 3 sentences in English.
Sentence 1: what was discovered or published, by who, and the core finding.
Sentence 2: explain the concept simply — no jargon, use an analogy if helpful.
Sentence 3: why it matters for society or what could come next.""",
}

DEFAULT_PROMPT = """You are a world news curator writing for a curious, intelligent reader.
Summarize in 3 sentences in English.
Give concrete facts, explain the context, and say why it matters."""


def _assign_topic(item: dict) -> str | None:
    text = (item["title"] + " " + item["summary"]).lower()
    for topic, keywords in WORLD_TOPICS.items():
        if any(kw in text for kw in keywords):
            return topic
    return None


def _summarize(item: dict) -> str:
    topic = item.get("topic", "")
    system = PROMPT_BY_TOPIC.get(topic, DEFAULT_PROMPT)
    prompt = f"""{system}

Title: {item['title']}
Source: {item['source']}
Content: {item['summary'][:1200]}

Summary:"""

    try:
        return _call_groq(prompt)
    except Exception as e:
        print(f"[world] LLM failed for '{item['title']}': {e}")
        return item["summary"][:300]


def filter_and_summarize(items: list[dict]) -> dict[str, list]:
    items = deduplicate(items)

    grouped: dict[str, list] = {t: [] for t in WORLD_TOPICS}
    for item in items:
        topic = _assign_topic(item)
        if topic:
            item["topic"] = topic
            grouped[topic].append(item)

    matched = sum(len(v) for v in grouped.values())
    print(f"[world] {matched}/{len(items)} items matched a topic")

    for topic, bucket in grouped.items():
        grouped[topic] = score_and_select(bucket, topic, MAX_WORLD_ITEMS_PER_TOPIC)

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
            sources = item["source"]
            badge = " ".join(
                f'<span style="background:#f0f0f0;padding:2px 8px;border-radius:12px;font-size:12px;color:#666">{s.strip()}</span>'
                for s in sources.split("·")
            )
            cards += f"""
            <div style="border:1px solid #eee;border-radius:10px;padding:16px 20px;margin-bottom:12px;background:#fff">
                <div style="margin-bottom:8px">{badge}</div>
                <a href="{item['url']}" style="font-size:16px;font-weight:600;color:#111;text-decoration:none;line-height:1.4">
                    {item['title']}
                </a>
                <p style="margin:10px 0 0;font-size:14px;color:#444;line-height:1.6">
                    {item.get('ai_summary') or item.get('summary', '')[:300]}
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
    items = collect_all_world()

    digest = filter_and_summarize(items)
    print("summarization done")

    subject, html = build_email(digest)
    print(f"subject: {subject}")

    send(subject, html)
    print("--- world-brief done ---")


if __name__ == "__main__":
    main()
