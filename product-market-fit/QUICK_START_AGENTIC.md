# Quick Start Guide - Agentic System

## Prerequisites

You need API keys for:
1. **Anthropic** (Claude) - https://console.anthropic.com/
2. **OpenAI** (GPT-4) - https://platform.openai.com/
3. **Tavily** (Web Search) - https://tavily.com/ ← **NEW!**

## Setup Steps

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install the new dependency: `tavily-python==0.3.3`

### 2. Get Tavily API Key

1. Visit https://tavily.com/
2. Sign up (free - 1,000 searches/month)
3. Copy your API key (starts with `tvly-`)

### 3. Configure Environment

Edit `backend/.env`:

```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
TAVILY_API_KEY=tvly-your-key-here

# Database
DATABASE_URL=sqlite:///./product_market_fit.db

# API Settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### 4. Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 5. Start Frontend

In a new terminal:

```bash
cd frontend
streamlit run app.py
```

Browser will open at: http://localhost:8501

## Test the Agentic System

### Test 1: Simple Web Search

```bash
cd backend
python -c "
from app.agents.tools.tavily_search import TavilySearch
t = TavilySearch()
result = t.search('AI fitness app market size 2024')
print('✅ Tavily working!')
print(f'Found {len(result.get(\"results\", []))} results')
"
```

Expected output:
```
✅ Tavily working!
Found 5 results
```

### Test 2: End-to-End Agentic Flow

1. **Open the UI** at http://localhost:8501

2. **Submit a Product Idea:**
   - Name: "AI Meal Planning App"
   - Description: "AI-powered personalized meal plans based on dietary preferences and health goals"
   - Target Market: "Health-conscious millennials aged 25-35"
   - Click "Submit Idea"

3. **Start Agentic Research:**
   - Click "🔬 Start AI Research"
   - Watch the backend logs for agentic behavior:

   ```
   [ResearchAgent] 🔄 Iteration 1/3
   [ResearchAgent] 📋 Planned 4 search queries
   [ResearchAgent] 🌐 Searching: AI meal planning app market size 2024
   [ResearchAgent] 🌐 Searching: meal planning app competitors
   [ResearchAgent] 🌐 Searching: diet app user pain points
   [ResearchAgent] 🌐 Searching: nutrition app market trends
   [ResearchAgent] 📊 Confidence: 0.65 | Valid: False | Suggestions: 3
   [ResearchAgent] 🔧 Retrying with 3 refinements
   [ResearchAgent] 🔄 Iteration 2/3
   [ResearchAgent] ✅ Acceptable quality reached: 0.85
   ```

4. **Check Research Results:**
   - Expand "📊 Research Findings"
   - Verify real market data (not hallucinations)
   - See actual search queries used
   - Expand "🧠 Research Reasoning Trace" to see iterations

5. **Check ICP Quality:**
   - ICP is automatically created after research
   - Expand "👤 Ideal Customer Profile"
   - Notice specific details (not vague ranges)
   - Expand "🧠 AI Reasoning Trace" to see quality improvements

6. **View Agentic Reasoning:**
   - Each iteration shows:
     - ✅ or 🔄 status icon
     - Progress bar (quality score)
     - Specific refinement suggestions
     - Final confidence score

## Expected Agentic Behavior

### Research Agent

**Iteration 1:**
```
Quality: 65%
Issues:
  • Find specific market size data with numbers
  • Identify at least 3 key competitors
  • Research more customer pain points

Status: 🔄 REFINING
```

**Iteration 2:**
```
Quality: 85%
Issues: None

Status: ✅ PASSED
```

### ICP Agent

**Iteration 1:**
```
Quality: 60%
Issues:
  • Specify concrete age range (e.g., 28-42)
  • Provide specific income range with data
  • Goals are too vague - make them measurable

Status: 🔄 REFINING
```

**Iteration 2:**
```
Quality: 80%
Issues: None

