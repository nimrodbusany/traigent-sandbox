#!/bin/bash
# Run basic test configuration with inline responses

echo "🎯 Running Basic Test Configuration (Mock Mode)"
echo "============================================="
echo ""

# Activate virtual environment
source cli_venv/bin/activate

# Run via safe CLI runner to avoid input desyncs
# 2 -> Basic Test, then Enter to continue, then 6 -> Exit
echo -e "2\n\n6\n" | python safe_cli_runner.py

echo ""
echo "✅ Basic test configuration complete!"