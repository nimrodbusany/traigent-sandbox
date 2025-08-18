#!/bin/bash
# Quick setup script for TraiGent CLI Benchmark Tool

set -e

echo "🎯 TraiGent CLI Setup Script"
echo "============================"
echo ""

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRAIGENT_DIR="$(dirname "$SCRIPT_DIR")/Traigent"

# Check if TraiGent directory exists
if [[ ! -d "$TRAIGENT_DIR" ]]; then
    echo "❌ TraiGent directory not found at: $TRAIGENT_DIR"
    echo "Please ensure you're in the traigent-sandbox/quickstart directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [[ ! -d "$SCRIPT_DIR/cli_venv" ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/cli_venv"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source "$SCRIPT_DIR/cli_venv/bin/activate"

# Install TraiGent
echo "📦 Installing TraiGent SDK..."
cd "$TRAIGENT_DIR"
pip install -e ".[all]" -q 2>/dev/null || pip install -e . -q

# Install CLI-specific dependencies
echo "📦 Installing CLI dependencies..."
pip install openai pandas pyyaml -q

# Go back to quickstart directory
cd "$SCRIPT_DIR"

# Create .env file if it doesn't exist
if [[ ! -f ".env" ]]; then
    echo "📝 Creating mock mode .env file..."
    cat > .env << 'EOF'
# TraiGent Mock Mode Configuration (No API Costs)
OPENAI_API_KEY=mock-key-for-demos
ANTHROPIC_API_KEY=mock-key-for-demos
TRAIGENT_EXECUTION_MODE=local
TRAIGENT_MOCK_MODE=true
EOF
    echo "✅ Mock mode configuration created"
else
    echo "✅ Using existing .env file"
fi

# Verify installation
echo ""
echo "🔍 Verifying installation..."
python -c "
import traigent
import openai
import pandas
import yaml
print('✅ All dependencies installed successfully')
print(f'   TraiGent version: {traigent.__version__}')
" 2>/dev/null || echo "⚠️  Some dependencies may be missing"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To run the CLI tool:"
echo "   1. Activate the environment: source cli_venv/bin/activate"
echo "   2. Run the CLI: python traigent_benchmark_cli.py"
echo ""
echo "Or run directly:"
echo "   ./run_cli.sh"
echo ""