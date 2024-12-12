"""
Configuration settings for the AI Newsletter Pipeline.
"""
from pathlib import Path
import os
from dotenv import load_dotenv
from langchain_core.callbacks import BaseCallbackManager

# Load environment variables
load_dotenv()

# Base directories
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# API Keys and Credentials
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Content Sources
CONTENT_SOURCES = {
    "ai_articles": [
        "https://towardsdatascience.com/latest-ai-research",
        "https://arxiv.org/list/cs.AI/recent",
        "https://www.technologyreview.com/topic/artificial-intelligence/"
    ],
    "product_management_articles": [
        "https://www.productplan.com/blog/product-management/",
        "https://medium.com/mind-the-product",
        "https://www.theproductmanager.com/topics/best-product-management-blogs/"
    ],
    "general_technology": [
        "https://www.wired.com/category/science/artificial-intelligence/",
        "https://venturebeat.com/category/ai/",
        "https://techcrunch.com/tag/artificial-intelligence/"
    ]
}

# Embedding Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_DB_PATH = str(DATA_DIR / "vectorstore")

# LLM Configuration
GEMINI_MODEL = "gemini-pro"  # or "gemini-pro-vision" if needed
LLM_TEMPERATURE = 0.7
MAX_TOKENS = 1000

# Newsletter Configuration
NEWSLETTER_SETTINGS = {
    "max_articles": 5,
    "summary_length": 150,
    "relevance_threshold": 0.75,
    "categories": ["AI Research", "Product Updates", "Industry News"]
}

# Grammar Check Configuration
LANGUAGE_TOOL_LANGUAGE = "en-US" 