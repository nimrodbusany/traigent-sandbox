#!/bin/bash
# Run advanced test configuration with inline responses

echo "🔬 Running Advanced Test Configuration (Mock Mode)"
echo "================================================"
echo ""

# Activate virtual environment
source cli_venv/bin/activate

# Run with inline responses using printf for better control
printf '%s\n' \
  "2" \
  "advanced_test" \
  "15" \
  "1" \
  "4" "4" "4" "3" \
  "y" \
  "y" "n" "2" \
  "y" "n" "3" \
  "n" \
  "n" \
  "y" \
  "y" "n" "2" \
  "y" "n" "2" \
  "y" \
  "y" "n" "2" \
  "y" "n" "2" \
  "n" \
  "n" \
  "n" \
  "1" \
  "y" \
  "n" \
  "y" \
  "y" \
  "y" | python traigent_benchmark_cli.py

echo ""
echo "✅ Advanced test configuration complete!"