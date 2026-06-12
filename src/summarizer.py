# src/summarizer.py

import os
import httpx
from config import TOPICS, MAX_ITEMS_PER_TOPIC

PROMPT_BY_TOPIC = {
    "agents": """You are an AI news curator for a junior AI engineer.
Summarize in 3 sentences in English.
Sentence 1: what happened concretely (names, numbers, tool names).
Sentence 2: why it matters for someone building AI products today.
Sentence 3: one thing to watch or try.""",

    "models": """You are an AI news curator for a junior AI engineer.
Summarize in 3 sentences in English.
Sentence 1: what model/release/benchmark, by who, key numbers.
Sentence 2: how it compares to what existed before.
Sentence 3: who should care and why.""",

    "tools": """You are an AI news curator for a developer who builds AI pipelines.
Summarize in 3 sentences in English.
Sentence 1: what tool/library/framework, what it does, who made it.
Sentence 2: what problem it solves better than existing options.
Sentence 3: how to get started or what to look at first.""",

    "industry": """You are an AI news curator for a junior consultant interested in AI strategy.
Summarize in 4 sentences in English.
Sentence 1: what happened (company, deal, product, amount).
Sentence 2: the business context — why this company, why now.
Sentence 3: what it means for the AI industry broadly.
Sentence 4: what a consultant should remember from this.""",

    "research": """You are an AI research explainer writing for a developer, not an academic.
Summarize in 3 sentences in English.
Sentence 1: what was published, by who, and the core claim.
Sentence 2: explain the key idea simply — no jargon.
Sentence 3: why practitioners should care and what it might change.""",

    "regulation": """You are a policy analyst writing for a developer who needs to stay compliant.
Summarize in 3 sentences in English.
Sentence 1: what regulation/law/decision, where, by who.
Sentence 2: what it concretely changes or prohibits.
Sentence 3: who is affected and what they need to do.""",
}

DEFAULT_PROMPT = """You are a news curator writing for a curious, intelligent reader.
Summarize in 3 sentences in English.
Give concrete facts, explain the context, and say why it matters."""


def _call_groq(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")
    r = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "content-type":  "application/json",
        },
        json={
            "model":                 "llama-3.3-70b-versatile",
            "messages":              [{"role": "user", "content": prompt}],
            "max_completion_tokens": 350,
            "temperature":           0.3,
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
        print(f"[summarizer] LLM failed for '{item['title']}': {e}")
        return item["summary"][:300]
