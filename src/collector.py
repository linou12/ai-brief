# src/collector.py

import os
import time
import feedparser
import httpx
from datetime import datetime, timezone, timedelta
from config import RSS_FEEDS, WORLD_RSS_FEEDS, YOUTUBE_CHANNELS, GITHUB_TOPICS, TWITTER_ACCOUNTS

try:
    import trafilatura
    HAS_TRAFILATURA = True
except ImportError:
    HAS_TRAFILATURA = False

CUTOFF_HOURS = 24


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
            # Only repos created in the last 30 days that were also pushed yesterday
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


def enrich_items(items: list[dict]) -> None:
    """Fetch full article text with trafilatura. Mutates items in-place."""
    if not HAS_TRAFILATURA:
        return
    enrichable = [i for i in items if i.get("type") not in ("youtube", "github")]
    print(f"[trafilatura] enriching {len(enrichable)} items...")
    enriched = 0
    for item in enrichable:
        try:
            downloaded = trafilatura.fetch_url(item["url"])
            if downloaded:
                text = trafilatura.extract(downloaded)
                if text and len(text) > len(item.get("summary", "")):
                    item["summary"] = text[:3000]
                    enriched += 1
        except Exception:
            pass
        time.sleep(0.3)
    print(f"[trafilatura] enriched {enriched}/{len(enrichable)} items")


def collect_all_ai() -> list[dict]:
    print("[collect] AI Brief...")
    items = fetch_rss() + fetch_youtube() + fetch_github()
    print(f"[collect] {len(items)} raw items")
    return items


def collect_all_world() -> list[dict]:
    print("[collect] World Brief...")
    items = fetch_rss(feeds=WORLD_RSS_FEEDS)
    print(f"[collect] {len(items)} raw items")
    return items


def collect_all() -> list[dict]:
    return collect_all_ai()
