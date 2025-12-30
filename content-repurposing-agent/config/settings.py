"""
Configuration management for the Content Repurposing Agent system.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional

# Load environment variables
load_dotenv()

class LLMConfig(BaseModel):
    """LLM provider configuration"""
    anthropic_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    google_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY"))
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))

class ImageConfig(BaseModel):
    """Image generation configuration"""
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    replicate_api_token: Optional[str] = Field(default_factory=lambda: os.getenv("REPLICATE_API_TOKEN"))
    default_provider: str = "openai"  # or "replicate"

class SEOConfig(BaseModel):
    """SEO research configuration"""
    serpapi_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("SERPAPI_API_KEY"))

class TwitterConfig(BaseModel):
    """Twitter API configuration"""
    api_key: Optional[str] = Field(default_factory=lambda: os.getenv("TWITTER_API_KEY"))
    api_secret: Optional[str] = Field(default_factory=lambda: os.getenv("TWITTER_API_SECRET"))
    access_token: Optional[str] = Field(default_factory=lambda: os.getenv("TWITTER_ACCESS_TOKEN"))
    access_secret: Optional[str] = Field(default_factory=lambda: os.getenv("TWITTER_ACCESS_SECRET"))
    bearer_token: Optional[str] = Field(default_factory=lambda: os.getenv("TWITTER_BEARER_TOKEN"))

class LinkedInConfig(BaseModel):
    """LinkedIn API configuration"""
    access_token: Optional[str] = Field(default_factory=lambda: os.getenv("LINKEDIN_ACCESS_TOKEN"))

class InstagramConfig(BaseModel):
    """Instagram API configuration"""
    username: Optional[str] = Field(default_factory=lambda: os.getenv("INSTAGRAM_USERNAME"))
    password: Optional[str] = Field(default_factory=lambda: os.getenv("INSTAGRAM_PASSWORD"))

class SubstackConfig(BaseModel):
    """Substack API configuration"""
    api_key: Optional[str] = Field(default_factory=lambda: os.getenv("SUBSTACK_API_KEY"))
    publication_id: Optional[str] = Field(default_factory=lambda: os.getenv("SUBSTACK_PUBLICATION_ID"))

class DatabaseConfig(BaseModel):
    """Database configuration"""
    url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./content_repurposing.db"))

class Settings(BaseModel):
    """Main application settings"""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    image: ImageConfig = Field(default_factory=ImageConfig)
    seo: SEOConfig = Field(default_factory=SEOConfig)
    twitter: TwitterConfig = Field(default_factory=TwitterConfig)
    linkedin: LinkedInConfig = Field(default_factory=LinkedInConfig)
    instagram: InstagramConfig = Field(default_factory=InstagramConfig)
    substack: SubstackConfig = Field(default_factory=SubstackConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    # Project paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data")

    class Config:
        arbitrary_types_allowed = True

# Global settings instance
settings = Settings()

# Create data directory if it doesn't exist
settings.data_dir.mkdir(exist_ok=True)
