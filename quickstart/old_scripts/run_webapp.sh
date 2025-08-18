#!/bin/bash

# TraiGent CLI Command Generator Web App Launcher

echo "🎯 Starting TraiGent CLI Command Generator..."
echo "==========================================="

# Check if streamlit is installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing Streamlit..."
    pip install streamlit
fi

# Activate virtual environment if it exists
if [ -d "cli_venv" ]; then
    echo "✅ Activating virtual environment..."
    source cli_venv/bin/activate
fi

# Launch the web app
echo ""
echo "🚀 Launching web app..."
echo "📍 Open your browser at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run cli_command_generator.py