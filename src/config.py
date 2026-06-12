# config.py

RECIPIENT_EMAIL = "bousbinl@gmail.com"
SEND_HOUR = 7
SUMMARY_LANGUAGE = "english"

RSS_FEEDS = [
    # releases & annonces
    "https://openai.com/blog/rss.xml",
    "https://www.anthropic.com/rss.xml",
    "https://mistral.ai/news/rss",
    "https://blog.google/technology/ai/rss/",
    "https://blogs.microsoft.com/ai/feed/",

    # agents & outils
    "https://blog.langchain.dev/rss/",
    "https://blog.llamaindex.ai/feed",
    "https://simonwillison.net/atom/everything/",
    "https://www.latent.space/feed",

    # cas d'usage & industrie
    "https://venturebeat.com/category/ai/feed/",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",

    # github trending
    "https://github-trending-rss.fly.dev/daily?language=python",
    "https://hnrss.org/newest?q=AI+agent+tool&points=100",

    # huggingface — juste les tops
    "https://huggingface.co/papers/feed",
]

WORLD_RSS_FEEDS = [
    # géopolitique
    "https://www.lemonde.fr/rss/une.xml",
    "https://www.bbc.com/news/world/rss.xml",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://www.economist.com/rss",

    # tech & économie
    "https://www.ft.com/rss/home",
    "https://techcrunch.com/feed/",
    "https://www.bloomberg.com/feed/podcast/etf-iq.xml",

    # science & innovation
    "https://www.nature.com/nature.rss",
    "https://www.sciencedaily.com/rss/top/science.xml",

    # culture & société
    "https://www.theguardian.com/world/rss",
    "https://www.courrier international.com/rss",
]

YOUTUBE_CHANNELS = [
    "@YannicKilcher",
    "@AndrejKarpathy",
    "@3blue1brown",
    "@AIExplained",
    "@WorldofAI",
    "@TwoMinutePapers",
    "@SamuelBoschAI",
    "@aiDotEngineer",
    "@MatthewBerman",
    "@DataIndependent",
    "@AlexKremerAI",
    "@Fireship",
    "@ArjanCodes",
]

TWITTER_ACCOUNTS = [
    # OpenAI
    "sama",
    "gdb",
    "karenxcheng",
    # Anthropic
    "AnthropicAI",
    "darioamodei",
    "jackclarkSF",
    # research
    "ylecun",
    "karpathy",
    "goodfellow_ian",
    "fchollet",
    "jonasgeiping",
    "lateinteraction",
    # builders & indie
    "emollick",
    "_philschmid",
    "swyx",
    "simonw",
    "mattshumer_",
    "hwchase17",
    "LangChainAI",
    # VC / industry
    "benedictevans",
    "saranormous",
    "omooretweets",
    "nathanbenaich",
]

GITHUB_TOPICS = [
    "llm",
    "ai-agent",
    "rag",
    "llm-inference",
    "fine-tuning",
    "multimodal",
    "ai-tools",
]

TOPICS = {
    "agents": [
        "agent", "agentic", "crewai", "langgraph", "autogen",
        "tool use", "function calling", "multi-agent", "smolagents",
        "tool call", "orchestration", "workflow",
    ],
    "models": [
        "llm", "model", "release", "benchmark", "fine-tun",
        "qwen", "llama", "gemini", "gpt", "claude", "mistral",
        "phi", "deepseek", "o1", "o3", "reasoning model",
        "multimodal", "vision", "audio", "weights",
    ],
    "tools": [
        "vllm", "ollama", "mlops", "inference", "open source",
        "github", "repo", "framework", "library", "sdk",
        "openwebui", "litellm", "lmdeploy", "triton",
        "cursor", "claude code", "copilot",
    ],
    "industry": [
        "deploy", "enterprise", "finance", "health", "legal",
        "startup", "funding", "series", "acquisition",
        "consulting", "use case", "roi", "production",
    ],
    "research": [
        "paper", "arxiv", "study", "training", "dataset",
        "alignment", "safety", "rlhf", "dpo", "synthetic data",
        "scaling", "emergent", "evals", "benchmark",
    ],
    "regulation": [
        "eu ai act", "regulation", "policy", "governance",
        "compliance", "ethics", "bias", "copyright", "liability",
        "gdpr", "watermark",
    ],
}

MAX_ITEMS_PER_TOPIC = 4
MAX_TOTAL_ITEMS = 20