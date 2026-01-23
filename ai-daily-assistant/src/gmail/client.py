"""Gmail API client for email operations."""

import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import structlog

logger = structlog.get_logger()


class GmailClient:
    """Gmail API client wrapper."""

    def __init__(self, credentials_file: str, token_file: str, scopes: List[str]):
        """Initialize Gmail client.

        Args:
            credentials_file: Path to OAuth credentials JSON file
            token_file: Path to token pickle file
            scopes: List of OAuth scopes
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes
        self.service = None
        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with Gmail API using OAuth 2.0."""
        creds = None

        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, "rb") as token:
                creds = pickle.load(token)

        # Refresh or create new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}. "
                        "Please run setup_gmail.py first."
                    )
                logger.info("Starting OAuth flow")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_file, "wb") as token:
                pickle.dump(creds, token)

        self.service = build("gmail", "v1", credentials=creds)
        logger.info("Gmail API client authenticated successfully")

    def list_messages(
        self,
        query: str = "",
        max_results: int = 10,
        label_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """List messages matching query.

        Args:
            query: Gmail search query (e.g., "from:john@example.com")
            max_results: Maximum number of messages to return
            label_ids: Filter by label IDs (e.g., ["UNREAD", "INBOX"])

        Returns:
            List of message objects with id and threadId
        """
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
        """Get message by ID.

        Args:
            message_id: Message ID
            format: Message format (full, metadata, minimal, raw)

        Returns:
            Message object with headers, body, etc.
        """
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
        """Get count of unread messages.

        Returns:
            Number of unread messages
        """
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
        """Search emails by sender.

        Args:
            sender_email: Sender email address
            max_results: Maximum number of messages to return
            days_back: Only search emails from last N days

        Returns:
            List of message objects
        """
        query = f"from:{sender_email}"
        if days_back:
            after_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y/%m/%d")
            query += f" after:{after_date}"

        return self.list_messages(query=query, max_results=max_results)

    def search_by_subject(
        self, subject: str, max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search emails by subject.

        Args:
            subject: Subject text to search for
            max_results: Maximum number of messages to return

        Returns:
            List of message objects
        """
        query = f"subject:{subject}"
        return self.list_messages(query=query, max_results=max_results)

    def search_by_date_range(
        self,
        after_date: Optional[str] = None,
        before_date: Optional[str] = None,
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search emails by date range.

        Args:
            after_date: Search emails after this date (YYYY/MM/DD)
            before_date: Search emails before this date (YYYY/MM/DD)
            max_results: Maximum number of messages to return

        Returns:
            List of message objects
        """
        query_parts = []
        if after_date:
            query_parts.append(f"after:{after_date}")
        if before_date:
            query_parts.append(f"before:{before_date}")

        query = " ".join(query_parts)
        return self.list_messages(query=query, max_results=max_results)

    def get_thread(self, thread_id: str) -> Dict[str, Any]:
        """Get email thread by ID.

        Args:
            thread_id: Thread ID

        Returns:
            Thread object with all messages
        """
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
