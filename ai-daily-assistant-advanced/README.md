# Email Analysis Slack Bot

An AI-powered Slack bot that analyzes your Gmail emails and answers questions using natural language. Built with Python, LangChain, and multi-provider AI support (Anthropic Claude & OpenAI GPT).

**✨ New:** Now includes a **Streamlit web UI** for easy testing without Slack! See [Streamlit Guide](STREAMLIT_GUIDE.md).

## Features

### Current (Phase 1 - MVP + Extensions)
- **Multi-Channel Support**: 🆕 Streamlit, Slack, and WhatsApp interfaces
- **Gmail Analysis**: Search, read, and analyze emails via natural language (5 tools)
- **Financial Analysis**: 🆕 Extract receipts and track spending from emails (3 tools)
- **Calendar Integration**: 🆕 Optional Composio integration for Google Calendar (2 tools)
- **Multi-Provider AI**: Support for both Anthropic Claude and OpenAI GPT-4
- **Hybrid Tool Architecture**: Custom tools + 150+ Composio tools (optional)
- **Production-Ready WhatsApp**: Message splitting, session cleanup, signature validation

### Example Queries
**Email Analysis:**
- "What are my unread emails?"
- "What is john@example.com saying?"
- "Show me emails from last week about the project"
- "Summarize emails from Sarah"

**Financial Analysis:**
- "Extract receipts from the last 30 days"
- "Analyze my spending by vendor this month"
- "Show me my monthly spending report"

**Calendar (with Composio):**
- "Find my next free slot for a 30-minute meeting"
- "What's on my calendar today?"

### Planned Features (Future Phases)
- **Phase 3**: Semantic search with vector database
- **Phase 4**: Production deployment (Pub/Sub, webhooks, monitoring)
- **Phase 5**: Additional channels (iMessage, Telegram, Discord)
- **Phase 6**: Advanced analytics and insights dashboard

## Architecture

```
Gmail API → Email Processor → Vector DB (future)
     ↓
Slack Bot ← AI Agent ← Tool Registry → Email Analysis Tools
```

### Tech Stack
- **Language**: Python 3.11+
- **Slack**: slack-bolt (Socket Mode for dev)
- **Gmail**: google-api-python-client
- **AI Framework**: LangChain
- **AI Providers**: Anthropic Claude, OpenAI GPT-4
- **Logging**: structlog

## Prerequisites

1. **Python 3.11+**
2. **Google Cloud Project** with Gmail API enabled
3. **Slack Workspace** with bot permissions
4. **AI Provider API Key** (Anthropic or OpenAI)

## Installation

### 1. Clone and Setup Python Environment

```bash
cd email-slack-bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup Gmail API

#### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the Gmail API:
   - Navigate to **APIs & Services → Library**
   - Search for "Gmail API"
   - Click **Enable**

#### Step 2: Create OAuth Credentials
1. Navigate to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth client ID**
3. Application type: **Desktop app**
4. Download the credentials JSON file
5. Save it as `credentials.json` in the project root

#### Step 3: Run Setup Wizard
```bash
python scripts/setup_gmail.py
```

This will:
- Verify your credentials file
- Open a browser for OAuth authorization
- Save the token for future use
- Test the Gmail API connection

### 3. Setup Slack App

#### Step 1: Create Slack App
1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App → From scratch**
3. Name your app (e.g., "Email Assistant")
4. Select your workspace

#### Step 2: Configure Bot Permissions
1. Navigate to **OAuth & Permissions**
2. Add the following **Bot Token Scopes**:
   - `app_mentions:read`
   - `chat:write`
   - `im:history`
   - `im:read`
   - `im:write`
3. Click **Install to Workspace**
4. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

#### Step 3: Enable Socket Mode (for development)
1. Navigate to **Socket Mode**
2. Enable Socket Mode
3. Create an **App-Level Token** with `connections:write` scope
4. Copy the token (starts with `xapp-`)

#### Step 4: Enable Events
1. Navigate to **Event Subscriptions**
2. Enable Events
3. Subscribe to these bot events:
   - `app_mention`
   - `message.im`
4. Save changes

#### Step 5: Get Signing Secret
1. Navigate to **Basic Information**
2. Copy the **Signing Secret**

### 4. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret

# AI Provider Configuration
ANTHROPIC_API_KEY=sk-ant-your-key
# OR
OPENAI_API_KEY=sk-your-key

# Gmail Configuration (optional, defaults provided)
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json

# Application Settings
DEFAULT_AI_PROVIDER=anthropic  # or 'openai'
LOG_LEVEL=INFO
```

