"""Core email analysis tools."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from src.gmail.client import GmailClient
from src.gmail.parser import EmailParser
from .registry import Tool, ToolRegistry
import structlog

logger = structlog.get_logger()


class EmailTools:
    """Email analysis tools for AI agent."""

    def __init__(self, gmail_client: GmailClient):
        """Initialize email tools.

        Args:
            gmail_client: Gmail API client
        """
        self.gmail = gmail_client
        self.parser = EmailParser()

    def list_unread(self) -> str:
        """Get count and list of unread emails.

        Returns:
            Summary of unread emails
        """
        try:
            logger.info("Listing unread emails")
            messages = self.gmail.list_messages(label_ids=["UNREAD"], max_results=20)

            if not messages:
                return "You have no unread emails."

            count = len(messages)
            summaries = []

            # Get details for first 10 unread emails
            for msg in messages[:10]:
                full_msg = self.gmail.get_message(msg["id"])
                parsed = self.parser.parse_message(full_msg)

                sender = self.parser.extract_sender_name(parsed["from"]) or self.parser.extract_sender_email(parsed["from"])
                subject = parsed["subject"] or "(no subject)"
                date = parsed["date"].strftime("%b %d, %I:%M %p") if parsed["date"] else "Unknown date"

                summaries.append(f"- From: {sender}\n  Subject: {subject}\n  Date: {date}")

            result = f"You have {count} unread email(s).\n\n"
            result += "Recent unread emails:\n" + "\n\n".join(summaries)

            if count > 10:
                result += f"\n\n... and {count - 10} more unread emails."

            return result

        except Exception as e:
            logger.error("Failed to list unread emails", error=str(e))
            return f"Error listing unread emails: {str(e)}"

    def search_emails(
        self,
        query: str,
        max_results: int = 10,
        days_back: Optional[int] = None
    ) -> str:
        """Search emails by query string.

        Args:
            query: Gmail search query (supports from:, subject:, etc.)
            max_results: Maximum number of results
            days_back: Only search last N days

        Returns:
            Summary of matching emails
        """
        try:
            logger.info("Searching emails", query=query, max_results=max_results)

            # Add date filter if specified
            search_query = query
            if days_back:
                after_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y/%m/%d")
                search_query += f" after:{after_date}"

            messages = self.gmail.list_messages(query=search_query, max_results=max_results)

            if not messages:
                return f"No emails found matching: {query}"

            summaries = []
            for msg in messages:
                full_msg = self.gmail.get_message(msg["id"])
                parsed = self.parser.parse_message(full_msg)

                sender = self.parser.extract_sender_name(parsed["from"]) or self.parser.extract_sender_email(parsed["from"])
                subject = parsed["subject"] or "(no subject)"
                date = parsed["date"].strftime("%b %d, %I:%M %p") if parsed["date"] else "Unknown date"
                snippet = parsed["snippet"][:150] + "..." if len(parsed["snippet"]) > 150 else parsed["snippet"]

                summaries.append(
                    f"From: {sender}\n"
                    f"Subject: {subject}\n"
                    f"Date: {date}\n"
                    f"Preview: {snippet}"
                )

            result = f"Found {len(messages)} email(s) matching '{query}':\n\n"
            result += "\n\n---\n\n".join(summaries)

            return result

        except Exception as e:
            logger.error("Failed to search emails", error=str(e))
            return f"Error searching emails: {str(e)}"

    def get_email_by_id(self, email_id: str) -> str:
        """Get full email details by ID.

        Args:
            email_id: Gmail message ID

        Returns:
            Full email details
        """
        try:
            logger.info("Getting email by ID", email_id=email_id)
            message = self.gmail.get_message(email_id)
            parsed = self.parser.parse_message(message)

            sender = parsed["from"]
            subject = parsed["subject"] or "(no subject)"
            date = parsed["date"].strftime("%b %d, %Y at %I:%M %p") if parsed["date"] else "Unknown date"
            to = parsed["to"]
            body = parsed["body"][:2000] + "..." if len(parsed["body"]) > 2000 else parsed["body"]

            result = (
                f"From: {sender}\n"
                f"To: {to}\n"
                f"Subject: {subject}\n"
                f"Date: {date}\n"
                f"\n---\n\n{body}"
            )

            return result

        except Exception as e:
            logger.error("Failed to get email", email_id=email_id, error=str(e))
            return f"Error retrieving email: {str(e)}"

    def get_sender_emails(
        self,
        sender_email: str,
        max_results: int = 10,
        days_back: Optional[int] = 30
    ) -> str:
        """Get emails from a specific sender.

        Args:
            sender_email: Sender's email address or name
            max_results: Maximum number of results
            days_back: Only search last N days

        Returns:
            Summary of emails from sender
        """
        try:
            logger.info("Getting sender emails", sender=sender_email)

            query = f"from:{sender_email}"
            if days_back:
                after_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y/%m/%d")
                query += f" after:{after_date}"

            messages = self.gmail.list_messages(query=query, max_results=max_results)

            if not messages:
                return f"No emails found from: {sender_email}"

            summaries = []
            for msg in messages:
                full_msg = self.gmail.get_message(msg["id"])
                parsed = self.parser.parse_message(full_msg)

                subject = parsed["subject"] or "(no subject)"
                date = parsed["date"].strftime("%b %d, %I:%M %p") if parsed["date"] else "Unknown date"
                snippet = parsed["snippet"][:200] + "..." if len(parsed["snippet"]) > 200 else parsed["snippet"]

                summaries.append(
                    f"Subject: {subject}\n"
                    f"Date: {date}\n"
                    f"Preview: {snippet}"
                )

            result = f"Found {len(messages)} email(s) from {sender_email}"
            if days_back:
                result += f" in the last {days_back} days"
            result += ":\n\n" + "\n\n---\n\n".join(summaries)

            return result

        except Exception as e:
            logger.error("Failed to get sender emails", error=str(e))
            return f"Error retrieving emails: {str(e)}"

    def summarize_thread(self, thread_id: str) -> str:
        """Summarize an email conversation thread.

        Args:
            thread_id: Gmail thread ID

        Returns:
            Summary of the thread
        """
        try:
            logger.info("Summarizing thread", thread_id=thread_id)
            thread = self.gmail.get_thread(thread_id)
            messages = self.parser.parse_thread(thread)

            if not messages:
                return "Thread is empty."

            # Get thread metadata
            first_msg = messages[0]
            subject = first_msg["subject"] or "(no subject)"
            participant_emails = set()

            for msg in messages:
                participant_emails.add(self.parser.extract_sender_email(msg["from"]))

            participants = ", ".join(participant_emails)

            # Summarize messages
            summaries = []
            for idx, msg in enumerate(messages, 1):
                sender = self.parser.extract_sender_name(msg["from"]) or self.parser.extract_sender_email(msg["from"])
                date = msg["date"].strftime("%b %d, %I:%M %p") if msg["date"] else "Unknown date"
                snippet = msg["snippet"][:150] + "..." if len(msg["snippet"]) > 150 else msg["snippet"]

                summaries.append(f"{idx}. {sender} ({date}):\n   {snippet}")

            result = (
                f"Thread: {subject}\n"
                f"Participants: {participants}\n"
                f"Messages: {len(messages)}\n\n"
                + "\n\n".join(summaries)
            )

            return result

        except Exception as e:
            logger.error("Failed to summarize thread", error=str(e))
            return f"Error summarizing thread: {str(e)}"


def register_email_tools(registry: ToolRegistry, gmail_client: GmailClient) -> None:
    """Register all email tools with the registry.

    Args:
        registry: Tool registry
        gmail_client: Gmail API client
    """
    tools = EmailTools(gmail_client)

    # Register list_unread tool
    registry.register(Tool(
        name="list_unread",
        description="Get count and list of unread emails. Use this when user asks about unread emails.",
        parameters={},
        function=tools.list_unread
    ))

    # Register search_emails tool
    registry.register(Tool(
        name="search_emails",
        description=(
            "Search emails by query. Supports Gmail search operators like 'from:', 'subject:', 'has:attachment', etc. "
            "Use this to find emails matching specific criteria."
        ),
        parameters={
            "query": {"type": "string", "description": "Gmail search query"},
            "max_results": {"type": "integer", "description": "Maximum results (default: 10)", "default": 10},
            "days_back": {"type": "integer", "description": "Only search last N days (optional)"}
        },
        function=tools.search_emails
    ))

    # Register get_email_by_id tool
    registry.register(Tool(
        name="get_email_by_id",
        description="Get full email content by message ID. Use when you need complete email details.",
        parameters={
            "email_id": {"type": "string", "description": "Gmail message ID"}
        },
        function=tools.get_email_by_id
    ))

    # Register get_sender_emails tool
    registry.register(Tool(
        name="get_sender_emails",
        description=(
            "Get all emails from a specific sender. Use this when user asks 'what is X saying?' or "
            "'show me emails from X'."
        ),
        parameters={
            "sender_email": {"type": "string", "description": "Sender email address or name"},
            "max_results": {"type": "integer", "description": "Maximum results (default: 10)", "default": 10},
            "days_back": {"type": "integer", "description": "Only search last N days (default: 30)", "default": 30}
        },
        function=tools.get_sender_emails
    ))

    # Register summarize_thread tool
    registry.register(Tool(
        name="summarize_thread",
        description="Summarize an email conversation thread. Use when user wants to understand an email thread.",
        parameters={
            "thread_id": {"type": "string", "description": "Gmail thread ID"}
        },
        function=tools.summarize_thread
    ))

    logger.info("Registered email tools", count=5)
