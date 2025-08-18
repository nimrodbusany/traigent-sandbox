#!/bin/bash
# Quick runner script for TraiGent CLI Benchmark Tool

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if virtual environment exists
if [[ ! -d "$SCRIPT_DIR/cli_venv" ]]; then
    echo "⚠️  Virtual environment not found. Running setup first..."
    bash "$SCRIPT_DIR/setup_cli.sh"
fi

# Activate virtual environment and run CLI
source "$SCRIPT_DIR/cli_venv/bin/activate"
python "$SCRIPT_DIR/traigent_benchmark_cli.py" "$@"