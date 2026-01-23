"""Tests for email tools."""

import pytest
from unittest.mock import Mock, MagicMock
from src.agent.tools.email_tools import EmailTools
from src.gmail.client import GmailClient


@pytest.fixture
def mock_gmail_client():
    """Create a mock Gmail client."""
    return Mock(spec=GmailClient)


@pytest.fixture
def email_tools(mock_gmail_client):
    """Create EmailTools instance with mock client."""
    return EmailTools(mock_gmail_client)


def test_list_unread_no_emails(email_tools, mock_gmail_client):
    """Test list_unread with no unread emails."""
    mock_gmail_client.list_messages.return_value = []

    result = email_tools.list_unread()

    assert "no unread emails" in result.lower()
    mock_gmail_client.list_messages.assert_called_once()


def test_list_unread_with_emails(email_tools, mock_gmail_client):
    """Test list_unread with unread emails."""
    # Mock message list
    mock_gmail_client.list_messages.return_value = [
        {"id": "msg1", "threadId": "thread1"},
        {"id": "msg2", "threadId": "thread2"},
    ]

    # Mock full message details
    mock_gmail_client.get_message.return_value = {
        "id": "msg1",
        "threadId": "thread1",
        "payload": {
            "headers": [
                {"name": "From", "value": "John Doe <john@example.com>"},
                {"name": "Subject", "value": "Test Email"},
                {"name": "Date", "value": "Mon, 20 Jan 2025 10:00:00 +0000"},
            ]
        },
        "snippet": "This is a test email",
    }

    result = email_tools.list_unread()

    assert "2 unread email" in result
    assert "john@example.com" in result.lower() or "john doe" in result.lower()


def test_search_emails_no_results(email_tools, mock_gmail_client):
    """Test search_emails with no results."""
    mock_gmail_client.list_messages.return_value = []

    result = email_tools.search_emails("from:nobody@example.com")

    assert "no emails found" in result.lower()


def test_get_sender_emails(email_tools, mock_gmail_client):
    """Test get_sender_emails."""
    mock_gmail_client.list_messages.return_value = [{"id": "msg1", "threadId": "thread1"}]

    mock_gmail_client.get_message.return_value = {
        "id": "msg1",
        "threadId": "thread1",
        "payload": {
            "headers": [
                {"name": "From", "value": "john@example.com"},
                {"name": "Subject", "value": "Hello"},
                {"name": "Date", "value": "Mon, 20 Jan 2025 10:00:00 +0000"},
            ]
        },
        "snippet": "Test message",
    }

    result = email_tools.get_sender_emails("john@example.com")

    assert "john@example.com" in result
    assert "found" in result.lower()
