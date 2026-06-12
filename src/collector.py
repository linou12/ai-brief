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

try:
    import praw
    HAS_PRAW = True
except ImportError:
    HAS_PRAW = False

CUTOFF_HOURS = 24
REDDIT_AI_SUBS    = ["MachineLearning", "LocalLLaMA", "artificial", "ChatGPT", "singularity", "StableDiffusion"]
REDDIT_WORLD_SUBS = ["worldnews", "europe", "france", "environment", "science", "geopolitics", "economics"]


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
    try:
        github_token = os.getenv("GITHUB_TOKEN")
        headers = {"Authorization": f"token {github_token}"} if github_token else {}
        cutoff = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        for topic in GITHUB_TOPICS:
            url = f"https://api.github.com/search/repositories?q=topic:{topic}+pushed:>{cutoff}&sort=stars&order=desc&per_page=3"
            r = httpx.get(url, headers=headers, timeout=10)
            for repo in r.json().get("items", []):
                items.append({
                    "source":    "GitHub",
                    "title":     repo["full_name"],
                    "url":       repo["html_url"],
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


def _fetch_reddit(subreddits: list[str], min_score: int, max_per_sub: int) -> list[dict]:
    if not HAS_PRAW:
        return []
    client_id     = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    if not (client_id and client_secret):
        return []
    user_agent = os.getenv("REDDIT_USER_AGENT", "ai-brief/1.0")
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        items = []
        for sub_name in subreddits:
            try:
                count = 0
                for post in reddit.subreddit(sub_name).top(time_filter="day", limit=20):
                    if post.score < min_score:
                        continue
                    items.append({
                        "source":    f"r/{sub_name}",
                        "title":     post.title,
                        "url":       post.url,
                        "summary":   post.selftext[:1000] if post.selftext else post.title,
                        "published": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
                        "type":      "reddit",
                    })
                    count += 1
                    if count >= max_per_sub:
                        break
            except Exception as e:
                print(f"[Reddit] failed r/{sub_name}: {e}")
        return items
    except Exception as e:
        print(f"[Reddit] init failed: {e}")
        return []


def fetch_reddit_ai() -> list[dict]:
    return _fetch_reddit(REDDIT_AI_SUBS, min_score=50, max_per_sub=5)


def fetch_reddit_world() -> list[dict]:
    return _fetch_reddit(REDDIT_WORLD_SUBS, min_score=100, max_per_sub=5)


def _enrich_with_trafilatura(items: list[dict]) -> list[dict]:
    if not HAS_TRAFILATURA:
        return items
    # Skip sources that already have good native text
    enrichable = [i for i in items if i.get("type") not in ("youtube", "reddit", "github")]
    print(f"[trafilatura] enriching {len(enrichable)}/{len(items)} items...")
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
    print(f"[trafilatura] enriched {enriched} items with full text")
    return items


def collect_all_ai() -> list[dict]:
    print("[collect] AI Brief...")
    items = fetch_rss() + fetch_youtube() + fetch_github() + fetch_reddit_ai()
    print(f"[collect] {len(items)} raw items")
    return _enrich_with_trafilatura(items)


def collect_all_world() -> list[dict]:
    print("[collect] World Brief...")
    items = fetch_rss(feeds=WORLD_RSS_FEEDS) + fetch_reddit_world()
    print(f"[collect] {len(items)} raw items")
    return _enrich_with_trafilatura(items)


def collect_all() -> list[dict]:
    return collect_all_ai()
