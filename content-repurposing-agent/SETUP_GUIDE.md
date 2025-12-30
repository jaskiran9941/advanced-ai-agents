# Setup Guide - Content Repurposing Agent System

## 🎯 What You've Built

A **multi-agent AI system** that:
1. Takes a topic as input
2. Researches SEO keywords and trends
3. Generates platform-specific content (LinkedIn, Twitter, Instagram, Substack)
4. Creates images for visual platforms
5. Posts to all platforms automatically

**With complete transparency** about which agents provide real value vs educational separation!

---

## 📋 Prerequisites

- Python 3.9 or higher
- API keys for:
  - Anthropic (Claude)
  - Google (Gemini)
  - OpenAI (for DALL-E)
  - SerpAPI (for SEO research)
  - Social media platforms (Twitter, LinkedIn, Instagram, Substack)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd content-repurposing-agent
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Set Up API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Required API keys for basic functionality:**
- `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com/
- `GOOGLE_API_KEY` - Get from https://makersuite.google.com/app/apikey
- `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys

**Optional API keys (for full functionality):**
- `SERPAPI_API_KEY` - For real SEO data (falls back to mock data)
- Social media platform keys - For actual posting (system uses mock posting without them)

### 3. Run the Example

```bash
python example.py
```

This will demonstrate the multi-agent system in action (dry run mode).

### 4. Launch the Streamlit UI

```bash
streamlit run ui/app.py
```

This opens an interactive web interface at `http://localhost:8501`

---

## 🏗️ Architecture Overview

### Agent Breakdown

```
ContentOrchestrator (Main Coordinator)
├── SEO Research Agent ✅ REAL
│   └── Calls SerpAPI for trending keywords
├── Image Generator Agent ✅ REAL
│   └── Calls DALL-E/Stable Diffusion APIs
├── Content Writer Agent ⚠️ EDUCATIONAL
│   └── Could be one LLM call (separated for learning)
├── Editor Agent 🔄 SEMI-REAL
│   └── Iteration/debate adds some value
└── Platform Agents ✅ REAL (4 agents)
    ├── LinkedIn Agent → LinkedIn API
    ├── Twitter Agent → Twitter API
    ├── Instagram Agent → Instagram API
    └── Substack Agent → Substack API
```

### Why This Architecture?

**✅ REAL Multi-Agent Value:**
1. **API Orchestration** - Each agent calls different external APIs
2. **Parallel Execution** - SEO + image generation run simultaneously
3. **Platform Specialization** - Each social platform has unique requirements
4. **Error Handling** - Orchestrator manages failures and retries

**⚠️ Educational Separation:**
- Content Writer could be one LLM call, separated to show agent patterns

**🔄 Semi-Real Value:**
- Editor agent provides iterative refinement through debate

---

## 📚 Learning Objectives

This project teaches you:

### 1. **Agno AI Framework**
- Creating agents with different LLM providers
- Tool calling and API integration
- Agent orchestration and coordination

### 2. **Multi-Agent Patterns**
- When to separate agents vs use single LLM
- Parallel vs sequential execution
- State management across agents
- Error handling in distributed systems

### 3. **API Integration**
- Working with multiple LLM APIs (Claude, Gemini, GPT)
- Image generation APIs (DALL-E, Stable Diffusion)
- SEO research APIs (SerpAPI)
- Social media APIs (Twitter, LinkedIn, Instagram, Substack)

### 4. **Production Practices**
- Configuration management
- Logging and monitoring
- Error handling and retries
- Testing without API keys (mock mode)

---

## 🎮 Usage Examples

### Example 1: Generate Content Only

```python
from agents.orchestrator import ContentOrchestrator

orchestrator = ContentOrchestrator()

results = orchestrator.generate_content_only(
    topic="AI in Healthcare",
    platforms=["linkedin", "twitter"],
    include_seo=True
)

print(results["content"]["linkedin"])
```