Status: ✅ PASSED
```

## Verification Checklist

- [ ] Tavily API key working (Test 1 passes)
- [ ] Backend starts without errors
- [ ] Frontend connects to backend
- [ ] Research shows real web search queries
- [ ] Reasoning traces visible in UI
- [ ] Multiple iterations visible in logs
- [ ] Quality scores displayed
- [ ] Refinement suggestions shown
- [ ] Final confidence >= 70%

## Troubleshooting

### "Tavily API key not found"
- Check `backend/.env` has `TAVILY_API_KEY=tvly-...`
- Restart backend after adding key

### "Module 'tavily' not found"
```bash
cd backend
pip install tavily-python==0.3.3
```

### Research showing 0% quality
- Tavily API key might be invalid
- Check backend logs for detailed error
- Verify you have search credits remaining (free tier: 1000/month)

### No reasoning traces in UI
- Clear browser cache
- Refresh page
- Verify research/ICP have `_reasoning_trace` field in database

### Quality gate always failing
- Check `MIN_ICP_CONFIDENCE` in `backend/app/config.py`
- Default is 0.7 (70%)
- Agent will retry up to `MAX_RESEARCH_ITERATIONS` times (default: 3)

## Understanding the Logs

### Good Agentic Flow:
```
[Workflow] 🔍 Executing agentic research for: AI Meal Planning App
[ResearchAgent] 🔄 Iteration 1/3
[ResearchAgent] 📋 Planned 4 search queries
[ResearchAgent] 🌐 Searching: ...
[ResearchAgent] 📊 Confidence: 0.85 | Valid: True
[ResearchAgent] ✅ Acceptable quality reached: 0.85
[Workflow] Research completed in 1 iterations
[Workflow] Final confidence: 0.85

[Workflow] 🎯 Creating ICP with quality validation
[ICPAgent] 🔄 Iteration 1/3
[ICPAgent] 📊 Confidence: 0.75 | Valid: True
[ICPAgent] ✅ Acceptable quality reached: 0.75
[Workflow] ICP completed in 1 iterations
[Workflow] ✅ ICP quality gate passed: 0.75 >= 0.70
```

### Agentic Retry Flow:
```
[ResearchAgent] 🔄 Iteration 1/3
[ResearchAgent] 📊 Confidence: 0.60 | Valid: False | Suggestions: 3
[ResearchAgent] 🔧 Retrying with 3 refinements
[ResearchAgent] 🔄 Iteration 2/3
[ResearchAgent] 📊 Confidence: 0.85 | Valid: True
[ResearchAgent] ✅ Acceptable quality reached: 0.85
```

## Cost Tracking

### Tavily Usage
- Check usage at: https://tavily.com/dashboard
- Each research uses 3-5 searches
- Free tier: 1000 searches = ~200-300 research runs

### LLM Usage
The agentic system uses 2-3x more LLM calls but produces 10x better quality:

**Before (Non-Agentic):**
- Research: 1 Claude call
- ICP: 1 Claude call
- Total: 2 calls

**After (Agentic):**
- Research: 1-3 Claude calls (query planning + synthesis)
- ICP: 1-3 Claude calls (with validation)
- Persona validation: 1-2 calls
- Total: 3-8 calls

Trade-off: Higher cost for significantly better quality

## Next Steps

Once the system is running:

1. **Generate Personas:**
   - Click "🎭 Generate Personas"
   - Check diversity (< 60% similarity)
   - View detailed background stories

2. **Chat with Personas:**
   - Test persona consistency
   - Try making them go out of character
   - Watch self-correction kick in

3. **Monitor Quality:**
   - All outputs should have >= 70% confidence
   - Reasoning traces show improvement path
   - Quality gates enforce standards

4. **Experiment:**
   - Try different product ideas
   - Compare agentic vs. non-agentic quality
   - Adjust thresholds in config.py

## Support

If you encounter issues:

1. Check backend logs for detailed errors
2. Verify all API keys are valid
3. Ensure dependencies installed correctly
4. Review `AGENTIC_ENHANCEMENTS.md` for architecture details

## Success!

If you see:
- ✅ Real web search results
- ✅ Multiple iterations in logs
- ✅ Reasoning traces in UI
- ✅ Quality scores >= 70%
- ✅ Specific, detailed outputs

**Your agentic system is working perfectly! 🎉**
