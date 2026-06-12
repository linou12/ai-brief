RSS_FEEDS = [
    # Major tech publications
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    "https://www.wired.com/feed/tag/artificial-intelligence/latest/rss",
    "https://www.technologyreview.com/feed/",
    # AI company blogs
    "https://openai.com/blog/rss/",
    "https://www.anthropic.com/rss.xml",
    "https://mistral.ai/feed.xml",
    "https://blog.langchain.dev/rss/",
    "https://blog.llamaindex.ai/rss/",
    # AI community blogs
    "https://simonwillison.net/atom/everything/",
    "https://www.interconnects.ai/feed",
    "https://www.latent.space/feed",
    "https://www.deeplearning.ai/the-batch/feed/",
    # Developer resources
    "https://github.com/trending/python.atom",
    "https://hnrss.org/newest?q=AI+OR+LLM+OR+GPT&points=50",
    "https://huggingface.co/papers.rss",
]

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
