# src/summarizer.py

import os
import httpx
from config import TOPICS, MAX_ITEMS_PER_TOPIC, SUMMARY_LANGUAGE

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def call_llm(prompt: str) -> str:
    if GROQ_API_KEY:
        return _call_groq(prompt)
    else:
        raise ValueError("no LLM API key found — set GROQ_API_KEY in .env")


def _call_groq(prompt: str) -> str:
    r = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "content-type":  "application/json",
        },
        json={
            "model":              "llama-3.3-70b-versatile",
            "messages":           [{"role": "user", "content": prompt}],
            "max_completion_tokens": 200,
            "temperature":        0.3,
        },
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if "choices" not in data:
        raise ValueError(f"unexpected groq response: {data}")
    return data["choices"][0]["message"]["content"]


def assign_topic(item: dict) -> str | None:
    text = (item["title"] + " " + item["summary"]).lower()
    for topic, keywords in TOPICS.items():
        if any(kw in text for kw in keywords):
            return topic
    return None


def filter_and_summarize(items: list[dict]) -> dict[str, list]:
    tagged = []
    for item in items:
        topic = assign_topic(item)
        if topic:
            item["topic"] = topic
            tagged.append(item)

    print(f"[summarizer] {len(tagged)}/{len(items)} items matched a topic")

    grouped: dict[str, list] = {topic: [] for topic in TOPICS}
    for item in tagged:
        bucket = grouped[item["topic"]]
        if len(bucket) < MAX_ITEMS_PER_TOPIC:
            bucket.append(item)

    for topic, bucket in grouped.items():
        for item in bucket:
            item["ai_summary"] = _summarize_item(item)

    return {t: b for t, b in grouped.items() if b}


def _summarize_item(item: dict) -> str:
    prompt = f"""You are an AI news curator writing for a junior AI engineer.
Summarize this item in 2 sentences in {SUMMARY_LANGUAGE}.
Be concrete — mention names, numbers, why it matters for someone building AI products.
Never start with "This article" or "The author".

Title: {item['title']}
Source: {item['source']}
Content: {item['summary'][:800]}

2-sentence summary:"""

    try:
        return call_llm(prompt)
    except Exception as e:
        print(f"[summarizer] LLM failed for '{item['title']}': {e}")
        return item["summary"][:200]