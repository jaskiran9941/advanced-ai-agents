# Quick Start Guide

Get your Email Analysis Slack Bot up and running in 15 minutes.

## Prerequisites Checklist
- [ ] Python 3.11+ installed
- [ ] Google account with Gmail
- [ ] Slack workspace (admin or app install permissions)
- [ ] Anthropic or OpenAI API key

## Step-by-Step Setup

### 1. Install Dependencies (2 minutes)

```bash
cd email-slack-bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup Gmail API (5 minutes)

#### Quick Steps:
1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project → Enable "Gmail API"
3. Create OAuth Desktop credentials
4. Download as `credentials.json` to project root
5. Run setup:
```bash
python scripts/setup_gmail.py
```

The script will open your browser for authorization. This is normal and safe.

### 3. Setup Slack App (5 minutes)

#### Quick Steps:
1. Go to [api.slack.com/apps](https://api.slack.com/apps) → "Create New App"
2. Choose "From scratch", name it (e.g., "Email Bot")
3. **OAuth & Permissions** → Add scopes:
   - `app_mentions:read`
   - `chat:write`
   - `im:history`
   - `im:read`
   - `im:write`
4. Install to workspace → Copy "Bot User OAuth Token" (`xoxb-...`)
5. **Socket Mode** → Enable → Create token → Copy App Token (`xapp-...`)
6. **Event Subscriptions** → Enable → Subscribe to:
   - `app_mention`
   - `message.im`
7. **Basic Information** → Copy "Signing Secret"

### 4. Configure Environment (2 minutes)

```bash
cp .env.example .env
```

Edit `.env`:
```bash
SLACK_BOT_TOKEN=xoxb-YOUR-TOKEN-HERE
SLACK_APP_TOKEN=xapp-YOUR-TOKEN-HERE
SLACK_SIGNING_SECRET=YOUR-SECRET-HERE

# Choose ONE provider:
ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE
# OR
# OPENAI_API_KEY=sk-YOUR-KEY-HERE

DEFAULT_AI_PROVIDER=anthropic  # or 'openai'
```

### 5. Start the Bot (1 minute)

```bash
python src/main.py
```

You should see:
```
Email Analysis Slack Bot is ready!
✓ Bolt app is running!
```

### 6. Test in Slack

Open Slack and try:

**In a channel:**
```
@EmailBot What are my unread emails?
```

**In a DM with the bot:**
```
List my unread emails
```

## Common Issues

### "credentials.json not found"
- Make sure you downloaded OAuth credentials from Google Cloud Console
- Save it as `credentials.json` in the project root (not in any subdirectory)

### "Bot not responding in Slack"
- Check Socket Mode is enabled
- Verify bot is installed to workspace
- Make sure you copied all three Slack tokens correctly

### "Invalid API key"
- Double-check your Anthropic/OpenAI key in `.env`
- Make sure no spaces or quotes around the key

## Next Steps

Once working, try these queries:
- "What is john@example.com saying?"
- "Show me emails from last week"
- "Summarize emails about [topic]"
- "Who sent me the most emails?"

## Expanding Functionality

The bot is designed to grow! See README.md for:
- Adding financial analysis (Phase 2)
- Enabling semantic search (Phase 3)
- Production deployment (Phase 4)
- Multi-channel support (Phase 5)

## Getting Help

- Check full setup details: `README.md`
- Review logs for errors
- Verify all prerequisites are met
- Test Gmail API separately: `python scripts/setup_gmail.py`

Happy email analyzing! 🚀
