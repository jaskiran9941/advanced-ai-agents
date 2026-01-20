#!/bin/bash

echo "🚀 Product Market Fit Platform"
echo "================================"
echo ""
echo "Starting backend and frontend..."
echo ""
echo "📝 Make sure you've added your API keys to backend/.env"
echo ""

# Start backend in background
echo "Starting backend on http://localhost:8000..."
cd backend && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend on http://localhost:8501..."
cd ../frontend && streamlit run app.py

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
