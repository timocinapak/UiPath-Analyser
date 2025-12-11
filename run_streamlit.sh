#!/bin/bash

# UiPath Workflow Analyzer - Streamlit App Launcher
# This script sets up and runs the Streamlit web application

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║   🤖 UiPath Workflow Analyzer - Streamlit App         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python installation
echo "🔍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✅ pip upgraded${NC}"
echo ""

# Install requirements
echo "📥 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt not found${NC}"
    echo "Installing essential packages..."
    pip install streamlit pandas reportlab
fi
echo ""

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ app.py not found${NC}"
    exit 1
fi

# Display app info
echo "════════════════════════════════════════════════════════"
echo "📊 Application Information:"
echo "════════════════════════════════════════════════════════"
echo "App:         UiPath Workflow Analyzer"
echo "Type:        Streamlit Web Application"
echo "File:        app.py"
echo "Port:        8501"
echo "URL:         http://localhost:8501"
echo "════════════════════════════════════════════════════════"
echo ""

# Display features
echo "✨ Features:"
echo "   🔍 Workflow Analysis"
echo "   📊 Health Score Calculation"
echo "   ⚠️  Issue Detection"
echo "   💡 Recommendations"
echo "   📥 Multiple Export Formats (Markdown, PDF, JSON)"
echo ""

# Ask for custom port
read -p "Press Enter to start (or type custom port [default: 8501]): " PORT
if [ -z "$PORT" ]; then
    PORT=8501
fi

echo ""
echo "🚀 Starting Streamlit application..."
echo "📱 Access the app at: ${GREEN}http://localhost:$PORT${NC}"
echo ""
echo "💡 Tips:"
echo "   • Press 'q' to quit"
echo "   • Reload the browser to restart"
echo "   • Check the terminal for logs"
echo ""

# Run Streamlit
streamlit run app.py --server.port $PORT
