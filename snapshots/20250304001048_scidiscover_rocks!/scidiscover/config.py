import os

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# PubTator3 API Configuration
PUBTATOR_BASE_URL = "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocjson"

# Database Configuration
DB_PATH = "scidiscover.db"

# LLM Configuration
# Using the latest specialized models for scientific analysis
# the newest OpenAI model is "o3-mini-2025-01-31" optimized for scientific research
OPENAI_MODEL = "o3-mini-2025-01-31"
# the newest Anthropic model is "claude-3-7-sonnet-20250219" with extended thinking capabilities
ANTHROPIC_MODEL = "claude-3-7-sonnet-20250219"

# Anthropic API configurations
ANTHROPIC_BETA_HEADER = "output-128k-2025-02-19"

# Extended thinking configurations - maximum
ANTHROPIC_MAX_TOKENS_HIGH = 80000
ANTHROPIC_THINKING_BUDGET_HIGH = 64000

# Extended thinking configurations - balanced
ANTHROPIC_MAX_TOKENS_LOW = 64000
ANTHROPIC_THINKING_BUDGET_LOW = 32000

# Standard mode without extended thinking
ANTHROPIC_MAX_TOKENS_NONE = 32000
ANTHROPIC_THINKING_BUDGET_NONE = 0

# Default to high configuration
ANTHROPIC_MAX_TOKENS = ANTHROPIC_MAX_TOKENS_HIGH
ANTHROPIC_THINKING_BUDGET = ANTHROPIC_THINKING_BUDGET_HIGH

# Scientific Analysis Configuration
PUBMED_BATCH_SIZE = 100
MAX_PAPERS_TO_ANALYZE = 1000
EVIDENCE_THRESHOLD = 0.85  # Minimum confidence score for including scientific claims

# Knowledge Graph Configuration
GRAPH_CACHE_DIR = ".graph_cache"