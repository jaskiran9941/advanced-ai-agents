#!/bin/bash
# Quick start script for the Streamlit UI

echo "🚀 Starting Multi-Agent Content Creator Streamlit UI..."
echo ""
echo "Installing dependencies..."
pip install streamlit pandas -q

echo "✅ Dependencies installed"
echo ""
echo "🎬 Starting Streamlit server..."
echo "Opening http://localhost:8501 in your browser..."
echo ""
streamlit run streamlit_ui.py --logger.level=warning
