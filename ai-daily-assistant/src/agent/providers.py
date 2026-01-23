"""AI provider abstraction layer supporting multiple LLM providers."""

from typing import Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.schema import BaseLanguageModel
import structlog

logger = structlog.get_logger()


class AIProvider:
    """AI provider abstraction."""

    def __init__(
        self,
        provider: str,
        api_key: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ):
        """Initialize AI provider.

        Args:
            provider: Provider name ('anthropic' or 'openai')
            api_key: API key for the provider
            model: Model name
            max_tokens: Maximum tokens for response
            temperature: Temperature for generation
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.llm = self._create_llm()

    def _create_llm(self) -> BaseLanguageModel:
        """Create LangChain LLM instance.

        Returns:
            LangChain LLM instance

        Raises:
            ValueError: If provider is not supported
        """
        if self.provider == "anthropic":
            logger.info("Creating Anthropic LLM", model=self.model)
            return ChatAnthropic(
                model=self.model,
                anthropic_api_key=self.api_key,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        elif self.provider == "openai":
            logger.info("Creating OpenAI LLM", model=self.model)
            return ChatOpenAI(
                model=self.model,
                openai_api_key=self.api_key,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def get_llm(self) -> BaseLanguageModel:
        """Get the LLM instance.

        Returns:
            LangChain LLM instance
        """
        return self.llm


class AIProviderFactory:
    """Factory for creating AI providers with multi-provider support."""

    def __init__(self, default_provider: str):
        """Initialize provider factory.

        Args:
            default_provider: Default provider name
        """
        self.default_provider = default_provider
        self.providers: dict[str, AIProvider] = {}

    def register_provider(self, provider: AIProvider) -> None:
        """Register an AI provider.

        Args:
            provider: AI provider instance
        """
        self.providers[provider.provider] = provider
        logger.info("Registered AI provider", provider=provider.provider, model=provider.model)

    def get_provider(self, provider_name: Optional[str] = None) -> AIProvider:
        """Get AI provider by name.

        Args:
            provider_name: Provider name (uses default if None)

        Returns:
            AI provider instance

        Raises:
            ValueError: If provider not found
        """
        name = provider_name or self.default_provider
        if name not in self.providers:
            raise ValueError(f"Provider not registered: {name}")
        return self.providers[name]

    def get_llm(self, provider_name: Optional[str] = None) -> BaseLanguageModel:
        """Get LLM for a provider.

        Args:
            provider_name: Provider name (uses default if None)

        Returns:
            LangChain LLM instance
        """
        provider = self.get_provider(provider_name)
        return provider.get_llm()
