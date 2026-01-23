# 🚀 Quick Start: Run Streamlit UI

## One-Command Setup

If you've already set up Gmail API, just run:

```bash
streamlit run streamlit_app.py
```

That's it! Your browser will open to `http://localhost:8501`

## First Time Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Gmail
```bash
python scripts/setup_gmail.py
```
Follow the browser prompts to authorize.

### 3. Configure AI Provider
```bash
cp .env.example .env
```

Edit `.env` and add ONE of these:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key
# OR
OPENAI_API_KEY=sk-your-key
```

### 4. Launch!
```bash
streamlit run streamlit_app.py
```

## What You'll See

### Interface Preview

```
┌──────────────────────────────────────────────────────────┐
│  📧 Email Analysis Bot                                    │
│  Ask questions about your Gmail emails                    │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  💡 Try these example queries:                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│  │📬 Unread │ │🔍 Recent │ │👥 Summary│                │
│  │  emails  │ │  emails  │ │          │                │
│  └──────────┘ └──────────┘ └──────────┘                │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 💬 Ask about your emails...                     │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
└──────────────────────────────────────────────────────────┘

Sidebar shows:
  ✅ Bot initialized successfully!
  📊 Unread Emails: 5
  🛠️ Configuration Details
  📝 Available Tools
```

## Sample Conversation

```
You: What are my unread emails?
🤔 Thinking...

Bot: You have 5 unread email(s).

Recent unread emails:

- From: John Doe
  Subject: Project Update
  Date: Jan 22, 2:30 PM

- From: Sarah Smith
  Subject: Meeting Tomorrow
  Date: Jan 22, 11:45 AM

... and 3 more unread emails.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You: Show me what John said

🤔 Thinking...

Bot: Found 1 email(s) from john@example.com:

Subject: Project Update
Date: Jan 22, 2:30 PM
Preview: Hi team, I wanted to share an update on the Q1 project...
```

## Features You Can Use

### Chat Interface
- Type any question about your emails
- Get natural language responses
- Conversation history maintained
- Timestamps on all messages

### Quick Actions
- **📬 Unread emails** - One click to check unread
- **🔍 Recent emails** - See last 3 days
- **👥 Email summary** - Top senders

### Sidebar
- **Configuration** - See AI provider, tools
- **Stats** - Unread email count (live)
- **Tools** - List of available email tools
- **Clear Chat** - Reset conversation

## Example Questions to Try

### Basic Queries
- "What are my unread emails?"
- "Show me emails from today"
- "List emails from last week"

### Sender Queries
- "What is john@example.com saying?"
- "Show me all emails from Sarah"
- "Who emailed me recently?"

### Search Queries
- "Find emails about the project"
- "Show me emails with subject 'meeting'"
- "Emails from last month about quarterly report"

### Thread Queries
- "Summarize this email thread"
- "What's the conversation about?"

## Keyboard Shortcuts

- **Enter** - Send message
- **Ctrl/Cmd + R** - Refresh page
- **Ctrl/Cmd + K** - Clear input

## Troubleshooting

### Port Already in Use
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Bot Not Initialized
1. Check `.env` file exists with API key
2. Run `python scripts/setup_gmail.py`
3. Restart Streamlit

### Gmail Connection Error
1. Delete `token.json`
2. Run `python scripts/setup_gmail.py` again
3. Restart Streamlit

## Tips

- **First message** may take 5-10 seconds (normal)
- **Follow-up questions** are faster with context
- **Clear chat** to start fresh conversation
- **Check sidebar** for quick stats

## Next Steps

Once comfortable with Streamlit:
1. Try the Slack bot: `python src/main.py`
2. Add more tools (Phase 2: spending analysis)
3. Enable semantic search (Phase 3: vector DB)

## Learn More

- **Streamlit Guide**: See [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md)
- **Full Setup**: See [README.md](README.md)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Ready to go? Run this now:**
```bash
streamlit run streamlit_app.py
```

Your browser will open automatically! 🎉
