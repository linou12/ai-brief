# src/collector.py

import os
import time
import feedparser
import httpx
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
from config import RSS_FEEDS, WORLD_RSS_FEEDS, YOUTUBE_CHANNELS, GITHUB_TOPICS, TWITTER_ACCOUNTS

try:
    import trafilatura
    HAS_TRAFILATURA = True
except ImportError:
    HAS_TRAFILATURA = False

CUTOFF_HOURS = 24

TAVILY_AI_QUERIES = [
    "AI agents LLM framework tool released this week",
    "new AI language model release benchmark 2025",
    "AI developer tools open source launch",
    "AI company startup funding product launch news",
    "AI research paper published arxiv this week",
]

TAVILY_WORLD_QUERIES = [
    "actualités géopolitique conflit diplomatie monde aujourd'hui",
    "économie finance marché tech actualités cette semaine",
    "société culture droits actualités France monde",
    "découverte scientifique recherche nature cette semaine",
]


def is_recent(entry) -> bool:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        return datetime.now(timezone.utc) - pub < timedelta(hours=CUTOFF_HOURS)
    return True


def fetch_rss(feeds: list[str] | None = None) -> list[dict]:
    items = []
    for url in (feeds or RSS_FEEDS):
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if not is_recent(entry):
                    continue
                items.append({
                    "source":    feed.feed.get("title", url),
                    "title":     entry.get("title", ""),
                    "url":       entry.get("link", ""),
                    "summary":   entry.get("summary", ""),
                    "published": entry.get("published", ""),
                    "type":      "rss",
                })
        except Exception as e:
            print(f"[RSS] failed {url}: {e}")
    return items


def fetch_youtube() -> list[dict]:
    items = []
    for channel in YOUTUBE_CHANNELS:
        try:
            rss_url = f"https://www.youtube.com/feeds/videos.xml?user={channel.lstrip('@')}"
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:3]:
                if not is_recent(entry):
                    continue
                items.append({
                    "source":    channel,
                    "title":     entry.get("title", ""),
                    "url":       entry.get("link", ""),
                    "summary":   entry.get("summary", ""),
                    "published": entry.get("published", ""),
                    "type":      "youtube",
                })
        except Exception as e:
            print(f"[YouTube] failed {channel}: {e}")
    return items


def fetch_github() -> list[dict]:
    items = []
    seen_urls: set[str] = set()
    try:
        github_token = os.getenv("GITHUB_TOKEN")
        headers = {"Authorization": f"token {github_token}"} if github_token else {}
        cutoff     = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        new_cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        for topic in GITHUB_TOPICS:
            url = (
                f"https://api.github.com/search/repositories"
                f"?q=topic:{topic}+pushed:>{cutoff}+created:>{new_cutoff}"
                f"&sort=stars&order=desc&per_page=5"
            )
            r = httpx.get(url, headers=headers, timeout=10)
            for repo in r.json().get("items", []):
                repo_url = repo["html_url"]
                if repo_url in seen_urls:
                    continue
                seen_urls.add(repo_url)
                items.append({
                    "source":    "GitHub",
                    "title":     repo["full_name"],
                    "url":       repo_url,
                    "summary":   repo.get("description", ""),
                    "published": repo.get("pushed_at", ""),
                    "stars":     repo.get("stargazers_count", 0),
                    "type":      "github",
                })
    except Exception as e:
        print(f"[GitHub] failed: {e}")
    return items


def fetch_twitter_rss() -> list[dict]:
    items = []
    for account in TWITTER_ACCOUNTS:
        try:
            url = f"https://nitter.net/{account}/rss"
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:
                if not is_recent(entry):
                    continue
                items.append({
                    "source":    f"@{account}",
                    "title":     entry.get("title", ""),
                    "url":       entry.get("link", ""),
                    "summary":   entry.get("summary", ""),
                    "published": entry.get("published", ""),
                    "type":      "twitter",
                })
        except Exception as e:
            print(f"[Twitter] failed @{account}: {e}")
    return items


def _fetch_tavily(queries: list[str], label: str) -> list[dict]:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return []
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        items = []
        seen_urls: set[str] = set()
        for query in queries:
            try:
                resp = client.search(query, max_results=3, days=2)
                for r in resp.get("results", []):
                    url = r.get("url", "")
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    domain = urlparse(url).netloc.replace("www.", "")
                    items.append({
                        "source":    domain or "Web",
                        "title":     r.get("title", ""),
                        "url":       url,
                        "summary":   r.get("content", ""),
                        "published": "",
                        "type":      "web",
                    })
                time.sleep(0.3)
            except Exception as e:
                print(f"[Tavily] query failed: {e}")
        print(f"[Tavily] {label}: {len(items)} items")
        return items
    except ImportError:
        print("[Tavily] tavily-python not installed, skipping")
        return []
    except Exception as e:
        print(f"[Tavily] failed: {e}")
        return []


def fetch_tavily_ai() -> list[dict]:
    return _fetch_tavily(TAVILY_AI_QUERIES, "AI")


def fetch_tavily_world() -> list[dict]:
    return _fetch_tavily(TAVILY_WORLD_QUERIES, "World")


def enrich_items(items: list[dict]) -> None:
    """Fetch full article text with trafilatura. Mutates items in-place."""
    if not HAS_TRAFILATURA:
        return
    # web items already have content from Tavily — skip them too
    enrichable = [i for i in items if i.get("type") not in ("youtube", "github", "web")]
    if not enrichable:
        return
    print(f"[trafilatura] enriching {len(enrichable)} items...")
    enriched = 0
    for item in enrichable:
        try:
            downloaded = trafilatura.fetch_url(item["url"])
            if downloaded:
                text = trafilatura.extract(downloaded)
                if text and len(text) > len(item.get("summary") or ""):
                    item["summary"] = text[:3000]
                    enriched += 1
        except Exception:
            pass
        time.sleep(0.3)
    print(f"[trafilatura] enriched {enriched}/{len(enrichable)} items")


def collect_all_ai() -> list[dict]:
    print("[collect] AI Brief...")
    items = fetch_rss() + fetch_youtube() + fetch_github() + fetch_tavily_ai()
    print(f"[collect] {len(items)} raw items")
    return items


def collect_all_world() -> list[dict]:
    print("[collect] World Brief...")
    items = fetch_rss(feeds=WORLD_RSS_FEEDS) + fetch_tavily_world()
    print(f"[collect] {len(items)} raw items")
    return items


def collect_all() -> list[dict]:
    return collect_all_ai()
