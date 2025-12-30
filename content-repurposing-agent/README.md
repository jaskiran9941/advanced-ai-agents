# 🤖 AI Content Repurposing Agent System

> **Multi-Agent AI System** that transforms a single topic into platform-specific content for Twitter and LinkedIn, then publishes automatically.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What This Does

Enter a topic like "Benefits of morning meditation" and this AI system will:
1. 🔍 Research trending keywords and hashtags (SEO)
2. ✍️ Write platform-specific content (Twitter thread, LinkedIn post)
3. 🎨 Generate eye-catching images
4. 🚀 Publish to your connected social media accounts

All automated. All optimized. All with specialized AI agents working together.

## 🏗️ Multi-Agent Architecture

This project demonstrates a **real multi-agent system** with different AI models working as specialized agents:

### ✅ REAL Multi-Agent Value

These agents provide **genuine separation of concerns** and couldn't easily be replaced by a single LLM call:

| Agent | Purpose | Why It's Real |
|-------|---------|---------------|
| **SEO Researcher** | Analyzes search trends, keyword difficulty, related queries | Uses external APIs (SerpAPI) + LLM analysis - requires specialized research tools |
| **Image Generator** | Creates platform-specific visuals | Uses Replicate/DALL-E - fundamentally different capability than text generation |
| **Platform Publishers** | Handles OAuth, API quirks, rate limits per platform | Each platform has unique APIs, auth flows, and posting requirements |
| **Orchestrator** | Coordinates pipeline, manages state, handles errors | Orchestration logic, parallel execution, error recovery |

### ⚠️ SEMI-REAL Value

These agents add value through **iteration and specialization**:

| Agent | Purpose | Value Add |
|-------|---------|-----------|
| **Editor Agent** | Reviews and improves content | Provides "second pair of eyes" - catches issues through iteration |

### 📚 EDUCATIONAL (Honest Assessment)

These agents demonstrate the **pattern** but could be collapsed into one LLM call:

| Agent | Purpose | Why It's Educational |
|-------|---------|---------------------|
| **Content Writer** | Writes platform-specific content | Different prompts for each platform, but no real isolation needed - single LLM could generate all content formats in one call |

> **Note on Transparency:** This project is built to showcase both what makes a "real" multi-agent system vs. what's just prompt engineering. The value is in the **orchestration**, **external integrations**, and **specialized capabilities**, not just breaking up LLM calls.

## ✨ Features

