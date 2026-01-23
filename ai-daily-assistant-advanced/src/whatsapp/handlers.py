"""WhatsApp message handlers."""

from typing import Dict
import structlog
from .formatters import format_welcome, format_error

logger = structlog.get_logger()


class WhatsAppHandler:
    """Handle WhatsApp messages."""

    def __init__(self, agent_runner, session_manager):
        """Initialize handler.

        Args:
            agent_runner: Agent runner instance
            session_manager: Session manager for conversation history
        """
        self.agent = agent_runner
        self.sessions = session_manager

    def handle_message(self, from_number: str, message_body: str) -> str:
        """Handle incoming WhatsApp message.

        Args:
            from_number: Sender's WhatsApp number
            message_body: Message text

        Returns:
            Response message
        """
        logger.info("Received WhatsApp message",
                   from_number=from_number,
                   message=message_body)

        # Handle special commands
        if message_body.lower() in ['help', 'start', 'hi', 'hello']:
            return self._get_welcome_message()

        if message_body.lower() == 'clear':
            session_id = self._get_session_id(from_number)
            self.sessions.clear_session(session_id)
            return "✅ Chat history cleared!"

        try:
            # Get conversation history for this user
            session_id = self._get_session_id(from_number)
            chat_history = self.sessions.get_history(session_id)

            # Run agent
            response = self.agent.run(
                query=message_body,
                chat_history=chat_history if chat_history else None
            )

            # Update session
            self.sessions.add_message(session_id, "human", message_body)
            self.sessions.add_message(session_id, "ai", response)

            logger.info("Sent WhatsApp response",
                       from_number=from_number,
                       response_length=len(response))

            return response

        except Exception as e:
            logger.error("Error handling message",
                        from_number=from_number,
                        error=str(e))
            return format_error(f"Sorry, I encountered an error: {str(e)}")

    def _get_session_id(self, from_number: str) -> str:
        """Get session ID from phone number.

        Args:
            from_number: WhatsApp number (format: whatsapp:+1234567890)

        Returns:
            Session ID
        """
        # Remove 'whatsapp:' prefix and format
        return from_number.replace("whatsapp:", "").replace("+", "")

    def _get_welcome_message(self) -> str:
        """Get welcome message.

        Returns:
            Welcome message
        """
        return format_welcome()
