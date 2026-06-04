# ai-brief

Automated daily AI news digest — aggregates RSS feeds, GitHub Trending, HuggingFace Papers, and YouTube, summarized by Claude and delivered to your inbox every morning.

## What it does

Runs every morning at 7am via GitHub Actions. Collects the latest AI news from curated sources, filters and summarizes with Claude API, and sends a structured HTML email to your inbox — organized by topic so you can scan it in 2 minutes.

## Sources

- HuggingFace Papers (daily feed)
- GitHub Trending (AI/ML repos)
- RSS feeds: Hacker News, MIT Tech Review, The Batch, Wired AI
- YouTube: latest videos from curated AI channels
- X/Twitter: key accounts via RSS bridge

## Stack

- Python 3.11
- Claude API (summarization and filtering)
- Gmail API (delivery)
- GitHub Actions (scheduling)

## Setup

1. Clone the repo
2. Add your secrets to GitHub (see below)
3. Push — the workflow runs automatically every morning

## Secrets required

| Secret | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Claude API key |
| `GMAIL_CREDENTIALS` | Gmail OAuth2 credentials JSON |
| `RECIPIENT_EMAIL` | Your email address |

## Local development

```bash
pip install -r requirements.txt
cp .env.example .env
python newsletter.py
```

## License

MIT
