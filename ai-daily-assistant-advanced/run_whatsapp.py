#!/usr/bin/env python3
"""Run WhatsApp webhook server for AI Daily Assistant.

This script starts a Flask server that receives WhatsApp messages via Twilio,
processes them using the AI agent, and sends responses back.

Usage:
    python3 run_whatsapp.py

Requirements:
    - Twilio account with WhatsApp sandbox enabled
    - ngrok or similar for local development
    - All credentials in .env file

See WHATSAPP_INTEGRATION.md for setup instructions.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import settings
from src.gmail.simple_client import SimpleGmailClient
from src.agent import AIProvider, AIProviderFactory, AgentRunner, SessionManager
from src.agent.tools import ToolRegistry, register_email_tools
from src.whatsapp.webhook import create_whatsapp_app
from src.whatsapp.handlers import WhatsAppHandler
import structlog

# Setup logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(structlog.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def main():
    """Initialize and run WhatsApp webhook server."""

    logger.info("=" * 70)
    logger.info("AI Daily Assistant - WhatsApp Integration")
    logger.info("=" * 70)

    # Check for required settings
    try:
        twilio_sid = settings.twilio.account_sid
        twilio_token = settings.twilio.auth_token
        twilio_number = settings.twilio.whatsapp_number
    except Exception:
        logger.error(
            "Missing Twilio configuration in .env file. "
            "Please add TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_WHATSAPP_NUMBER"
        )
        sys.exit(1)

    logger.info("Initializing components...")

    # Initialize Gmail client
    try:
        gmail_client = SimpleGmailClient()
        logger.info("✓ Gmail client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Gmail client: {e}")
        logger.info("Make sure you've run: python3 scripts/setup_gmail_simple.py")
        sys.exit(1)

    # Initialize AI provider
    try:
        provider_factory = AIProviderFactory(default_provider=settings.ai.default_provider)

        if settings.ai.default_provider == "anthropic":
            provider = AIProvider(
                provider="anthropic",
                api_key=settings.anthropic.api_key,
                model=settings.anthropic.model,
                max_tokens=settings.anthropic.max_tokens,
            )
        else:
            provider = AIProvider(
                provider="openai",
                api_key=settings.openai.api_key,
                model=settings.openai.model,
                max_tokens=settings.openai.max_tokens,
            )

        provider_factory.register_provider(provider)
        llm = provider_factory.get_llm()
        logger.info(f"✓ AI provider initialized ({settings.ai.default_provider})")
    except Exception as e:
        logger.error(f"Failed to initialize AI provider: {e}")
        logger.info("Make sure you've added your API key to .env")
        sys.exit(1)

    # Initialize tools
    tool_registry = ToolRegistry(
        allowlist=settings.tools.allowlist,
        blocklist=settings.tools.blocklist,
    )
    register_email_tools(tool_registry, gmail_client)
    logger.info(f"✓ Registered {len(tool_registry.get_filtered_tools())} email tools")

    # Initialize agent
    agent_runner = AgentRunner(
        llm=llm,
        tool_registry=tool_registry,
        max_iterations=10,
        verbose=False,
    )
    logger.info("✓ Agent runner initialized")

    # Initialize session manager
    session_manager = SessionManager()
    logger.info("✓ Session manager initialized")

    # Create WhatsApp handler
    whatsapp_handler = WhatsAppHandler(agent_runner, session_manager)
    logger.info("✓ WhatsApp handler initialized")

    # Create Flask app
    app = create_whatsapp_app(whatsapp_handler)

    logger.info("=" * 70)
    logger.info("WhatsApp Webhook Server Ready!")
    logger.info("=" * 70)
    logger.info(f"Twilio WhatsApp Number: {twilio_number}")
    logger.info(f"Webhook endpoint: /webhook/whatsapp")
    logger.info(f"Health check: /health")
    logger.info("")
    logger.info("To test locally:")
    logger.info("1. Start ngrok: ngrok http 5000")
    logger.info("2. Copy the https URL (e.g., https://abc123.ngrok.io)")
    logger.info("3. Set webhook in Twilio: https://your-url.ngrok.io/webhook/whatsapp")
    logger.info("4. Send a WhatsApp message to your Twilio number")
    logger.info("=" * 70)

    # Run Flask app
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
