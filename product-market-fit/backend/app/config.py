"""
Configuration settings
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

    # LLM Models
    CLAUDE_MODEL = "claude-sonnet-4-20250514"
    GPT4_MODEL = "gpt-4-turbo-preview"

    # Workflow settings
    MAX_RESEARCH_ITERATIONS = 3
    MIN_ICP_CONFIDENCE = 0.7
    DEFAULT_NUM_PERSONAS = 3

    # API settings
    BACKEND_HOST = "0.0.0.0"
    BACKEND_PORT = 8000
    CORS_ORIGINS = ["http://localhost:8501", "http://localhost:3000"]


settings = Settings()
