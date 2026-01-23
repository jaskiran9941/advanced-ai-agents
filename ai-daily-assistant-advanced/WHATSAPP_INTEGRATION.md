# WhatsApp Integration Guide

Extend the AI Daily Assistant to work with WhatsApp, allowing you to query your emails via WhatsApp messages.

## Architecture Overview

```
WhatsApp Message
    ↓
Twilio API (receives message)
    ↓
Webhook Server (Flask/FastAPI)
    ↓
WhatsApp Handler
    ↓
Agent Runner (existing) → Email Tools (existing)
    ↓
WhatsApp Formatter
    ↓
Twilio API (sends response)
    ↓
WhatsApp (user receives message)
```

## Why Twilio?

- Easy setup (no business verification needed)
- Free sandbox for testing
- Well-documented Python SDK
- Supports rich messages (buttons, media, etc.)

## Implementation Steps

### Step 1: Twilio Setup (5 minutes)

1. **Create Twilio Account**
   - Go to https://www.twilio.com/try-twilio
   - Sign up for free account
   - Get $15 free credit

2. **Enable WhatsApp Sandbox**
   - In Twilio Console, go to "Messaging" → "Try it out" → "Send a WhatsApp message"
   - Follow instructions to connect your WhatsApp to sandbox
   - You'll send a message like "join <code>" to Twilio's WhatsApp number
   - Save your sandbox number

3. **Get API Credentials**
   - Account SID (found on dashboard)
   - Auth Token (found on dashboard)
   - WhatsApp sandbox number (e.g., +14155238886)

### Step 2: Install Dependencies

```bash
pip install twilio flask flask-cors
```

Add to `requirements.txt`:
```
twilio>=8.0.0
flask>=3.0.0
flask-cors>=4.0.0
```

### Step 3: Add to .env

```bash
# WhatsApp/Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok.io  # We'll set this up
```

### Step 4: Project Structure

```
ai-daily-assistant/
├── src/
│   ├── whatsapp/              # NEW
│   │   ├── __init__.py
│   │   ├── webhook.py         # Flask webhook server
│   │   ├── handlers.py        # Message handling logic
│   │   └── formatters.py      # WhatsApp message formatting
│   ├── agent/                 # EXISTING (reuse)
│   ├── gmail/                 # EXISTING (reuse)
│   └── config/                # UPDATE (add Twilio settings)
└── run_whatsapp.py           # NEW (entry point)
```

## Implementation

### 1. Update Configuration

**File: `src/config/settings.py`**

Add after existing settings:

```python
class TwilioSettings(BaseSettings):
    """Twilio/WhatsApp configuration."""

    account_sid: str = Field(..., alias="TWILIO_ACCOUNT_SID")
    auth_token: str = Field(..., alias="TWILIO_AUTH_TOKEN")
    whatsapp_number: str = Field(..., alias="TWILIO_WHATSAPP_NUMBER")
    webhook_base_url: str = Field(default="", alias="WEBHOOK_BASE_URL")

# In Settings class, add:
twilio: TwilioSettings = Field(default_factory=TwilioSettings)

# In __init__, add:
self.twilio = TwilioSettings()
```

### 2. Create WhatsApp Formatters

**File: `src/whatsapp/formatters.py`**

```python
"""WhatsApp message formatters."""

def format_email_list(emails: list, title: str = "Emails") -> str:
    """Format email list for WhatsApp."""
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
    """Format single email for WhatsApp."""
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
    """Format error message for WhatsApp."""
    return f"❌ *Error*\n\n{error_msg}"


def format_thinking() -> str:
    """Format thinking message for WhatsApp."""
    return "🤔 Let me check your emails..."
```

### 3. Create WhatsApp Handlers

**File: `src/whatsapp/handlers.py`**

```python
"""WhatsApp message handlers."""

from typing import Dict
from twilio.twiml.messaging_response import MessagingResponse
from ..agent import AgentRunner, SessionManager
import structlog

logger = structlog.get_logger()


class WhatsAppHandler:
    """Handle WhatsApp messages."""

    def __init__(self, agent_runner: AgentRunner, session_manager: SessionManager):
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
            return f"❌ Sorry, I encountered an error: {str(e)}"

    def _get_session_id(self, from_number: str) -> str:
        """Get session ID from phone number."""
        # Remove 'whatsapp:' prefix and format
        return from_number.replace("whatsapp:", "").replace("+", "")
```

### 4. Create Webhook Server

**File: `src/whatsapp/webhook.py`**

```python
"""Flask webhook server for WhatsApp messages."""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from .handlers import WhatsAppHandler
import structlog
import os

logger = structlog.get_logger()


def create_whatsapp_app(handler: WhatsAppHandler) -> Flask:
    """Create Flask app for WhatsApp webhook.

    Args:
        handler: WhatsApp message handler

    Returns:
        Flask app instance
    """
    app = Flask(__name__)

    # Get Twilio credentials for validation
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    validator = RequestValidator(auth_token)

    @app.route("/webhook/whatsapp", methods=["POST"])
    def whatsapp_webhook():
        """Handle incoming WhatsApp messages."""
        # Get message details
        from_number = request.form.get("From")
        message_body = request.form.get("Body", "").strip()

        logger.info("Webhook received", from_number=from_number)

        # Validate request is from Twilio (optional but recommended)
        # if not validate_twilio_request(request):
        #     return "Unauthorized", 401

        # Handle message
        response_text = handler.handle_message(from_number, message_body)

        # Create Twilio response
        resp = MessagingResponse()
        resp.message(response_text)

        return str(resp)

    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return {"status": "healthy"}, 200

    def validate_twilio_request(req) -> bool:
        """Validate request is from Twilio."""
        url = request.url
        signature = req.headers.get("X-Twilio-Signature", "")
        params = req.form.to_dict()
        return validator.validate(url, params, signature)

    return app
```

