# src/collector.py

import feedparser
import httpx
from datetime import datetime, timezone, timedelta
from config import RSS_FEEDS, YOUTUBE_CHANNELS, GITHUB_TOPICS, TWITTER_ACCOUNTS

YOUTUBE_API_KEY = None  # on branche ca plus tard via .env
GITHUB_TOKEN    = None  # idem

CUTOFF_HOURS = 24  # on ne garde que les articles des dernières 24h


def is_recent(entry) -> bool:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        return datetime.now(timezone.utc) - pub < timedelta(hours=CUTOFF_HOURS)
    return True  # si pas de date, on garde


def fetch_rss() -> list[dict]:
    items = []
    for url in RSS_FEEDS:
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
    if not YOUTUBE_API_KEY:
        print("[YouTube] no API key, skipping")
        return []
    items = []
    for channel in YOUTUBE_CHANNELS:
        try:
            # on passe par le flux RSS public YouTube — pas besoin d'API key en fait
            rss_url = f"https://www.youtube.com/feeds/videos.xml?user={channel.lstrip('@')}"
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:3]:  # max 3 vidéos par chaine
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
    try:
        headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
        for topic in GITHUB_TOPICS:
            url = f"https://api.github.com/search/repositories?q=topic:{topic}+pushed:>{(datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d')}&sort=stars&order=desc&per_page=3"
            r = httpx.get(url, headers=headers, timeout=10)
            for repo in r.json().get("items", []):
                items.append({
                    "source":      "GitHub",
                    "title":       repo["full_name"],
                    "url":         repo["html_url"],
                    "summary":     repo.get("description", ""),
                    "published":   repo.get("pushed_at", ""),
                    "stars":       repo.get("stargazers_count", 0),
                    "type":        "github",
                })
    except Exception as e:
        print(f"[GitHub] failed: {e}")
    return items


def fetch_twitter_rss() -> list[dict]:
    items = []
    for account in TWITTER_ACCOUNTS:
        try:
            # nitter RSS bridge — pas besoin de compte Twitter
            url = f"https://nitter.net/{account}/rss"
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:  # max 2 tweets par compte
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


def collect_all() -> list[dict]:
    print("collecting...")
    items = (
        fetch_rss()
        + fetch_youtube()
        + fetch_github()
        + fetch_twitter_rss()
    )
    print(f"collected {len(items)} items total")
    return items