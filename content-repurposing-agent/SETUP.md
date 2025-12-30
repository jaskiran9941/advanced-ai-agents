# Quick Setup Guide

Get your Content Repurposing Agent up and running in 5 minutes!

## Prerequisites

- Python 3.9+
- API keys from service providers (see below)

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure API Keys

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:

### Required API Keys:

**LLM Providers (choose at least one):**
- `ANTHROPIC_API_KEY` - Get from [Anthropic Console](https://console.anthropic.com/)
- `GOOGLE_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- `OPENAI_API_KEY` - Get from [OpenAI Platform](https://platform.openai.com/api-keys)

**Image Generation:**
- `REPLICATE_API_TOKEN` - Get from [Replicate](https://replicate.com/account/api-tokens)

**SEO Research:**
- `SERPAPI_API_KEY` - Get from [SerpAPI](https://serpapi.com/manage-api-key)

### Example `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
GOOGLE_API_KEY=AIzaSy-your-key-here
OPENAI_API_KEY=sk-proj-your-key-here
REPLICATE_API_TOKEN=r8_your-token-here
SERPAPI_API_KEY=your-serpapi-key-here
```

## Step 3: Run the Application

```bash
streamlit run ui/app.py
```

The app will open at `http://localhost:8501`

## Step 4: Link Social Media Accounts

### Twitter/X Setup:

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app (or use existing)
3. Go to app settings → User authentication settings
4. Enable OAuth 2.0
5. Add redirect URI: `http://localhost:5000/twitter_callback`
6. Copy your **Client ID** and **Client Secret**
7. In the Streamlit app, navigate to **Account Linking** page
8. Enter your Twitter credentials and click "Link Account"
9. Authorize in the browser that opens

### LinkedIn Setup:

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Create a new app
3. Go to "Products" tab
4. Request access to:
   - "Share on LinkedIn"
   - "Sign In with LinkedIn using OpenID Connect"
5. Go to "Auth" tab
6. Add redirect URI: `http://localhost:5000/linkedin_callback`
7. Copy your **Client ID** and **Client Secret**
8. In the Streamlit app, go to **Account Linking** page
9. Enter your LinkedIn credentials and click "Link Account"
10. Authorize in the browser

## Step 5: Create Content!

1. Go to the main page
2. Select platforms (Twitter, LinkedIn, or both)
3. Enter a topic
4. Click "Generate & Publish"
5. Watch the magic happen! ✨

## Troubleshooting

### "Failed to start OAuth server"
- Port 5000 might be in use
- Kill any process using port 5000: `lsof -ti:5000 | xargs kill -9`

### "Invalid API Key" errors
- Double-check your API keys in `.env`
- Make sure there are no extra spaces or quotes
- Restart the Streamlit app after changing `.env`

### Twitter/LinkedIn not posting
- Verify your accounts are linked in the Account Linking page
- Check that OAuth callback server is running (port 5000)
- Review app permissions in developer portals

### Missing dependencies
```bash
pip install -r requirements.txt --upgrade
```

## Architecture

The system uses multiple specialized AI agents:
- **SEO Researcher** - Finds trending keywords and hashtags
- **Content Writer** - Creates platform-specific content
- **Image Generator** - Creates visuals for posts
- **Publisher Agents** - Handle platform-specific posting
- **Orchestrator** - Coordinates the entire pipeline

## Support

Having issues? Check out:
- [SECURITY.md](SECURITY.md) - Security best practices
- [GitHub Issues](https://github.com/your-repo/issues) - Report bugs or request features

## What's Next?

- Experiment with different topics
- Try different platform combinations
- Customize agent prompts in `agents/` directory
- Build your own specialized agents!

---

**Happy content creating! 🚀**
