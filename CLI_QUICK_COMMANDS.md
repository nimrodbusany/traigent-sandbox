# TraiGent CLI Quick Command Reference

Essential bash commands for different CLI scenarios.

## 🚀 Quick Setup Commands

### Initial Setup (One-Time)
```bash
# Navigate to quickstart directory
cd /path/to/traigent-sandbox/quickstart

# Create dedicated virtual environment
python3 -m venv cli_venv
source cli_venv/bin/activate

# Install required dependencies
pip install openai pandas pyyaml

# Install TraiGent SDK
cd ../Traigent && pip install -e . && cd ../quickstart

# Mock mode will auto-create .env on first run
```

### Quick Start (After Setup)
```bash
# Navigate to quickstart
cd /path/to/traigent-sandbox/quickstart

# Activate environment and run
source cli_venv/bin/activate
python traigent_benchmark_cli.py
```

### Verify Setup
```bash
# Check files exist
ls traigent_benchmark_cli.py support_classification_dataset.json

# Test Python imports
python -c "import traigent; print('✅ TraiGent ready')"

# Launch CLI
python traigent_benchmark_cli.py
```

## 🎯 Common CLI Input Sequences

### Scenario 1: Basic Mock Test (Minimal Parameters)
```bash
python traigent_benchmark_cli.py
```
**Input sequence (safe - avoids empty parameter issue):**
```
2              # Guided Configuration
basic_test     # Experiment name
10             # Number of examples
1              # Stratified sampling
3              # Easy examples
3              # Medium examples
2              # Hard examples
2              # Expert examples
y              # Include Core LLM
y              # Include model
n              # No custom values
2              # 2 model values (IMPORTANT: Never use 0)
y              # Include temperature
n              # No custom values
2              # 2 temperature values
n              # Skip few-shot
n              # Skip prompt engineering
n              # Skip context/retrieval
1              # Local execution
y              # Mock mode
n              # No early stopping
y              # Proceed with config
y              # Save configuration
y              # Run now
```

**⚠️ Important**: Never enter `0` for "How many values to use" - always use at least 1

### Scenario 2: Advanced Mock Test (Multiple Parameters)
```bash
python traigent_benchmark_cli.py
```
**Input sequence:**
```
2                    # Guided Configuration
advanced_test        # Experiment name
20                   # Number of examples
1                    # Stratified sampling
5 5 5 5             # Difficulty distribution
y                    # Include Core LLM
y y n 2 y y n 3     # Model + temperature config
y                    # Include Few-Shot Learning
y y n 3 y y n 2     # Few-shot k + strategy config
y                    # Include Prompt Engineering
y y n 2 y y n 2     # System role + output format
n y n 2 n           # Skip other prompt params
n                    # Skip context/retrieval
random               # Random optimization
30                   # Max trials
1                    # Local execution
y                    # Mock mode
n                    # No early stopping
y                    # Proceed
y                    # Save
y                    # Run
```

### Scenario 3: Prompt Engineering Focus
```bash
python traigent_benchmark_cli.py
```
**Input sequence:**
```
2                      # Guided Configuration
prompt_test            # Experiment name
15                     # Examples
1                      # Stratified
4 4 4 3               # Distribution
y                      # Core LLM
n y y n 3             # Skip model, include temperature
y                      # Few-shot learning
y y n 3 y y n 2       # Include both few-shot params
y                      # Prompt engineering
y y n 3               # System role (3 values)
y y n 2               # Output format (2 values)
y y n 2               # Response style (2 values)
y y                   # Chain of thought (both values)
n                      # Skip context
1 y n                 # Local, mock, no early stop
y y y                 # Proceed, save, run
```

## 🔧 Environment Management Commands

### Switch Between Mock and Real API
```bash
# Enable mock mode (no costs)
export TRAIGENT_MOCK_MODE=true
export OPENAI_API_KEY=mock-key-for-demos

# Enable real API mode (costs money!)
export TRAIGENT_MOCK_MODE=false
export OPENAI_API_KEY=your-real-key-here

# Check current mode
echo "Mock mode: $TRAIGENT_MOCK_MODE"
```

