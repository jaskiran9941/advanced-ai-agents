# 🚀 Quick Start - Everything in .env

**This is the simplified setup where all credentials are in the `.env` file!**

## What You Need (2 things)

1. ✅ **AI API Key** - Anthropic or OpenAI (required)
2. ✅ **Gmail OAuth** - One-time Google Cloud setup (required)

## Setup (5 minutes)

### 1️⃣ Install Dependencies

```bash
pip install google-api-python-client google-auth-oauthlib \
            langchain langchain-anthropic streamlit python-dotenv \
            structlog pydantic pydantic-settings
```

### 2️⃣ Add Your AI API Key

Edit `.env` file and add:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get key from: https://console.anthropic.com/

### 3️⃣ Setup Gmail (One-time)

**Part A: Get OAuth credentials from Google**
1. Go to https://console.cloud.google.com/
2. Create project → Enable "Gmail API"
3. Create OAuth credentials (Desktop app)
4. Download as `credentials.json` → Save in project root

**Part B: Run setup script**
```bash
python3 scripts/setup_gmail_simple.py
```

This opens your browser, you authorize it, and it saves everything to `.env` automatically!

### 4️⃣ Run Streamlit

```bash
python3 -m streamlit run streamlit_app_simple.py
```

Opens at: http://localhost:8501

## Try It

Ask questions like:
- "What are my unread emails?"
- "Show me emails from john@example.com"
- "List emails from the last week"

## How It Works

- **LangChain Agent** - Intelligently picks which tool to use
- **5 Gmail Tools** - Search, list unread, get by ID, etc.
- **AI Provider** - Claude or GPT-4 for natural language
- **All in .env** - No separate token files!

## Files Overview

- `📄 .env` - All your credentials (AI key + Gmail OAuth)
- `📄 credentials.json` - Download from Google Cloud (one-time)
- `🐍 streamlit_app_simple.py` - Main app to run
- `🐍 scripts/setup_gmail_simple.py` - Gmail setup helper
- `📘 SETUP_SIMPLE.md` - Detailed instructions

Need help? Check SETUP_SIMPLE.md for troubleshooting!
