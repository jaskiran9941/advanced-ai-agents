# Streamlit UI Guide

The Email Analysis Bot now includes a **Streamlit web interface** for easy testing and interaction without needing Slack!

## Features

### Chat Interface
- 💬 **Natural conversation** with the bot
- 📝 **Chat history** preserved during session
- ⏱️ **Timestamps** for all messages
- 🔄 **Real-time responses** with thinking indicator

### Sidebar
- ⚙️ **Configuration display** (AI provider, tools available)
- 📊 **Quick stats** (unread email count)
- 🛠️ **Tool listing** with descriptions
- 🗑️ **Clear chat** button

### Quick Actions
- 📬 Pre-configured example queries
- 🎯 One-click common questions
- 💡 Suggested queries for new users

## Quick Start

### 1. Install Dependencies

```bash
cd email-slack-bot
source venv/bin/activate  # If not already activated
pip install streamlit
# Or reinstall all requirements
pip install -r requirements.txt
```

### 2. Setup (if not already done)

```bash
# Setup Gmail OAuth
python scripts/setup_gmail.py

# Configure .env file
cp .env.example .env
# Edit .env with your AI provider API key
```

### 3. Run Streamlit App

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

### First Time Setup

1. When you first open the app, check the sidebar for initialization status
2. If you see "✅ Bot initialized successfully!" - you're ready!
3. If you see errors, follow the setup instructions in the sidebar

### Asking Questions

Simply type your question in the chat input at the bottom:

**Example queries:**
- "What are my unread emails?"
- "Show me emails from john@example.com"
- "List emails from the last 7 days"
- "Who has emailed me most recently?"
- "Summarize emails about [topic]"

### Quick Action Buttons

For first-time users, three quick action buttons are available:
- **📬 Unread emails** - Check your unread messages
- **🔍 Recent emails** - See emails from last 3 days
- **👥 Email summary** - See who's been emailing you

### Viewing Configuration

Click the expandable sections in the sidebar to see:
- **Configuration Details** - AI provider, scopes, tool count
- **Available Tools** - List of all tools the bot can use

### Clearing Chat

Click the "Clear Chat History" button in the sidebar to:
- Reset the conversation
- Clear chat history
- Start fresh

## Configuration

### Streamlit Theme

The app uses a custom theme defined in `.streamlit/config.toml`:
- Primary color: Google Blue (#4285F4)
- Clean, professional interface
- Sans-serif font

You can customize by editing `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#4285F4"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F5F5"
textColor = "#262730"
```

### Port and Server Settings

Default port: `8501`

To change the port:
```bash
streamlit run streamlit_app.py --server.port 8080
```

Or edit `.streamlit/config.toml`:
```toml
[server]
port = 8080
```

## Comparison: Streamlit vs Slack

| Feature | Streamlit UI | Slack Bot |
|---------|-------------|-----------|
| **Setup** | Just run locally | Requires Slack app setup |
| **Testing** | ✅ Perfect for testing | Needs workspace |
| **Multi-user** | ❌ Single user (local) | ✅ Team collaboration |
| **Deployment** | Can deploy to Streamlit Cloud | Runs as service |
| **Notifications** | ❌ No notifications | ✅ Real-time notifications |
| **Mobile** | ✅ Responsive web | ✅ Slack mobile app |
| **Best for** | Development & demos | Production use |

## Development Tips

### Debugging

Enable verbose logging in `streamlit_app.py`:
```python
agent_runner = AgentRunner(
    llm=llm,
    tool_registry=tool_registry,
    max_iterations=10,
    verbose=True,  # Set to True for debugging
)
```

View logs in the terminal where Streamlit is running.

### Auto-reload

Streamlit automatically reloads when you save changes to:
- `streamlit_app.py`
- Any imported modules

Just save and refresh the browser!

### Session State

Chat history is stored in `st.session_state.messages`

To reset during development, click "Clear Chat History" or restart Streamlit.

## Troubleshooting

### "Bot not initialized" Error

**Cause:** Missing Gmail credentials or AI API keys

**Solution:**
1. Run `python scripts/setup_gmail.py`
2. Ensure `.env` file has `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
3. Restart Streamlit

### "Could not fetch email stats" Warning

**Cause:** Gmail API connection issue

**Solution:**
1. Check `credentials.json` exists
2. Delete `token.json` and re-run `scripts/setup_gmail.py`
3. Verify Gmail API is enabled in Google Cloud Console

### Slow Response Times

**Cause:** First request to AI provider or Gmail API

**Solutions:**
- First request may take 5-10 seconds (normal)
- Subsequent requests are faster
- Consider adding caching in future (Phase 3)

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Kill existing Streamlit process
pkill -f streamlit

# Or use different port
streamlit run streamlit_app.py --server.port 8502
```

## Advanced Features

### Running on Network

To access from other devices on your network:

```bash
streamlit run streamlit_app.py --server.address 0.0.0.0
```

Then access from any device: `http://YOUR_IP:8501`

### Deploying to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets (API keys) in Streamlit dashboard
5. Deploy!

**Note:** You'll need to handle Gmail OAuth differently for cloud deployment.

## Keyboard Shortcuts

- **Ctrl/Cmd + Enter** - Send message (in chat input)
- **Ctrl/Cmd + R** - Reload page
- **/** - Focus on chat input

## Privacy & Security

### Local Usage
- All data stays on your machine
- Gmail OAuth tokens stored locally
- No data sent anywhere except:
  - Gmail API (Google)
  - AI Provider API (Anthropic/OpenAI)

### Cloud Deployment
- ⚠️ Be careful with OAuth tokens
- Use Streamlit secrets for API keys
- Consider implementing user authentication
- Don't commit credentials to GitHub

## Future Enhancements

Planned features for Streamlit UI:

### Phase 2: Analytics Dashboard
- 📊 Spending charts and graphs
- 📈 Email volume over time
- 👥 Top senders visualization

### Phase 3: Advanced Features
- 🔍 Semantic search interface
- 📎 Attachment viewer
- 📧 Email preview pane
- 🏷️ Label/category filtering

### Phase 4: Collaboration
- 👥 Multi-user support
- 🔐 Authentication
- 💾 Saved queries
- 📤 Export functionality

## Example Workflows

### 1. Morning Email Check
```
1. Open Streamlit app
2. Click "📬 Unread emails"
3. Review unread count and recent emails
4. Ask follow-up: "Show me the most important ones"
```

### 2. Finding Specific Information
```
1. Ask: "Show me emails from john@example.com about the project"
2. Review results
3. Ask: "Summarize the latest one"
4. Get quick summary
```

### 3. Weekly Email Review
```
1. Ask: "Show me all emails from the last 7 days"
2. Ask: "Who emailed me the most?"
3. Ask: "Any important updates I should know about?"
```

## Support

### Getting Help
- Check this guide for common issues
- Review main README.md for setup
- Check terminal logs for errors
- Verify Gmail and AI API configurations

### Reporting Issues
If you find bugs or have suggestions:
1. Check existing documentation
2. Verify configuration is correct
3. Include error messages from terminal
4. Note your OS and Python version

## Summary

The Streamlit UI provides a user-friendly way to:
- ✅ Test the bot locally without Slack
- ✅ Demonstrate functionality
- ✅ Debug and develop new features
- ✅ Quick email analysis on demand

Perfect for development, testing, and personal use!

**Run it now:**
```bash
streamlit run streamlit_app.py
```

Happy email analyzing! 🚀
