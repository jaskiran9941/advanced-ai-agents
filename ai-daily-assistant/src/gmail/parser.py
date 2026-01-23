"""Email parsing utilities."""

import base64
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import structlog

logger = structlog.get_logger()


class EmailParser:
    """Parse Gmail API message objects into structured data."""

    @staticmethod
    def parse_message(message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a Gmail message into structured format.

        Args:
            message: Gmail API message object

        Returns:
            Parsed message with from, to, subject, date, body, etc.
        """
        headers = message.get("payload", {}).get("headers", [])

        # Extract headers
        from_email = EmailParser._get_header(headers, "From")
        to_email = EmailParser._get_header(headers, "To")
        subject = EmailParser._get_header(headers, "Subject")
        date_str = EmailParser._get_header(headers, "Date")

        # Parse date
        date = EmailParser._parse_date(date_str)

        # Extract body
        body = EmailParser._extract_body(message.get("payload", {}))

        # Extract snippet
        snippet = message.get("snippet", "")

        parsed = {
            "id": message.get("id"),
            "thread_id": message.get("threadId"),
            "from": from_email,
            "to": to_email,
            "subject": subject,
            "date": date,
            "date_str": date_str,
            "body": body,
            "snippet": snippet,
            "labels": message.get("labelIds", []),
        }

        logger.debug("Parsed message", message_id=parsed["id"], subject=subject)
        return parsed

    @staticmethod
    def _get_header(headers: List[Dict[str, str]], name: str) -> str:
        """Extract header value by name.

        Args:
            headers: List of header objects
            name: Header name to find

        Returns:
            Header value or empty string
        """
        for header in headers:
            if header.get("name", "").lower() == name.lower():
                return header.get("value", "")
        return ""

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        """Parse email date string to datetime.

        Args:
            date_str: Date string from email header

        Returns:
            datetime object or None
        """
        if not date_str:
            return None

        try:
            # Try common email date formats
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception as e:
            logger.warning("Failed to parse date", date_str=date_str, error=str(e))
            return None

    @staticmethod
    def _extract_body(payload: Dict[str, Any]) -> str:
        """Extract email body from payload.

        Args:
            payload: Message payload object

        Returns:
            Email body text (HTML converted to plain text)
        """
        body = ""

        # Handle simple body
        if "body" in payload and payload["body"].get("data"):
            body = EmailParser._decode_body(payload["body"]["data"])

        # Handle multipart
        elif "parts" in payload:
            body = EmailParser._extract_multipart_body(payload["parts"])

        return body

    @staticmethod
    def _extract_multipart_body(parts: List[Dict[str, Any]]) -> str:
        """Extract body from multipart message.

        Args:
            parts: List of message parts

        Returns:
            Email body text
        """
        for part in parts:
            mime_type = part.get("mimeType", "")

            # Prefer text/plain
            if mime_type == "text/plain" and part.get("body", {}).get("data"):
                return EmailParser._decode_body(part["body"]["data"])

            # Recursively check nested parts
            if "parts" in part:
                nested_body = EmailParser._extract_multipart_body(part["parts"])
                if nested_body:
                    return nested_body

        # Fallback to HTML
        for part in parts:
            mime_type = part.get("mimeType", "")
            if mime_type == "text/html" and part.get("body", {}).get("data"):
                html = EmailParser._decode_body(part["body"]["data"])
                return EmailParser._html_to_text(html)

        return ""

    @staticmethod
    def _decode_body(data: str) -> str:
        """Decode base64url encoded body.

        Args:
            data: Base64url encoded string

        Returns:
            Decoded text
        """
        try:
            # Gmail uses base64url encoding
            decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            return decoded
        except Exception as e:
            logger.warning("Failed to decode body", error=str(e))
            return ""

    @staticmethod
    def _html_to_text(html: str) -> str:
        """Convert HTML to plain text.

        Args:
            html: HTML string

        Returns:
            Plain text
        """
        try:
            soup = BeautifulSoup(html, "lxml")
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)
            return text
        except Exception as e:
            logger.warning("Failed to convert HTML to text", error=str(e))
            return html

    @staticmethod
    def extract_sender_email(from_header: str) -> str:
        """Extract email address from From header.

        Args:
            from_header: From header value (e.g., "John Doe <john@example.com>")

        Returns:
            Email address
        """
        # Match email in angle brackets or standalone
        match = re.search(r"<(.+?)>", from_header)
        if match:
            return match.group(1)

        # Try to match standalone email
        match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", from_header)
        if match:
            return match.group(0)

        return from_header

    @staticmethod
    def extract_sender_name(from_header: str) -> str:
        """Extract sender name from From header.

        Args:
            from_header: From header value (e.g., "John Doe <john@example.com>")

        Returns:
            Sender name or empty string
        """
        # Match name before angle bracket
        match = re.search(r"^(.+?)\s*<", from_header)
        if match:
            name = match.group(1).strip('"')
            return name
        return ""

    @staticmethod
    def parse_thread(thread: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse email thread into list of messages.

        Args:
            thread: Gmail API thread object

        Returns:
            List of parsed messages
        """
        messages = thread.get("messages", [])
        parsed_messages = [EmailParser.parse_message(msg) for msg in messages]
        logger.info("Parsed thread", thread_id=thread.get("id"), message_count=len(parsed_messages))
        return parsed_messages