- 🎯 **One-Click OAuth** - Secure account linking for Twitter & LinkedIn
- 🤖 **Specialized AI Agents** - Each agent has a specific role and expertise
- 📊 **SEO-Optimized** - Research-backed keywords and hashtags
- 🎨 **Auto-Generated Images** - Platform-optimized visuals
- 🔄 **Parallel Processing** - Agents work concurrently for speed
- 📱 **Platform-Specific** - Content tailored to each platform's style
- 🎛️ **Full Control** - Preview before publishing, dry-run mode
- 🔐 **Secure** - OAuth 2.0, encrypted token storage, no credentials in code

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- API keys from:
  - [Anthropic](https://console.anthropic.com/) (Claude) or [OpenAI](https://platform.openai.com/) (GPT) or [Google](https://makersuite.google.com/app/apikey) (Gemini)
  - [Replicate](https://replicate.com/account/api-tokens) (Image generation)
  - [SerpAPI](https://serpapi.com/manage-api-key) (SEO research)
- Developer accounts:
  - [Twitter Developer Portal](https://developer.twitter.com/)
  - [LinkedIn Developers](https://www.linkedin.com/developers/)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jaskiran9941/content-repurposing-agent.git
   cd content-repurposing-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

   Example `.env`:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
   OPENAI_API_KEY=sk-proj-your-key-here
   GOOGLE_API_KEY=AIzaSy-your-key-here
   REPLICATE_API_TOKEN=r8_your-token-here
   SERPAPI_API_KEY=your-serpapi-key-here
   ```

4. **Run the application**
   ```bash
   streamlit run ui/app.py
   ```

5. **Open in browser**
   - Navigate to `http://localhost:8501`
   - Go to "Account Linking" page
   - Link your Twitter and LinkedIn accounts
   - Start creating content!

## 📖 Detailed Setup Guide

### Setting Up Twitter OAuth

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app (or use existing)
3. Navigate to app settings → **User authentication settings**
4. Click "Set up" and configure:
   - **App permissions**: Read and Write
   - **Type of App**: Web App
   - **Callback URI**: `http://localhost:5000/twitter_callback`
   - **Website URL**: `http://localhost:8501`
5. Save and copy your **Client ID** and **Client Secret**
6. In the Streamlit app, go to **Account Linking** page
7. Enter credentials and click **"Link Twitter Account"**
8. Authorize in the browser window that opens

### Setting Up LinkedIn OAuth

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Create a new app
3. Go to **Products** tab and request access to:
   - "Share on LinkedIn"
   - "Sign In with LinkedIn using OpenID Connect"
4. Go to **Auth** tab
5. Add **Redirect URL**: `http://localhost:5000/linkedin_callback`
6. Copy your **Client ID** and **Client Secret**
7. In the Streamlit app, go to **Account Linking** page
8. Enter credentials and click **"Link LinkedIn Account"**
9. Authorize in the browser

## 🎮 Usage

### Generate Content Only
1. Select platforms (Twitter, LinkedIn, or both)
2. Enter your topic
3. Click **"Generate Content Only"**
4. Review content in the Preview tab

### Generate & Publish
1. Select platforms
2. Enter your topic
3. Uncheck **"Dry Run"** if you want to actually post
4. Click **"Generate & Publish"**
5. View results in the Results tab

### Example Topics
- "Benefits of morning meditation"
- "Future of AI in healthcare"
- "Tips for remote work productivity"
- "How to build a personal brand"

## 🏗️ Project Structure

```
content-repurposing-agent/
├── agents/                    # AI Agent implementations
│   ├── base_agent.py         # Base agent class
│   ├── seo_researcher.py     # SEO research agent (REAL)
│   ├── content_writer.py     # Content writing agent (EDUCATIONAL)
│   ├── image_generator.py    # Image generation agent (REAL)
│   ├── editor.py             # Content editing agent (SEMI-REAL)
│   ├── publishers/           # Platform-specific publishers (REAL)
│   │   ├── twitter.py
│   │   └── linkedin.py
│   └── orchestrator.py       # Main orchestration (REAL)
├── tools/                     # Tool functions for agents
│   ├── seo_tools.py          # SEO API integrations
│   ├── social_tools.py       # Social media APIs
│   └── image_tools.py        # Image generation
├── auth/                      # OAuth management
│   └── oauth_manager.py      # OAuth 2.0 flows
├── utils/                     # Utility functions
│   ├── oauth_helpers.py      # OAuth UI helpers
│   └── logger.py             # Logging
├── ui/                        # Streamlit interface
│   ├── app.py               # Main app
│   └── pages/
│       └── 1_Account_Linking.py  # OAuth linking UI
├── config/                    # Configuration
│   └── settings.py           # Settings loader
├── data/                      # Generated data (gitignored)
│   ├── images/               # Generated images
│   └── user_tokens.json      # OAuth tokens (gitignored)
├── .env                       # API keys (gitignored)
├── .env.example              # Example environment file
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── SETUP.md                  # Detailed setup guide
└── SECURITY.md               # Security best practices
```

## 🤔 Architecture Deep Dive

### Why This is a REAL Multi-Agent System

**1. External API Integration (SEO Agent)**
- Can't be replaced by a single LLM call
- Requires SerpAPI for real-time search data
- Combines API data with LLM analysis

**2. Different Modalities (Image Generator)**
- Fundamentally different capability (text → image)
- Uses specialized models (Stable Diffusion, DALL-E)
- Platform-specific sizing and optimization

**3. Specialized Platform Logic (Publisher Agents)**
- Each platform has unique OAuth flows
- Different API endpoints and rate limits
- Platform-specific content formatting
- Error handling and retry logic

**4. Orchestration Complexity**
- Parallel execution of independent agents
- State management across pipeline
- Error recovery and rollback
- Conditional execution based on user settings

### What Could Be Simplified?

The **Content Writer** agent is honestly educational. While it's implemented as separate agents for each platform, a single LLM call could generate all content formats. The real value is in the:
- SEO research informing the content
- Image generation complementing the text
- Platform APIs handling the publishing
- Orchestrator coordinating everything

This transparency helps you understand what makes a **real** multi-agent system vs. marketing hype.

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM Providers** | Anthropic Claude, OpenAI GPT, Google Gemini | Content generation and analysis |
| **Agent Framework** | Agno AI | Agent orchestration and management |
| **Image Generation** | Replicate (Stable Diffusion), DALL-E | Visual content creation |
| **SEO Research** | SerpAPI | Search trends and keyword data |
| **UI Framework** | Streamlit | Interactive web interface |
| **OAuth 2.0** | Custom implementation | Secure social media authentication |
| **Social APIs** | Twitter API v2, LinkedIn API | Content publishing |

## 🔐 Security

- ✅ OAuth 2.0 with PKCE for Twitter and LinkedIn
- ✅ Encrypted token storage
- ✅ All credentials in `.env` (gitignored)
- ✅ No hardcoded secrets
- ✅ Local callback server for OAuth
- ✅ Automatic token refresh

See [SECURITY.md](SECURITY.md) for detailed security guidelines.

## 🐛 Troubleshooting

### OAuth Server Won't Start
```bash
# Kill any process using port 5000
lsof -ti:5000 | xargs kill -9
```

### Twitter/LinkedIn Not Posting
- Verify accounts are linked in Account Linking page
- Check OAuth tokens in `data/user_tokens.json`
- Ensure callback server is running (port 5000)
- Review app permissions in developer portals

### API Key Errors
- Double-check `.env` file has correct keys
- No extra spaces or quotes around keys
- Restart Streamlit after changing `.env`

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## 🗺️ Roadmap

- [ ] Add support for Instagram Stories
- [ ] Implement Substack newsletter publishing
- [ ] Add analytics dashboard
- [ ] Content scheduling
- [ ] A/B testing for content variations
- [ ] Custom agent creation interface
- [ ] More LLM provider options

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Agno AI](https://github.com/agno-agi/agno) for agent orchestration
- Powered by Claude (Anthropic), GPT (OpenAI), and Gemini (Google)
- UI framework: [Streamlit](https://streamlit.io/)

## 📧 Contact

**Your Name** - [@jaskiransin](https://twitter.com/jaskiransin)

Project Link: [https://github.com/jaskiran9941/content-repurposing-agent](https://github.com/YOUR_USERNAME/content-repurposing-agent)

---

**Built with transparency in mind - showcasing what makes a real multi-agent system vs. marketing hype** 🚀
