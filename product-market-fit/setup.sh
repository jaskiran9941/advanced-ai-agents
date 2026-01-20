#!/bin/bash

echo "🔧 Setting up Product Market Fit Platform..."
echo ""

# Setup backend
echo "📦 Installing backend dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# Setup frontend  
echo "📦 Installing frontend dependencies..."
cd frontend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your API keys to backend/.env"
echo "2. Run ./start.sh to start the application"
