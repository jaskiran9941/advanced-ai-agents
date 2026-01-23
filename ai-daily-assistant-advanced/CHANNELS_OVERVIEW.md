# Multi-Channel Architecture Overview

The AI Daily Assistant supports multiple communication channels, all using the same backend.

## Supported Channels

### 1. Streamlit Web UI ✅
**Status:** Fully implemented
**Best for:** Testing, personal use, demos
**Setup time:** 5 minutes

**Files:**
- `streamlit_app_simple.py` - Main UI
- `SETUP_SIMPLE.md` - Setup guide

**Run:**
```bash
streamlit run streamlit_app_simple.py
```

**Pros:**
- Easiest to set up
- Great for development
- Visual interface
- No external accounts needed

**Cons:**
- Not mobile-friendly
- Single user only
- No notifications

---

### 2. Slack Bot ✅
**Status:** Fully implemented
**Best for:** Team collaboration, work environments
**Setup time:** 15 minutes

**Files:**
- `src/slack/` - Slack integration
- `src/main.py` - Entry point
- `README.md` - Setup guide

**Run:**
```bash
python src/main.py
```

**Pros:**
- Team collaboration
- Mobile app available
- Real-time notifications
- Thread-based conversations

**Cons:**
- Requires Slack workspace
- More complex setup
- Socket Mode for development

---

### 3. WhatsApp Bot ✅
**Status:** Newly implemented
**Best for:** Personal use, mobile-first
**Setup time:** 10 minutes

**Files:**
- `src/whatsapp/` - WhatsApp integration
- `run_whatsapp.py` - Webhook server
- `WHATSAPP_QUICKSTART.md` - Setup guide

**Run:**
```bash
python3 run_whatsapp.py
```

**Pros:**
- Mobile-native
- Everyone has WhatsApp
- Easy to use
- Session persistence

**Cons:**
- Requires Twilio account
- Needs public webhook URL (ngrok for dev)
- Sandbox limits for testing

---

## Architecture

All channels share the same core components:

```
┌─────────────────────────────────────────────────────────┐
│                    Communication Layer                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Streamlit  │  │    Slack    │  │  WhatsApp   │     │
│  │     UI      │  │   Handler   │  │   Handler   │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
└─────────┼─────────────────┼─────────────────┼───────────┘
          │                 │                 │
          └────────┬────────┴────────┬────────┘
                   │                 │
          ┌────────▼─────────────────▼────────┐
          │      Session Manager               │
          │   (conversation context)           │
          └────────┬───────────────────────────┘
                   │
          ┌────────▼────────┐
          │  Agent Runner   │
          │  (LangChain)    │
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │  Tool Registry  │
          │  (5 email tools)│
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │  Gmail Client   │
          │  (OAuth API)    │
          └─────────────────┘
```

## Code Reuse

### Shared Components (100% reuse)

**Agent & Tools** (`src/agent/`)
- `runner.py` - Agent execution
- `providers.py` - AI provider abstraction
- `tools/` - Email analysis tools

**Gmail Client** (`src/gmail/`)
- `simple_client.py` - Gmail API wrapper
- `parser.py` - Email parsing

**Configuration** (`src/config/`)
- `settings.py` - Centralized config

### Channel-Specific Code

**Streamlit** (`streamlit_app_simple.py`)
- UI rendering
- Chat interface
- Session state management

**Slack** (`src/slack/`)
- Event handlers
- Message formatters
- Thread management

**WhatsApp** (`src/whatsapp/`)
- Webhook server
- Message handlers
- Response formatters

## Adding a New Channel

Want to add Telegram, Discord, or another channel? Here's how:

### 1. Create Channel Module

```bash
mkdir src/telegram
touch src/telegram/__init__.py
touch src/telegram/handlers.py
touch src/telegram/formatters.py
```

### 2. Implement Handler

```python
class TelegramHandler:
    def __init__(self, agent_runner, session_manager):
        self.agent = agent_runner
        self.sessions = session_manager

    def handle_message(self, user_id, message):
        # Get session history
        history = self.sessions.get_history(user_id)

        # Run agent (reuse existing!)
        response = self.agent.run(message, history)

        # Update session
        self.sessions.add_message(user_id, "human", message)
        self.sessions.add_message(user_id, "ai", response)

        return response
```

### 3. Create Entry Point

```python
# run_telegram.py
from src.telegram.handlers import TelegramHandler
from src.agent import AgentRunner, SessionManager
# ... initialize agent (reuse existing code)

handler = TelegramHandler(agent_runner, session_manager)
# ... start Telegram bot
```

### 4. Add Configuration

Update `src/config/settings.py`:
```python
class TelegramSettings(BaseSettings):
    bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
```

That's it! All the agent logic, tools, and Gmail integration work automatically.

## Channel Comparison

| Feature | Streamlit | Slack | WhatsApp |
|---------|-----------|-------|----------|
| **Mobile** | ⚠️ Web only | ✅ Native app | ✅ Native app |
| **Setup** | ⭐⭐⭐⭐⭐ Easy | ⭐⭐⭐ Medium | ⭐⭐⭐⭐ Easy |
| **Multi-user** | ❌ No | ✅ Yes | ⚠️ Personal | **Notifications** | ❌ No | ✅ Yes | ✅ Yes |
| **Cost** | 💰 Free | 💰 Free | 💰 Free tier |
| **Best for** | Development | Teams | Personal |

## Future Channels

Easy to add:
- **Telegram** - Similar to WhatsApp
- **Discord** - Similar to Slack
- **SMS** - Simple text interface
- **Email** - Reply to emails
- **Voice** - Twilio Voice API
- **iMessage** - Requires Mac server

## Configuration

All channels configured in `.env`:

```bash
# AI (required for all)
ANTHROPIC_API_KEY=sk-ant-...

# Gmail (required for all)
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
GMAIL_REFRESH_TOKEN=...

# Streamlit (no extra config needed)

# Slack (optional)
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...

# WhatsApp (optional)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+1...
```

## Running Multiple Channels

You can run multiple channels simultaneously:

```bash
# Terminal 1: Streamlit
streamlit run streamlit_app_simple.py

# Terminal 2: Slack
python src/main.py

# Terminal 3: WhatsApp
python3 run_whatsapp.py

# Terminal 4: ngrok (for WhatsApp)
ngrok http 5000
```

All channels share the same Gmail credentials and AI provider!

## Session Management

Each channel maintains separate conversation history:
- Streamlit: One session per browser
- Slack: One session per thread
- WhatsApp: One session per phone number

Sessions are independent - your Slack conversation doesn't affect WhatsApp.

## Benefits of Multi-Channel Architecture

1. **Code Reuse** - Write once, use everywhere
2. **Consistent Experience** - Same capabilities across channels
3. **Easy Testing** - Use Streamlit for quick tests
4. **Flexibility** - Choose the best channel for each use case
5. **Scalability** - Add new channels without changing core logic

## Learn More

- **Streamlit Setup:** `SETUP_SIMPLE.md`
- **Slack Setup:** `README.md`
- **WhatsApp Setup:** `WHATSAPP_QUICKSTART.md`
- **Architecture Details:** `ARCHITECTURE.md`

Ready to extend to more channels! 🚀
