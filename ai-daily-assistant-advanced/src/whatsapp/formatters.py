"""WhatsApp message formatters."""


def format_email_list(emails: list, title: str = "Emails") -> str:
    """Format email list for WhatsApp.

    Args:
        emails: List of email dictionaries
        title: Title for the list

    Returns:
        Formatted message string
    """
    if not emails:
        return "📭 No emails found."

    message = f"*{title}*\n\n"

    for i, email in enumerate(emails[:5], 1):  # Limit to 5
        sender = email.get('from', 'Unknown')
        subject = email.get('subject', 'No subject')
        date = email.get('date', '')

        message += f"{i}. 📧 *From:* {sender}\n"
        message += f"   *Subject:* {subject}\n"
        if date:
            message += f"   *Date:* {date}\n"
        message += "\n"

    if len(emails) > 5:
        message += f"\n_...and {len(emails) - 5} more_"

    return message


def format_email_detail(email: dict) -> str:
    """Format single email for WhatsApp.

    Args:
        email: Email dictionary

    Returns:
        Formatted message string
    """
    sender = email.get('from', 'Unknown')
    subject = email.get('subject', 'No subject')
    date = email.get('date', '')
    body = email.get('body', 'No content')

    # Truncate long bodies
    if len(body) > 500:
        body = body[:500] + "...\n\n_[Message truncated]_"

    message = f"📧 *Email Details*\n\n"
    message += f"*From:* {sender}\n"
    message += f"*Subject:* {subject}\n"
    if date:
        message += f"*Date:* {date}\n"
    message += f"\n*Message:*\n{body}"

    return message


def format_error(error_msg: str) -> str:
    """Format error message for WhatsApp.

    Args:
        error_msg: Error message

    Returns:
        Formatted error message
    """
    return f"❌ *Error*\n\n{error_msg}"


def format_thinking() -> str:
    """Format thinking message for WhatsApp.

    Returns:
        Thinking message
    """
    return "🤔 Let me check your emails..."


def format_welcome() -> str:
    """Format welcome message for WhatsApp.

    Returns:
        Welcome message
    """
    return """👋 *Welcome to AI Daily Assistant!*

I can help you with your Gmail emails. Try:

• "What are my unread emails?"
• "Show me emails from john@example.com"
• "List emails from the last week"
• "Summarize recent emails"

Just send me a message and I'll help! 📧"""
