import os

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# PubTator3 API Configuration
PUBTATOR_BASE_URL = "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocjson"

# Database Configuration
DB_PATH = "scidiscover.db"

# LLM Configuration
# the newest OpenAI model is "gpt-4o" which was released May 13, 2024
OPENAI_MODEL = "gpt-4o"
# the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

# Knowledge Graph Configuration
GRAPH_CACHE_DIR = ".graph_cache"
