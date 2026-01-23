# Simplified Setup Guide - All credentials in .env

This guide shows how to run the email bot with all credentials in the `.env` file.

## Prerequisites

- Python 3.11+
- Google account with Gmail
- Anthropic or OpenAI API key

## Setup Steps

### Step 1: Install Dependencies

```bash
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2 \
            langchain langchain-anthropic langchain-openai \
            streamlit python-dotenv structlog pydantic pydantic-settings
```

### Step 2: Get AI API Key

Choose one:

**Option A: Anthropic Claude (Recommended)**
1. Go to https://console.anthropic.com/
2. Create an API key
3. Copy it (starts with `sk-ant-`)

**Option B: OpenAI GPT-4**
1. Go to https://platform.openai.com/api-keys
2. Create an API key
3. Copy it (starts with `sk-`)

### Step 3: Add AI API Key to .env

Open `.env` file and add your key:

```bash
# For Anthropic
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
DEFAULT_AI_PROVIDER=anthropic

# OR for OpenAI
# OPENAI_API_KEY=sk-your-actual-key-here
# DEFAULT_AI_PROVIDER=openai
```

### Step 4: Setup Gmail OAuth (One-time)

**4.1 Get OAuth Credentials from Google Cloud**

1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. **Enable Gmail API:**
   - Click "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. **Create OAuth Credentials:**
   - Click "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as application type
   - Name it (e.g., "Email Bot")
   - Download the JSON file
5. **Save the file as `credentials.json`** in the project root:
   ```
   email-slack-bot/credentials.json
   ```

**4.2 Run the Setup Script**

```bash
python3 scripts/setup_gmail_simple.py
```

This will:
- Read your `credentials.json`
- Open your browser for OAuth authorization (authorize it - it's safe!)
- Extract the OAuth tokens
- **Automatically save everything to `.env`**

After this, your `.env` will have all Gmail credentials!

### Step 5: Run Streamlit

```bash
streamlit run streamlit_app_simple.py
```

Or use Python module:

```bash
python3 -m streamlit run streamlit_app_simple.py
```

The app will open at http://localhost:8501

## What's in .env After Setup

After running the setup script, your `.env` will contain:

```bash
# AI Configuration
ANTHROPIC_API_KEY=sk-ant-your-key-here
DEFAULT_AI_PROVIDER=anthropic

# Gmail OAuth (Auto-filled by setup script)
GMAIL_CLIENT_ID=123456789.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-abc123xyz
GMAIL_REFRESH_TOKEN=1//0abcd1234xyz
GMAIL_TOKEN_URI=https://oauth2.googleapis.com/token
```

That's it! Everything is in one file.

## Usage

Once running, try these queries in the Streamlit interface:

- "What are my unread emails?"
- "Show me emails from john@example.com"
- "List emails from the last 7 days"
- "Who has emailed me recently?"
- "Summarize emails about [topic]"

## Troubleshooting

### "credentials.json not found"
- Make sure you downloaded the OAuth credentials from Google Cloud Console
- Save it exactly as `credentials.json` in the project root

### "Missing Gmail OAuth credentials"
- Run: `python3 scripts/setup_gmail_simple.py`
- This will populate the `.env` file with Gmail credentials

### "Invalid API key"
- Check your `.env` file
- Make sure the API key doesn't have quotes or spaces
- Verify the key is valid in your AI provider console

### "Could not fetch email stats"
- Your Gmail OAuth might have expired
- Re-run: `python3 scripts/setup_gmail_simple.py`

## How It Works

1. **AI Provider**: Uses Anthropic Claude or OpenAI GPT-4 for natural language understanding
2. **LangChain Agent**: Intelligently decides which tools to use based on your question
3. **Gmail API**: Fetches emails using OAuth credentials from `.env`
4. **Tools**: 5 email analysis tools (list unread, search, get by ID, etc.)

## Next Steps

- Try different queries to see the agent in action
- Check the sidebar to see which tools are available
- View the chat history to see how the agent maintains context
- Explore the code to understand LangChain agents

Enjoy! 🚀
