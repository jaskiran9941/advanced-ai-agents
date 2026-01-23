"""Slack bot initialization and setup."""

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from src.config import settings
import structlog

logger = structlog.get_logger()


def create_slack_app() -> App:
    """Create and configure Slack Bolt app.

    Returns:
        Configured Slack app
    """
    app = App(
        token=settings.slack.bot_token,
        signing_secret=settings.slack.signing_secret,
    )

    logger.info("Created Slack app")
    return app


def start_slack_bot(app: App) -> None:
    """Start Slack bot in Socket Mode.

    Args:
        app: Slack Bolt app
    """
    if settings.slack.socket_mode:
        logger.info("Starting Slack bot in Socket Mode")
        handler = SocketModeHandler(app, settings.slack.app_token)
        handler.start()
    else:
        # For production with Events API
        logger.info("Starting Slack bot with Events API")
        app.start(port=3000)
