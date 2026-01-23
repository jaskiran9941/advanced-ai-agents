"""Configuration management using Pydantic settings."""

from typing import List, Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SlackSettings(BaseSettings):
    """Slack bot configuration."""

    bot_token: str = Field(..., alias="SLACK_BOT_TOKEN")
    app_token: str = Field(..., alias="SLACK_APP_TOKEN")
    signing_secret: str = Field(..., alias="SLACK_SIGNING_SECRET")
    socket_mode: bool = Field(default=True)


class GmailSettings(BaseSettings):
    """Gmail API configuration."""

    credentials_file: str = Field(default="credentials.json", alias="GMAIL_CREDENTIALS_FILE")
    token_file: str = Field(default="token.json", alias="GMAIL_TOKEN_FILE")
    scopes: List[str] = Field(
        default=["https://www.googleapis.com/auth/gmail.readonly"]
    )
    poll_interval_seconds: int = Field(default=300)


class AnthropicProviderSettings(BaseSettings):
    """Anthropic AI provider configuration."""

    api_key: str = Field(..., alias="ANTHROPIC_API_KEY")
    model: str = Field(default="claude-opus-4-5-20251101")
    max_tokens: int = Field(default=4096)


class OpenAIProviderSettings(BaseSettings):
    """OpenAI AI provider configuration."""

    api_key: str = Field(..., alias="OPENAI_API_KEY")
    model: str = Field(default="gpt-4-turbo")
    max_tokens: int = Field(default=4096)


class AISettings(BaseSettings):
    """AI configuration."""

    default_provider: Literal["anthropic", "openai"] = Field(
        default="anthropic", alias="DEFAULT_AI_PROVIDER"
    )


class VectorDBSettings(BaseSettings):
    """Vector database configuration."""

    type: str = Field(default="chromadb")
    path: str = Field(default="./data/chroma", alias="CHROMA_DB_PATH")
    collection: str = Field(default="emails")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")


class ToolsSettings(BaseSettings):
    """Tools configuration."""

    allowlist: List[str] = Field(
        default=[
            "search_emails",
            "analyze_spending",
            "list_unread",
            "get_email_by_id",
            "get_sender_emails",
        ]
    )
    blocklist: List[str] = Field(default=[])


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Sub-configurations
    slack: SlackSettings = Field(default_factory=SlackSettings)
    gmail: GmailSettings = Field(default_factory=GmailSettings)
    ai: AISettings = Field(default_factory=AISettings)
    anthropic: AnthropicProviderSettings = Field(default_factory=AnthropicProviderSettings)
    openai: OpenAIProviderSettings = Field(default_factory=OpenAIProviderSettings)
    vector_db: VectorDBSettings = Field(default_factory=VectorDBSettings)
    tools: ToolsSettings = Field(default_factory=ToolsSettings)

    # General settings
    log_level: str = Field(default="INFO")

    def __init__(self, **kwargs):  # type: ignore
        super().__init__(**kwargs)
        # Initialize nested settings with environment variables
        self.slack = SlackSettings()
        self.gmail = GmailSettings()
        self.ai = AISettings()
        self.anthropic = AnthropicProviderSettings()
        self.openai = OpenAIProviderSettings()
        self.vector_db = VectorDBSettings()
        self.tools = ToolsSettings()


# Global settings instance
settings = Settings()
