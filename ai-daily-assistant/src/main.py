"""Main entry point for the Email Analysis Slack Bot."""

import structlog
from src.config import settings
from src.gmail import GmailClient
from src.agent import AIProvider, AIProviderFactory, AgentRunner, SessionManager
from src.agent.tools import ToolRegistry, register_email_tools
from src.slack import create_slack_app, start_slack_bot, register_handlers


def setup_logging() -> None:
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog.processors, settings.log_level.upper(), structlog.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def initialize_gmail_client() -> GmailClient:
    """Initialize Gmail API client.

    Returns:
        Configured Gmail client
    """
    logger = structlog.get_logger()
    logger.info("Initializing Gmail client")

    client = GmailClient(
        credentials_file=settings.gmail.credentials_file,
        token_file=settings.gmail.token_file,
        scopes=settings.gmail.scopes,
    )

    return client


def initialize_ai_providers() -> AIProviderFactory:
    """Initialize AI provider factory with configured providers.

    Returns:
        AI provider factory
    """
    logger = structlog.get_logger()
    logger.info("Initializing AI providers")

    factory = AIProviderFactory(default_provider=settings.ai.default_provider)

    # Register Anthropic provider
    try:
        anthropic_provider = AIProvider(
            provider="anthropic",
            api_key=settings.anthropic.api_key,
            model=settings.anthropic.model,
            max_tokens=settings.anthropic.max_tokens,
        )
        factory.register_provider(anthropic_provider)
    except Exception as e:
        logger.warning("Failed to initialize Anthropic provider", error=str(e))

    # Register OpenAI provider
    try:
        openai_provider = AIProvider(
            provider="openai",
            api_key=settings.openai.api_key,
            model=settings.openai.model,
            max_tokens=settings.openai.max_tokens,
        )
        factory.register_provider(openai_provider)
    except Exception as e:
        logger.warning("Failed to initialize OpenAI provider", error=str(e))

    return factory


def initialize_tool_registry(gmail_client: GmailClient) -> ToolRegistry:
    """Initialize tool registry with email tools.

    Args:
        gmail_client: Gmail API client

    Returns:
        Configured tool registry
    """
    logger = structlog.get_logger()
    logger.info("Initializing tool registry")

    registry = ToolRegistry(
        allowlist=settings.tools.allowlist,
        blocklist=settings.tools.blocklist,
    )

    # Register email tools
    register_email_tools(registry, gmail_client)

    return registry


def main() -> None:
    """Main entry point."""
    # Setup logging
    setup_logging()
    logger = structlog.get_logger()

    logger.info("Starting Email Analysis Slack Bot")

    try:
        # Initialize Gmail client
        gmail_client = initialize_gmail_client()

        # Initialize AI providers
        provider_factory = initialize_ai_providers()
        llm = provider_factory.get_llm()

        # Initialize tool registry
        tool_registry = initialize_tool_registry(gmail_client)

        # Initialize agent runner
        agent_runner = AgentRunner(
            llm=llm,
            tool_registry=tool_registry,
            max_iterations=10,
            verbose=True,
        )

        # Initialize session manager
        session_manager = SessionManager()

        # Create Slack app
        slack_app = create_slack_app()

        # Register message handlers
        register_handlers(slack_app, agent_runner, session_manager)

        # Start bot
        logger.info("Email Analysis Slack Bot is ready!")
        logger.info(
            "Configuration",
            gmail_scopes=settings.gmail.scopes,
            ai_provider=settings.ai.default_provider,
            tool_count=len(tool_registry.get_filtered_tools()),
        )

        start_slack_bot(slack_app)

    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error("Fatal error", error=str(e))
        raise


if __name__ == "__main__":
    main()
