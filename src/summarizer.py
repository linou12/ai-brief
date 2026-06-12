# src/summarizer.py

import os
import json
import re
import httpx
from config import TOPICS, MAX_ITEMS_PER_TOPIC

STOPWORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or",
    "is", "are", "was", "were", "with", "how", "why", "what", "new", "says",
    "say", "its", "this", "that", "from", "has", "have", "will", "can", "by",
}

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


def deduplicate(items: list[dict], threshold: float = 0.35) -> list[dict]:
    def key_words(title: str) -> set[str]:
        return {w for w in title.lower().split() if len(w) > 3 and w not in STOPWORDS}

    groups: list[list[dict]] = []
    used: set[int] = set()

    for i, item in enumerate(items):
        if i in used:
            continue
        words_i = key_words(item["title"])
        group = [item]
        for j, other in enumerate(items[i + 1:], i + 1):
            if j in used:
                continue
            words_j = key_words(other["title"])
            inter = words_i & words_j
            union = words_i | words_j
            if inter and union and len(inter) / len(union) >= threshold:
                group.append(other)
                used.add(j)
        used.add(i)
        groups.append(group)

    merged = []
    for group in groups:
        if len(group) == 1:
            merged.append(group[0])
        else:
            best = dict(max(group, key=lambda x: len(x.get("summary", ""))))
            best["source"] = " · ".join(dict.fromkeys(x["source"] for x in group))
            merged.append(best)

    removed = len(items) - len(merged)
    if removed:
        print(f"[dedup] merged {removed} duplicates → {len(merged)} unique items")
    return merged


def score_and_select(items: list[dict], topic: str, max_items: int) -> list[dict]:
    if len(items) <= max_items:
        return items

    titles_block = "\n".join(f"{i + 1}. {item['title']}" for i, item in enumerate(items))
    prompt = f"""Rate each headline 1-10 for importance and relevance to "{topic}" news.
10 = major development everyone should know. 1 = minor or irrelevant.
Return ONLY a JSON array of integers like [8, 3, 9, ...], one score per headline in the same order. No explanation.

Headlines:
{titles_block}

Scores:"""

    try:
        raw = _call_groq(prompt)
        match = re.search(r'\[[\d,\s]+\]', raw)
        if match:
            scores = json.loads(match.group())
            if len(scores) == len(items):
                top = sorted(scores, reverse=True)[:max_items]
                print(f"[scoring] topic={topic}: top scores {top}")
                scored = sorted(zip(scores, items), key=lambda x: x[0], reverse=True)
                return [item for _, item in scored[:max_items]]
    except Exception as e:
        print(f"[scoring] failed for topic={topic}: {e}")

    return items[:max_items]


def assign_topic(item: dict) -> str | None:
    text = (item["title"] + " " + item["summary"]).lower()
    for topic, keywords in TOPICS.items():
        if any(kw in text for kw in keywords):
            return topic
    return None


def filter_and_summarize(items: list[dict]) -> dict[str, list]:
    items = deduplicate(items)

    tagged: list[dict] = []
    for item in items:
        topic = assign_topic(item)
        if topic:
            item["topic"] = topic
            tagged.append(item)

    print(f"[summarizer] {len(tagged)}/{len(items)} items matched a topic")

    grouped: dict[str, list] = {topic: [] for topic in TOPICS}
    for item in tagged:
        grouped[item["topic"]].append(item)

    for topic, bucket in grouped.items():
        grouped[topic] = score_and_select(bucket, topic, MAX_ITEMS_PER_TOPIC)

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
