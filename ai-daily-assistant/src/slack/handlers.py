"""Slack message event handlers."""

from typing import Any, Dict
from slack_bolt import App, Say, Ack
from src.agent.runner import AgentRunner, SessionManager
from .formatters import SlackFormatter
import structlog

logger = structlog.get_logger()


class MessageHandler:
    """Handle Slack message events."""

    def __init__(self, agent_runner: AgentRunner, session_manager: SessionManager):
        """Initialize message handler.

        Args:
            agent_runner: AI agent runner
            session_manager: Session manager for conversation context
        """
        self.agent = agent_runner
        self.session_manager = session_manager
        self.formatter = SlackFormatter()

    def handle_app_mention(self, event: Dict[str, Any], say: Say) -> None:
        """Handle app mention events.

        Args:
            event: Slack event data
            say: Slack say function
        """
        try:
            # Extract message details
            text = event.get("text", "")
            user = event.get("user", "")
            channel = event.get("channel", "")
            thread_ts = event.get("thread_ts") or event.get("ts")

            # Remove bot mention from text
            # Slack mentions look like "<@U12345678> your message here"
            import re
            text = re.sub(r"<@[A-Z0-9]+>\s*", "", text).strip()

            if not text:
                say("Hi! Ask me anything about your emails.", thread_ts=thread_ts)
                return

            logger.info(
                "Received app mention",
                user=user,
                channel=channel,
                text=text,
                thread_ts=thread_ts
            )

            # Send thinking indicator
            say(**self.formatter.format_thinking(), thread_ts=thread_ts)

            # Create session ID from channel + thread
            session_id = f"{channel}:{thread_ts}"

            # Get chat history for this thread
            chat_history = self.session_manager.get_history(session_id)

            # Run agent
            response = self.agent.run(query=text, chat_history=chat_history)

            # Update session history
            self.session_manager.add_message(session_id, "human", text)
            self.session_manager.add_message(session_id, "ai", response)

            # Send response
            say(text=response, thread_ts=thread_ts)

            logger.info("Sent response", session_id=session_id, response_length=len(response))

        except Exception as e:
            logger.error("Error handling app mention", error=str(e))
            say(**self.formatter.format_error(str(e)), thread_ts=thread_ts)

    def handle_direct_message(self, event: Dict[str, Any], say: Say) -> None:
        """Handle direct message events.

        Args:
            event: Slack event data
            say: Slack say function
        """
        try:
            # Extract message details
            text = event.get("text", "")
            user = event.get("user", "")
            channel = event.get("channel", "")
            thread_ts = event.get("thread_ts") or event.get("ts")

            if not text:
                return

            # Ignore bot messages
            if event.get("bot_id"):
                return

            logger.info(
                "Received direct message",
                user=user,
                channel=channel,
                text=text
            )

            # Send thinking indicator
            say(**self.formatter.format_thinking(), thread_ts=thread_ts)

            # Create session ID from channel + thread
            session_id = f"{channel}:{thread_ts}"

            # Get chat history for this thread
            chat_history = self.session_manager.get_history(session_id)

            # Run agent
            response = self.agent.run(query=text, chat_history=chat_history)

            # Update session history
            self.session_manager.add_message(session_id, "human", text)
            self.session_manager.add_message(session_id, "ai", response)

            # Send response
            say(text=response, thread_ts=thread_ts)

            logger.info("Sent DM response", session_id=session_id, response_length=len(response))

        except Exception as e:
            logger.error("Error handling direct message", error=str(e))
            say(**self.formatter.format_error(str(e)), thread_ts=thread_ts)


def register_handlers(app: App, agent_runner: AgentRunner, session_manager: SessionManager) -> None:
    """Register all Slack event handlers.

    Args:
        app: Slack Bolt app
        agent_runner: AI agent runner
        session_manager: Session manager
    """
    handler = MessageHandler(agent_runner, session_manager)

    # Register app mention handler (@bot in channels)
    @app.event("app_mention")
    def on_app_mention(event: Dict[str, Any], say: Say) -> None:
        handler.handle_app_mention(event, say)

    # Register direct message handler
    @app.event("message")
    def on_message(event: Dict[str, Any], say: Say) -> None:
        # Only handle DMs (channel type is "im")
        channel_type = event.get("channel_type")
        if channel_type == "im":
            handler.handle_direct_message(event, say)

    logger.info("Registered Slack message handlers")
