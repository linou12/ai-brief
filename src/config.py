# config.py

RECIPIENT_EMAIL = "bousbinl@gmail.com"
SEND_HOUR = 7
SUMMARY_LANGUAGE = "english"

RSS_FEEDS = [
    # industry news — priorité
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://www.wired.com/feed/tag/artificial-intelligence/rss",
    "https://www.technologyreview.com/feed/",

    # company blogs
    "https://openai.com/blog/rss.xml",
    "https://www.anthropic.com/rss.xml",
    "https://mistral.ai/news/rss",
    "https://blog.langchain.dev/rss/",
    "https://blog.llamaindex.ai/feed",

    # practitioners & newsletters
    "https://simonwillison.net/atom/everything/",
    "https://www.interconnects.ai/feed",
    "https://latent.space/feed",
    "https://www.deeplearning.ai/the-batch/feed/",

    # github & HN
    "https://github-trending-rss.fly.dev/daily?language=python",
    "https://hnrss.org/newest?q=AI+LLM+agent&points=50",

    # papers — juste huggingface
    "https://huggingface.co/papers/feed",
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