### Example 2: Full Pipeline (Dry Run)

```python
results = orchestrator.run_full_pipeline(
    topic="AI in Healthcare",
    platforms=["linkedin", "twitter", "instagram"],
    enable_editing=True,
    enable_images=True,
    dry_run=True  # Don't actually post
)

print(f"Completed in {results['duration_seconds']}s")
```

### Example 3: Using Individual Agents

```python
from agents.seo_agent import SEOResearchAgent
from agents.writer_agent import ContentWriterAgent

# SEO research
seo_agent = SEOResearchAgent()
keywords = seo_agent.research_topic("AI in Healthcare")

# Content writing
writer = ContentWriterAgent()
linkedin_post = writer.write_linkedin_post(
    topic="AI in Healthcare",
    keywords=keywords["primary_keywords"]
)

print(linkedin_post)
```

---

## 🔧 Configuration

### LLM Provider Selection

Each agent can use different LLM providers:

```python
# In agents/orchestrator.py, modify agent initialization:

self.seo_agent = SEOResearchAgent(llm_provider="gemini")  # Fast, cheap
self.writer_agent = ContentWriterAgent(llm_provider="claude")  # Quality writing
self.twitter_agent = TwitterAgent(llm_provider="gemini")  # Speed
```

### Image Provider Selection

```python
self.image_agent = ImageGeneratorAgent(
    llm_provider="claude",
    image_provider="openai"  # or "replicate" for Stable Diffusion
)
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: API key errors

**Solution:**
- Check that `.env` file exists in project root
- Verify API keys are correct (no extra spaces)
- For testing, the system will fall back to mock mode without keys

### Issue: Agno installation fails

**Solution:**
```bash
# Try installing with --upgrade flag
pip install --upgrade agno-ai

# Or install from source if needed
pip install git+https://github.com/agno-ai/agno.git
```

---

## 📈 Next Steps

### Extend the System

1. **Add More Platforms**
   - TikTok, Facebook, Medium, etc.
   - Copy platform agent template from existing agents

2. **Add More Content Types**
   - Video scripts
   - Podcast outlines
   - Email newsletters

3. **Improve Quality**
   - Add fact-checking agent
   - Implement A/B testing
   - Add sentiment analysis

4. **Production Features**
   - Scheduling (post at optimal times)
   - Analytics tracking
   - User authentication
   - Database for content history

### Learn More About Multi-Agent Systems

**When to use multi-agent:**
- ✅ Different agents need different tools/APIs
- ✅ Tasks can run in parallel for speed
- ✅ Complex workflows with error handling
- ✅ Different specialized knowledge domains

**When NOT to use multi-agent:**
- ❌ Simple, single-step tasks
- ❌ All work can be done by one LLM call
- ❌ No parallelization or tool use needed

---

## 🎓 What You Learned

By building this system, you now understand:

1. **Real Multi-Agent Value** - API orchestration, parallelization, platform specialization
2. **Agno Framework** - Agent creation, tool calling, orchestration
3. **Multiple APIs** - LLMs (Claude, Gemini, GPT), image generation, SEO, social media
4. **Production Patterns** - Config, logging, error handling, testing
5. **When to Use Multi-Agent** - Honest assessment of value vs complexity

---

## 📞 Support

- **Agno AI Documentation**: https://github.com/agno-ai/agno
- **Anthropic Claude Docs**: https://docs.anthropic.com/
- **Google Gemini Docs**: https://ai.google.dev/docs
- **OpenAI Docs**: https://platform.openai.com/docs

---

## ✅ Success Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with API keys
- [ ] Example script runs successfully (`python example.py`)
- [ ] Streamlit UI launches (`streamlit run ui/app.py`)
- [ ] Generated content for at least one platform
- [ ] Understood the difference between real vs educational agent separation

**Congratulations! You've built a complete multi-agent AI system!** 🎉
