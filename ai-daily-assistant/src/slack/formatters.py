"""Slack message formatting utilities."""

from typing import Dict, Any


class SlackFormatter:
    """Format messages for Slack."""

    @staticmethod
    def format_response(text: str) -> Dict[str, Any]:
        """Format text response for Slack.

        Args:
            text: Response text

        Returns:
            Slack message block
        """
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text
                    }
                }
            ]
        }

    @staticmethod
    def format_error(error: str) -> Dict[str, Any]:
        """Format error message for Slack.

        Args:
            error: Error message

        Returns:
            Slack error message block
        """
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":warning: *Error:* {error}"
                    }
                }
            ]
        }

    @staticmethod
    def format_thinking() -> Dict[str, Any]:
        """Format 'thinking' indicator message.

        Returns:
            Slack message block
        """
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":thinking_face: Analyzing your emails..."
                    }
                }
            ]
        }

    @staticmethod
    def escape_slack_text(text: str) -> str:
        """Escape special characters for Slack markdown.

        Args:
            text: Text to escape

        Returns:
            Escaped text
        """
        # Escape special Slack markdown characters
        replacements = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
        }
        for char, escaped in replacements.items():
            text = text.replace(char, escaped)
        return text
