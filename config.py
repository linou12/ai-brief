RSS_FEEDS = [
    # releases & annonces — priorité absolue
    "https://openai.com/blog/rss/",
    "https://www.anthropic.com/rss.xml",
    "https://mistral.ai/feed.xml",
    "https://blog.google/technology/ai/rss/",
    "https://blogs.microsoft.com/ai/feed/",
    "https://meta.ai/blog/rss/",

    # agents & outils — ce que tu utilises au boulot
    "https://blog.langchain.dev/rss/",
    "https://blog.llamaindex.ai/rss/",
    "https://simonwillison.net/atom/everything/",
    "https://www.latent.space/feed",
    "https://eugeneyan.com/rss/",
    "https://lilianweng.github.io/lil-log/feed.xml",
    "https://karpathy.github.io/feed.xml",
    "https://www.interconnects.ai/feed",

    # industrie & cas d'usage
    "https://venturebeat.com/category/ai/feed/",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    "https://www.deeplearning.ai/the-batch/feed/",

    # github & HN
    "https://github.com/trending/python.atom",
    "https://hnrss.org/newest?q=AI+OR+LLM+OR+agent&points=100",

    # huggingface — que les tops
    "https://huggingface.co/papers.rss",
]

WORLD_RSS_FEEDS = [
    # France & francophone
    "https://www.lemonde.fr/rss/une.xml",
    "https://www.rts.ch/rss/info/",
    "https://www.20minutes.fr/feeds/rss/actu.xml",
    "https://www.courrierinternational.com/feed/all/rss.xml",

    # international — géopolitique
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.aljazeera.com/xml/rss/all.xml",

    # tech & économie mondiale
    "https://techcrunch.com/feed/",
    "https://www.ft.com/rss/home",

    # science & environnement
    "https://www.sciencedaily.com/rss/top/science.xml",
    "https://www.nature.com/nature.rss",
    "https://reporterre.net/spip.php?page=backend",  # écologie
]

WORLD_TOPICS = {
    "geopolitique": [
        "guerre", "conflit", "diplomatie", "élection", "président",
        "war", "conflict", "election", "diplomacy", "sanctions",
        "ukraine", "gaza", "chine", "russia", "china", "nato", "otan",
    ],
    "tech_economie": [
        "économie", "inflation", "croissance", "bourse", "marché",
        "economy", "market", "trade", "recession", "gdp", "startup",
        "tech", "silicon valley", "microsoft", "google", "apple",
    ],
    "societe_culture": [
        "société", "culture", "féminisme", "droits", "inégalité",
        "climate", "environnement", "grève", "manifestation",
        "social", "rights", "inequality", "protest", "strike",
    ],
    "science": [
        "découverte", "recherche", "espace", "santé", "médecine",
        "science", "discovery", "space", "health", "biology", "physics",
    ],
}

MAX_WORLD_ITEMS_PER_TOPIC = 3

YOUTUBE_CHANNELS = [
    "YannicKilcher",
    "AndrejKarpathy",
    "3blue1brown",
    "AIExplained",
    "WorldofAI",
    "TwoMinutePapers",
    "MatthewBerman",
    "Fireship",
]

TWITTER_ACCOUNTS = [
    "sama",
    "karpathy",
    "ylecun",
    "AnthropicAI",
    "emollick",
    "swyx",
    "simonw",
    "hwchase17",
    "LangChainAI",
    "nathanbenaich",
]

GITHUB_TOPICS = [
    "llm",
    "ai-agent",
    "rag",
    "llm-inference",
    "fine-tuning",
    "multimodal",
]

TOPICS = {
    "agents": [
        "agent", "agentic", "autonomous", "multi-agent", "tool use", "function calling",
        "workflow", "orchestration", "crewai", "autogen", "langgraph",
    ],
    "models": [
        "model", "llm", "gpt", "claude", "gemini", "llama", "mistral", "phi",
        "release", "benchmark", "fine-tun", "training", "weights", "open-source",
    ],
    "tools": [
        "framework", "library", "sdk", "api", "langchain", "llamaindex", "rag",
        "vector", "embedding", "inference", "deployment", "vllm", "ollama",
    ],
    "industry": [
        "funding", "startup", "acquisition", "partnership", "enterprise", "product",
        "launch", "company", "business", "revenue", "valuation", "investment",
    ],
    "research": [
        "paper", "research", "arxiv", "study", "experiment", "dataset", "evaluation",
        "alignment", "safety", "interpretability", "mechanistic", "scaling",
    ],
    "regulation": [
        "regulation", "law", "policy", "government", "eu", "act", "compliance",
        "ban", "copyright", "legal", "ethics", "bias", "risk", "governance",
    ],
}

MAX_ITEMS_PER_TOPIC = 4
SUMMARY_LANGUAGE = "english"