## Usage

### Option 1: Streamlit Web UI (Recommended for Testing)

The easiest way to test the bot is through the Streamlit interface:

```bash
streamlit run streamlit_app.py
```

This opens a web interface at `http://localhost:8501` where you can:
- Chat with the bot in a user-friendly interface
- See available tools and configuration
- View unread email count
- Clear chat history
- No Slack setup required!

**See [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md) for detailed Streamlit documentation.**

### Option 2: Slack Bot (For Production Use)

Start the Slack bot:

```bash
python src/main.py
```

You should see:
```
Email Analysis Slack Bot is ready!
Configuration: gmail_scopes=['https://www.googleapis.com/auth/gmail.readonly'], ai_provider='anthropic', tool_count=5
Bolt app is running!
```

### Using the Bot in Slack

#### In Channels (requires @mention):
```
@EmailBot What are my unread emails?
@EmailBot What is john@example.com saying?
@EmailBot Show me emails about "quarterly report"
```

#### In Direct Messages (no @mention needed):
```
List my unread emails
What did Sarah send me last week?
Show me emails with attachments
```

### Conversation Threads
The bot maintains context within Slack threads. You can have multi-turn conversations:

```
You: What are my unread emails?
Bot: You have 5 unread emails...

You: Show me the most recent one
Bot: [Shows email details]

You: Who sent it?
Bot: [Provides sender info]
```

## Project Structure

```
email-slack-bot/
├── src/
│   ├── slack/              # Slack bot integration
│   │   ├── bot.py         # Bot initialization
│   │   ├── handlers.py    # Message event handlers
│   │   └── formatters.py  # Message formatting
│   ├── gmail/             # Gmail API client
│   │   ├── client.py      # Gmail client
│   │   └── parser.py      # Email parsing
│   ├── agent/             # AI agent
│   │   ├── runner.py      # Agent execution
│   │   ├── providers.py   # AI provider abstraction
│   │   └── tools/         # Tool implementations
│   │       ├── registry.py     # Tool registry
│   │       └── email_tools.py  # Email tools
│   ├── config/            # Configuration
│   │   └── settings.py    # Pydantic settings
│   └── main.py            # Entry point
├── scripts/
│   └── setup_gmail.py     # Gmail OAuth setup wizard
├── tests/                 # Tests (to be added)
├── .env.example           # Example environment file
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

## Available Tools

### Email Analysis Tools (5)
1. **list_unread**: Get count and list of unread emails
2. **search_emails**: Search emails with Gmail query operators
3. **get_email_by_id**: Get full email content by ID
4. **get_sender_emails**: Get all emails from a specific sender
5. **summarize_thread**: Summarize an email conversation thread

### Financial Tools (3)
6. **extract_receipts**: Extract receipts from emails for spending analysis
7. **analyze_spending_by_vendor**: Group spending by vendor from receipts
8. **monthly_spending_report**: Generate monthly spending summary

### Calendar Helper Tools (2)
9. **find_next_free_slot**: Find next available calendar time
10. **summarize_todays_meetings**: Get today's meeting summary

### Google Workspace Tools via Composio (150+) - OPTIONAL
When enabled, provides access to:
- **Google Calendar** (15+ actions): Create/list/update events, find free slots
- **Google Drive** (20+ actions): List/search/read files, export documents
- **Google Docs** (10+ actions): Create/update/copy documents

See [Composio Integration](#composio-integration-optional) section below for setup instructions.

## Configuration

### Tool Policy
You can control which tools are available by editing `.env` or `src/config/settings.py`:

```python
# Allow only specific tools
allowlist = ["list_unread", "search_emails", "get_sender_emails"]

# Block specific tools
blocklist = []
```

### AI Provider Selection
The bot supports multiple AI providers. Configure in `.env`:

```bash
# Use Anthropic Claude (recommended)
DEFAULT_AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Or use OpenAI GPT-4
DEFAULT_AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

### Switching Providers
You can register multiple providers and switch between them:

```python
# Both providers will be initialized
# Default provider is used unless specified
```

## Composio Integration (Optional)

Enable Google Workspace integration with 150+ production-ready tools:

