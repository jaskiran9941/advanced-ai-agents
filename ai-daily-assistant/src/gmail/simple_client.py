"""Simplified Gmail API client that reads credentials from .env"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import structlog

logger = structlog.get_logger()


class SimpleGmailClient:
    """Simplified Gmail API client that uses .env credentials."""

    def __init__(self):
        """Initialize Gmail client using credentials from environment variables."""
        self.service = None
        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with Gmail API using credentials from .env."""
        # Get credentials from environment variables
        client_id = os.getenv('GMAIL_CLIENT_ID')
        client_secret = os.getenv('GMAIL_CLIENT_SECRET')
        refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')
        token_uri = os.getenv('GMAIL_TOKEN_URI', 'https://oauth2.googleapis.com/token')

        if not all([client_id, client_secret, refresh_token]):
            raise ValueError(
                "Missing Gmail OAuth credentials in .env file. "
                "Please run: python3 scripts/setup_gmail_simple.py"
            )

        # Create credentials object
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri=token_uri,
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/gmail.readonly']
        )

        # Refresh the token
        try:
            creds.refresh(Request())
            logger.info("Gmail credentials refreshed successfully")
        except Exception as e:
            logger.error("Failed to refresh Gmail credentials", error=str(e))
            raise

        self.service = build("gmail", "v1", credentials=creds)
        logger.info("Gmail API client authenticated successfully")

    def list_messages(
        self,
        query: str = "",
        max_results: int = 10,
        label_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """List messages matching query."""
        try:
            kwargs: Dict[str, Any] = {
                "userId": "me",
                "maxResults": max_results,
            }
            if query:
                kwargs["q"] = query
            if label_ids:
                kwargs["labelIds"] = label_ids

            result = self.service.users().messages().list(**kwargs).execute()
            messages = result.get("messages", [])

            logger.info("Listed messages", count=len(messages), query=query)
            return messages

        except HttpError as error:
            logger.error("Failed to list messages", error=str(error))
            raise

    def get_message(self, message_id: str, format: str = "full") -> Dict[str, Any]:
        """Get message by ID."""
        try:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format=format)
                .execute()
            )
            logger.info("Retrieved message", message_id=message_id)
            return message

        except HttpError as error:
            logger.error("Failed to get message", message_id=message_id, error=str(error))
            raise

    def get_unread_count(self) -> int:
        """Get count of unread messages."""
        try:
            messages = self.list_messages(label_ids=["UNREAD"], max_results=500)
            count = len(messages)
            logger.info("Got unread count", count=count)
            return count

        except HttpError as error:
            logger.error("Failed to get unread count", error=str(error))
            raise

    def search_by_sender(
        self, sender_email: str, max_results: int = 10, days_back: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search emails by sender."""
        query = f"from:{sender_email}"
        if days_back:
            after_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y/%m/%d")
            query += f" after:{after_date}"

        return self.list_messages(query=query, max_results=max_results)

    def search_by_subject(
        self, subject: str, max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search emails by subject."""
        query = f"subject:{subject}"
        return self.list_messages(query=query, max_results=max_results)

    def search_by_date_range(
        self,
        after_date: Optional[str] = None,
        before_date: Optional[str] = None,
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search emails by date range."""
        query_parts = []
        if after_date:
            query_parts.append(f"after:{after_date}")
        if before_date:
            query_parts.append(f"before:{before_date}")

        query = " ".join(query_parts)
        return self.list_messages(query=query, max_results=max_results)

    def get_thread(self, thread_id: str) -> Dict[str, Any]:
        """Get email thread by ID."""
        try:
            thread = (
                self.service.users()
                .threads()
                .get(userId="me", id=thread_id, format="full")
                .execute()
            )
            logger.info("Retrieved thread", thread_id=thread_id)
            return thread

        except HttpError as error:
            logger.error("Failed to get thread", thread_id=thread_id, error=str(error))
            raise
