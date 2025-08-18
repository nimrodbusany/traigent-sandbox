#!/bin/bash
# Run quick test configuration with inline responses

echo "🚀 Running Quick Test Configuration (Mock Mode)"
echo "=============================================="
echo ""

# Activate virtual environment
source cli_venv/bin/activate

# Run with inline responses using echo and pipe
echo -e "2\nquick_test\n5\n1\n2\n2\n1\n0\ny\ny\nn\n2\ny\nn\n2\nn\nn\nn\n1\ny\nn\ny\ny\ny" | python traigent_benchmark_cli.py

echo ""
echo "✅ Quick test configuration complete!"