### Setup
1. Get Composio API key from https://app.composio.dev
2. Add to `.env`:
   ```bash
   COMPOSIO_API_KEY=your-composio-api-key
   COMPOSIO_ENABLED=true
   COMPOSIO_APPS=GOOGLECALENDAR,GOOGLEDRIVE,GOOGLEDOCS
   COMPOSIO_ENTITY_ID=default
   ```
3. Install: `pip install composio-langchain`

### OAuth Connection
For Google Calendar/Drive/Docs access:
```python
from src.agent.tools.composio_tools import initiate_composio_connection

auth_url = initiate_composio_connection(
    app_name="GOOGLECALENDAR",
    entity_id="user@example.com",
    redirect_url="http://localhost:8501/oauth/callback"
)
print(f"Visit: {auth_url}")
```

### Available Apps
- **GOOGLECALENDAR** - Create/manage calendar events, find free slots
- **GOOGLEDRIVE** - Access and search files, export documents
- **GOOGLEDOCS** - Create and edit documents
- **150+ more apps available** - Slack, GitHub, Gmail (send), Notion, etc.

### Example Queries with Composio
- "Schedule a meeting for tomorrow at 2pm"
- "Find files in my Drive about project X"
- "Create a new doc with meeting notes"
- "What's on my calendar today?"

## Troubleshooting

### Gmail API Issues

**Error: "credentials.json not found"**
- Run `scripts/setup_gmail.py` to setup Gmail OAuth
- Make sure `credentials.json` is in the project root

**Error: "Token has been expired or revoked"**
- Delete `token.json` and run `scripts/setup_gmail.py` again

**Error: "Insufficient Permission"**
- Check that Gmail API is enabled in Google Cloud Console
- Verify OAuth scopes include `gmail.readonly`

### Slack Issues

**Error: "Bot not responding"**
- Verify bot is installed in your workspace
- Check that Socket Mode is enabled
- Ensure `SLACK_APP_TOKEN` is set correctly
- Verify bot has required OAuth scopes

**Error: "Not authed"**
- Check `SLACK_BOT_TOKEN` is correct
- Re-install the app to workspace if needed

### AI Provider Issues

**Error: "API key not found"**
- Verify `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` is set in `.env`
- Check for typos in the key

**Error: "Rate limit exceeded"**
- Wait and retry
- Consider implementing rate limiting in production

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
ruff check src/
```

### Type Checking
```bash
mypy src/
```

## Roadmap

### Phase 2: Financial Analysis (Week 3)
- Transaction extraction from receipts
- Spending analysis by vendor
- Monthly/weekly spending reports

### Phase 3: Vector Search (Week 4)
- ChromaDB integration
- Semantic email search
- Background email sync

### Phase 4: Production (Week 5-6)
- Pub/Sub for real-time updates
- Events API (replace Socket Mode)
- Monitoring and logging
- Deployment guide

### Phase 5: Multi-Channel (Future)
- WhatsApp integration
- iMessage support
- Telegram bot
- Discord integration

### Phase 6: Tool Expansion (Future)
- Google Calendar tools
- Google Drive integration
- Web search capabilities
- Booking and action tools
- ~50 total tools

## Architecture Patterns

This project follows key architecture patterns from [Clawdbot](https://github.com/anthropics/clawdbot):

1. **Tool Registry Pattern**: Extensible tool system with allowlist/blocklist
2. **Multi-Provider Support**: Provider abstraction layer for AI models
3. **Session Management**: Per-thread conversation context
4. **Modular Design**: Clear separation of concerns (Slack, Gmail, Agent)

## Future Considerations

### Scalability
- Move from Socket Mode to Events API
- Implement message queuing (Celery + Redis)
- Add caching layer for frequently accessed emails
- Use Pub/Sub for real-time Gmail updates

### Security
- Implement user authentication
- Add rate limiting
- Encrypt stored tokens
- Audit tool usage

### Extensibility
- Plugin system for custom tools
- Dynamic tool loading
- Multi-user support
- Custom agent prompts per user

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Create an issue](#)
- Documentation: See this README
- Examples: Check `scripts/` directory

## Acknowledgments

- Inspired by [Clawdbot](https://github.com/anthropics/clawdbot) architecture
- Built with [LangChain](https://python.langchain.com/)
- Powered by [Anthropic Claude](https://www.anthropic.com/) and [OpenAI](https://openai.com/)
