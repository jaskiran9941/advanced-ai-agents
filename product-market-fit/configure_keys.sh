#!/bin/bash

echo "🔑 API Key Configuration"
echo "======================="
echo ""

# Prompt for Anthropic API key
read -p "Enter your Anthropic API key (starts with sk-ant-): " ANTHROPIC_KEY

# Prompt for OpenAI API key
read -p "Enter your OpenAI API key (starts with sk-): " OPENAI_KEY

# Write to .env file
cat > backend/.env << ENVFILE
# API Keys
ANTHROPIC_API_KEY=$ANTHROPIC_KEY
OPENAI_API_KEY=$OPENAI_KEY

# Database
DATABASE_URL=sqlite:///./product_market_fit.db

# API Settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
ENVFILE

echo ""
echo "✅ API keys configured successfully!"
echo ""
echo "Next steps:"
echo "1. Restart the backend server"
echo "2. Refresh your browser at http://localhost:8501"
echo ""
echo "To restart backend:"
echo "  cd backend"
echo "  kill the current process (Ctrl+C)"
echo "  python3 -m uvicorn app.main:app --reload"