### Configuration Management
```bash
# List saved configurations
ls benchmark_configs/

# View configuration details
cat benchmark_configs/your_config.yaml

# Copy configuration for modification
cp benchmark_configs/basic_test.yaml benchmark_configs/modified_test.yaml

# Clean up old configurations
rm benchmark_configs/old_config.yaml
```

## 🚨 Emergency Commands

### Stop CLI Safely
```bash
# In CLI interface:
Ctrl+C    # Graceful exit

# If CLI is stuck, force kill:
pkill -f traigent_benchmark_cli.py
```

### Reset Environment
```bash
# Clear mock mode
unset TRAIGENT_MOCK_MODE
unset OPENAI_API_KEY

# Reload environment
source .env

# Restart virtual environment
deactivate && source venv/bin/activate
```

### Debug Import Issues
```bash
# Check Python path
python -c "import sys; print('\\n'.join(sys.path))"

# Reinstall TraiGent
cd ../Traigent
pip uninstall traigent -y
pip install -e ".[all]"
cd ../quickstart
```

## 📊 Quick Data Exploration

### Dataset Statistics
```bash
# Quick dataset overview
python -c "
import json
with open('support_classification_dataset.json') as f:
    data = json.load(f)
    print(f'Examples: {len(data[\"examples\"])}')
    print(f'Categories: {data[\"metadata\"][\"categories\"]}')
    print(f'Difficulties: {data[\"metadata\"][\"difficulty_levels\"]}')
"
```

### Configuration Analysis
```bash
# Count saved configurations
ls benchmark_configs/*.yaml | wc -l

# Find large configurations (many parameters)
grep -l "total.*[0-9][0-9][0-9]" benchmark_configs/*.yaml

# Show recent configurations
ls -lt benchmark_configs/ | head -5
```

## 🎮 Interactive Navigation Tips

### CLI Menu Navigation
```bash
# Always valid during CLI:
Enter     # Accept default (shown in [brackets])
y/yes     # Confirm actions
n/no      # Decline actions
1,2,3...  # Menu selections
Ctrl+C    # Safe exit

# Parameter configuration shortcuts:
n n n n   # Skip all parameters in a category
y y n 2   # Include parameter, use defaults, 2 values
```

### Common Input Patterns
```bash
# Minimal test setup:
10        # Small number of examples
2         # 2 values per parameter
y         # Mock mode
n         # No advanced features

# Comprehensive test setup:
25        # More examples
3         # 3 values per parameter
y         # Include multiple parameter types
random    # Use random optimization
50        # Higher trial limit
```

## 🔍 Troubleshooting One-Liners

### Check Environment
```bash
# Verify all components
python -c "import traigent, openai, anthropic; print('✅ All imports OK')" 2>/dev/null || echo "❌ Import issues"
```

### Test CLI Without Running
```bash
# Test CLI startup
timeout 10s python traigent_benchmark_cli.py <<< "$(echo -e '\\n\\n\\n')" || echo "CLI startup test"
```

### Validate Dataset
```bash
# Check dataset format
python -c "
import json
try:
    with open('support_classification_dataset.json') as f:
        data = json.load(f)
    print(f'✅ Valid dataset: {len(data[\"examples\"])} examples')
except Exception as e:
    print(f'❌ Dataset error: {e}')
"
```

## 📈 Performance Testing Commands

### Benchmark CLI Performance
```bash
# Time CLI startup
time python -c "
from traigent_benchmark_cli import TraiGentBenchmarkCLI
cli = TraiGentBenchmarkCLI()
print('CLI initialized')
"

# Test with larger datasets
python -c "
import json
with open('support_classification_dataset.json') as f:
    data = json.load(f)
print(f'Dataset load time for {len(data[\"examples\"])} examples')
"
```

### Resource Monitoring
```bash
# Monitor resource usage during CLI operation
python traigent_benchmark_cli.py &
CLI_PID=$!
watch -n 1 "ps -p $CLI_PID -o pid,pcpu,pmem,time,cmd"
```

This quick reference provides the essential commands for productive CLI usage across different scenarios and operational needs.