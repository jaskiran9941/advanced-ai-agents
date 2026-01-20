# Quick Start Guide

## Setup (One Time)

1. **Add your API keys**
   ```bash
   cd backend
   nano .env  # or use any text editor
   ```

   Replace the placeholder values:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

2. **Install dependencies**
   ```bash
   ./setup.sh
   ```

## Running the App

**Option 1: Use the start script (Recommended)**
```bash
./start.sh
```

**Option 2: Manual start (two terminals)**

Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload
```

Terminal 2 - Frontend:
```bash
cd frontend
source venv/bin/activate
streamlit run app.py
```

## Access the App

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Test the Workflow

1. Go to http://localhost:8501
2. Click "1_Input_Idea" in sidebar
3. Enter:
   - Name: "AI Fitness App"
   - Description: "Personalized workout plans powered by AI"
   - Target: "Busy professionals aged 25-40"
4. Click "Submit Idea"
5. Go to "2_Research_ICP"
6. Click "Start AI Research" (wait ~60 seconds)
7. Review research findings and ICP
8. Go to "3_Synthetic_Personas"
9. Click "Generate Personas" (wait ~60 seconds)
10. Chat with the generated personas!

## Troubleshooting

**Backend won't start?**
- Check API keys in `backend/.env`
- Make sure port 8000 is available

**Frontend can't connect?**
- Ensure backend is running first
- Check backend is on http://localhost:8000

**Slow persona generation?**
- Normal! LLM calls take time (30-60 sec)
- Multiple agents are working in sequence

**Want to reset?**
- Delete `product_market_fit.db`
- Restart the backend