### 5. Create Entry Point

**File: `run_whatsapp.py`**

```python
#!/usr/bin/env python3
"""Run WhatsApp webhook server."""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import settings
from src.gmail.simple_client import SimpleGmailClient
from src.agent import AIProvider, AIProviderFactory, AgentRunner, SessionManager
from src.agent.tools import ToolRegistry, register_email_tools
from src.whatsapp.webhook import create_whatsapp_app
from src.whatsapp.handlers import WhatsAppHandler
import structlog

# Setup logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(structlog.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def main():
    """Initialize and run WhatsApp webhook server."""

    logger.info("Initializing AI Daily Assistant for WhatsApp")

    # Initialize Gmail client
    gmail_client = SimpleGmailClient()

    # Initialize AI provider
    provider_factory = AIProviderFactory(default_provider=settings.ai.default_provider)

    if settings.ai.default_provider == "anthropic":
        provider = AIProvider(
            provider="anthropic",
            api_key=settings.anthropic.api_key,
            model=settings.anthropic.model,
            max_tokens=settings.anthropic.max_tokens,
        )
    else:
        provider = AIProvider(
            provider="openai",
            api_key=settings.openai.api_key,
            model=settings.openai.model,
            max_tokens=settings.openai.max_tokens,
        )

    provider_factory.register_provider(provider)
    llm = provider_factory.get_llm()

    # Initialize tools
    tool_registry = ToolRegistry(
        allowlist=settings.tools.allowlist,
        blocklist=settings.tools.blocklist,
    )
    register_email_tools(tool_registry, gmail_client)

    # Initialize agent
    agent_runner = AgentRunner(
        llm=llm,
        tool_registry=tool_registry,
        max_iterations=10,
        verbose=False,
    )

    # Initialize session manager
    session_manager = SessionManager()

    # Create WhatsApp handler
    whatsapp_handler = WhatsAppHandler(agent_runner, session_manager)

    # Create Flask app
    app = create_whatsapp_app(whatsapp_handler)

    logger.info(
        "WhatsApp webhook server ready",
        twilio_number=settings.twilio.whatsapp_number,
        webhook_url=f"{settings.twilio.webhook_base_url}/webhook/whatsapp"
    )

    # Run Flask app
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
```

## Testing Locally with ngrok

Since Twilio needs a public URL, use ngrok to expose your local server:

### 1. Install ngrok

```bash
# macOS
brew install ngrok

# Or download from https://ngrok.com/download
```

### 2. Start the webhook server

```bash
python3 run_whatsapp.py
```

### 3. In another terminal, start ngrok

```bash
ngrok http 5000
```

You'll get a URL like: `https://abc123.ngrok.io`

### 4. Configure Twilio Webhook

1. Go to Twilio Console → Messaging → Try it out → Send a WhatsApp message
2. In "Sandbox Settings", set:
   - **When a message comes in:** `https://your-ngrok-url.ngrok.io/webhook/whatsapp`
   - Method: POST
3. Save

### 5. Test it!

Send a WhatsApp message to your Twilio sandbox number:
```
What are my unread emails?
```

The bot should respond with your unread emails!

## Example Conversations

```
You: What are my unread emails?
Bot: 📬 Unread Emails

1. 📧 From: john@example.com
   Subject: Meeting tomorrow
   Date: Jan 23, 2026

2. 📧 From: jane@company.com
   Subject: Project update
   Date: Jan 22, 2026

...and 3 more

---

You: Show me emails from john@example.com
Bot: 📧 Email Details

From: john@example.com
Subject: Meeting tomorrow
Date: Jan 23, 2026

Message:
Hi, can we meet tomorrow at 2pm to discuss...

---

You: Summarize this email
Bot: This email is asking to schedule a meeting tomorrow...
```

## Production Deployment

For production (real WhatsApp number, not sandbox):

1. **Apply for WhatsApp Business API**
   - Requires business verification
   - Can take 1-2 weeks

2. **Deploy webhook server**
   - Use Heroku, AWS, Google Cloud, etc.
   - Need persistent public URL
   - Add proper authentication

3. **Add features**
   - Message templates (for WhatsApp Business)
   - Rich media support (images, PDFs)
   - Interactive buttons
   - Read receipts

## Next Steps

1. ✅ Set up Twilio account and WhatsApp sandbox
2. ✅ Add Twilio credentials to `.env`
3. ✅ Create the WhatsApp integration files
4. ✅ Test locally with ngrok
5. 🚀 Deploy to production

## Architecture Benefits

- ✅ **Reuses existing code**: Agent, tools, and email client stay the same
- ✅ **Multi-channel**: Slack, Streamlit, and WhatsApp all use same backend
- ✅ **Session management**: Maintains conversation context per user
- ✅ **Scalable**: Can add more channels (Telegram, Discord, etc.)

## Cost Considerations

- **Twilio Free Tier**: $15 credit, then ~$0.005 per message
- **Production WhatsApp**: Varies by country, typically $0.01-0.05 per conversation
- **Alternative**: Use WhatsApp Business API directly (free but more complex)

Ready to implement? Let me know if you want me to create these files!
