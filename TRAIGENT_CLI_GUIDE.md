# TraiGent Benchmark CLI Tool - Complete Setup Guide

A comprehensive step-by-step guide for using the TraiGent Advanced Benchmark CLI Tool with different scenarios and bash commands.

## 🎯 Overview

The TraiGent Benchmark CLI Tool (`quickstart/traigent_benchmark_cli.py`) is an advanced optimization platform that allows you to:
- Configure dynamic parameter spaces for LLM optimization
- Test different prompt engineering strategies
- Run cost-free experiments in mock mode
- Compare multiple execution modes (local, standard, cloud)
- Export comprehensive results and visualizations

## 📋 Prerequisites

### 1. Environment Setup
```bash
# Navigate to project root
cd /path/to/traigent-sandbox

# Verify you have the required files
ls quickstart/
# Should show: traigent_benchmark_cli.py, support_classification_dataset.json, etc.

# Check Python version (3.8+ required)
python --version
```

### 2. Install Dependencies
```bash
# Navigate to main SDK
cd Traigent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install TraiGent with all features
pip install -e ".[all]"

# Verify installation
python -c "import traigent; print(f'TraiGent {traigent.__version__} installed')"
```

### 3. Environment Configuration
```bash
# Navigate back to quickstart
cd ../quickstart

# Create .env file for mock mode (no API costs)
cat > .env << 'EOF'
# Mock mode - no real API calls
OPENAI_API_KEY=mock-key-for-demos
ANTHROPIC_API_KEY=mock-key-for-demos
TRAIGENT_EXECUTION_MODE=local
TRAIGENT_MOCK_MODE=true
EOF

# OR for real API usage
cat > .env << 'EOF'
# Real API mode
OPENAI_API_KEY=your-actual-openai-key
ANTHROPIC_API_KEY=your-actual-anthropic-key
TRAIGENT_EXECUTION_MODE=local
TRAIGENT_MOCK_MODE=false
EOF
```

## 🚀 Getting Started - Mock Mode Scenarios

### Scenario 1: Basic Mock Mode Setup (Recommended First Run)

```bash
# Ensure you're in quickstart directory
cd quickstart

# Verify dataset exists
ls -la support_classification_dataset.json

# Launch the CLI tool
python traigent_benchmark_cli.py
```

**Expected Output:**
```
🎯 TraiGent Advanced Benchmark CLI Tool
========================================
Configure and run comprehensive LLM optimization experiments
with full control over parameters, datasets, and execution modes.

📋 Configuration Mode:
1. Quick Start (Presets)
2. Guided Configuration
3. Advanced Configuration
4. Load Configuration File

Choice (1-4):
```

**Step-by-step walkthrough:**

1. **Choose Guided Configuration:**
   ```
   Choice (1-4): 2
   ```

2. **Enter Experiment Name:**
   ```
   Experiment name [benchmark_experiment]: mock_test_basic
   ```

3. **Configure Dataset:**
   ```
   📊 Dataset Configuration
   ==================================================
   Total examples available: 100
   Number of examples to use (1-100) [25]: 10
   
   Sampling strategy:
   1. Stratified (balanced across difficulty levels)
   2. Random sampling
   3. Sequential (first N examples)
   Strategy (1-3) [1]: 1
   
   Difficulty distribution:
   Easy examples [2]: 3
   Medium examples [2]: 3
   Hard examples [2]: 2
   Expert examples [4]: 2
   ```

4. **Configure Parameters (Choose Minimal Set):**
   ```
   🔧 Parameter Space Configuration
   ==================================================
   
   Core LLM:
   Include Core LLM parameters? (y/n) [y]: y
   
     model: LLM model to use
     Available values: ['gpt-3.5-turbo', 'gpt-4o-mini', 'gpt-4o', 'gpt-4']
     Include model? (y/n) [y]: y
     Use custom values? (y/n) [n]: n
     How many values to use (1-4) [3]: 2
   
     temperature: Sampling temperature (0.0 = deterministic, 1.0 = random)
     Available values: [0.0, 0.3, 0.5, 0.7, 1.0]
     Include temperature? (y/n) [y]: y
     Use custom values? (y/n) [n]: n
     How many values to use (1-5) [3]: 2
   
   Few-Shot Learning:
   Include Few-Shot Learning parameters? (y/n) [y]: n
   
   Prompt Engineering:
   Include Prompt Engineering parameters? (y/n) [y]: n
   
   Context/Retrieval:
   Include Context/Retrieval parameters? (y/n) [y]: n
   ```

5. **Configure Execution (Mock Mode):**
   ```
   ⚙️  Execution Configuration
   ==================================================
   Execution modes:
   1. Local (no backend required)
   2. Standard (hybrid with backend)
   3. Cloud (full cloud execution)
   Mode (1-3) [1]: 1
   
   Use mock mode (no API costs)? (y/n) [n]: y
   Enable early stopping? (y/n) [n]: n
   ```

6. **Review and Confirm:**
   ```
   📋 Configuration Summary
   ==================================================
   Experiment: mock_test_basic
   Examples: 10
   Parameters: 2
   Execution mode: local
   Mock mode: True
   
   💰 Cost Estimation
   ==================================================
   Total API calls: 40
   Estimated cost: $0.00
   Estimated time: 0.3 minutes
   
   Proceed with this configuration? (y/n): y
   ```

7. **Save and Run:**
   ```
   Save this configuration? (y/n) [y]: y
   💾 Configuration saved to: benchmark_configs/mock_test_basic.yaml
   
   Run benchmark now? (y/n) [y]: y
   ```

### Scenario 2: Advanced Parameter Exploration (Mock Mode)

```bash
# Start fresh CLI session
python traigent_benchmark_cli.py
```

**Configuration for this scenario:**
- Experiment name: `advanced_mock_test`
- Examples: 15 (stratified sampling)
- Parameters: Include multiple categories
- Mock mode: Enabled

**Step-by-step:**

1. **Choose Guided Configuration:** `2`

2. **Advanced Dataset Configuration:**
   ```
   Experiment name [benchmark_experiment]: advanced_mock_test
   
   Number of examples to use (1-100) [25]: 15
   Strategy (1-3) [1]: 1
   
   Difficulty distribution:
   Easy examples [3]: 4
   Medium examples [3]: 4
   Hard examples [3]: 4
   Expert examples [6]: 3
   ```

3. **Include Multiple Parameter Categories:**
   ```
   Core LLM:
   Include Core LLM parameters? (y/n) [y]: y
   # Include model (2 values) and temperature (3 values)
   
   Few-Shot Learning:
   Include Few-Shot Learning parameters? (y/n) [y]: y
   # Include few_shot_k (3 values) and few_shot_strategy (2 values)
   
   Prompt Engineering:
   Include Prompt Engineering parameters? (y/n) [y]: y
   # Include system_role (2 values) and output_format (2 values)
   
   Context/Retrieval:
   Include Context/Retrieval parameters? (y/n) [y]: n
   ```

4. **Expected Parameter Combinations:**
   ```
   📈 Total parameter combinations: 144
   ⚠️  Warning: Large number of configurations!
   Optimization strategy (grid/random/bayesian) [random]: random
   Maximum trials [50]: 25
   ```

5. **Mock Mode Execution:**
   ```
   Mode (1-3) [1]: 1
   Use mock mode (no API costs)? (y/n) [n]: y
   Enable early stopping? (y/n) [n]: n
   ```

### Scenario 3: Prompt Engineering Focus (Mock Mode)

```bash
# Launch with focus on prompt engineering
python traigent_benchmark_cli.py
```

**Configuration specifics:**
- Experiment name: `prompt_engineering_test`
- Examples: 20
- Focus: Prompt engineering parameters only
- Mock mode: Enabled

**Key parameter selections:**
```
Core LLM:
Include Core LLM parameters? (y/n) [y]: y
# Only include temperature (3 values)

Few-Shot Learning:
Include Few-Shot Learning parameters? (y/n) [y]: y
# Include few_shot_k: [0, 1, 3]
# Include few_shot_strategy: ["random", "diverse"]

Prompt Engineering:
Include Prompt Engineering parameters? (y/n) [y]: y
# Include system_role: ["classifier", "expert", "technical"]
# Include output_format: ["single_word", "json"]
# Include response_style: ["concise", "detailed"]
# Include chain_of_thought: [True, False]
```

## 🔧 Configuration Management

### Save and Load Configurations

```bash
# Save current configuration during guided setup
# (Automatic prompt during configuration)

# List saved configurations
ls benchmark_configs/
# Output: mock_test_basic.yaml, advanced_mock_test.yaml, etc.

# View a saved configuration
cat benchmark_configs/mock_test_basic.yaml
```

**Example saved configuration:**
```yaml
name: mock_test_basic
dataset:
  total_examples: 10
  sampling_strategy: stratified
  difficulty_distribution:
    easy: 3
    medium: 3
    hard: 2
    expert: 2
execution:
  mode: local
  mock_mode: true
  early_stopping: false
  algorithm: grid
  max_trials: 4
parameters:
  model:
    param_type: categorical
    values:
    - gpt-3.5-turbo
    - gpt-4o-mini
    enabled: true
    description: LLM model to use
  temperature:
    param_type: continuous
    values:
    - 0.0
    - 0.3
    enabled: true
    description: Sampling temperature (0.0 = deterministic, 1.0 = random)
```

### Load Existing Configuration

```bash
# Copy a configuration for modification
cp benchmark_configs/mock_test_basic.yaml benchmark_configs/my_custom_test.yaml

# Edit the configuration
nano benchmark_configs/my_custom_test.yaml

# Currently, loading configurations requires implementation
# Use guided mode to recreate similar configurations
```

## 🎮 Interactive CLI Navigation

### Navigation Commands During Configuration

```bash
# During CLI interaction, you can use:
Ctrl+C          # Exit the CLI safely
Enter           # Accept default values (shown in brackets)
y/yes/n/no      # Boolean responses
1,2,3...        # Menu selections
```

### Understanding CLI Prompts

```bash
# Default values shown in brackets
"Number of examples to use (1-100) [25]:"
# Press Enter to use 25, or type a number

# Boolean prompts
"Use mock mode (no API costs)? (y/n) [n]:"
# Press Enter for 'n' (no), or type 'y' for yes

# Menu selections
"Choice (1-4):"
# Type the number corresponding to your choice
```

## 📊 Understanding Output and Results

### CLI Output Structure

```bash
# 1. Banner and Mode Selection
🎯 TraiGent Advanced Benchmark CLI Tool
📋 Configuration Mode:

# 2. Dataset Configuration
📊 Dataset Configuration
Total examples available: 100

# 3. Parameter Space Configuration
🔧 Parameter Space Configuration
📈 Total parameter combinations: X

# 4. Execution Configuration
⚙️  Execution Configuration
💰 Cost Estimation

# 5. Final Summary
📋 Configuration Summary
✅ Configuration saved!
🚀 Executing Benchmark...
```

### Mock Mode Indicators

```bash
# Look for these indicators in mock mode:
Mock mode: True
Estimated cost: $0.00
✅ Mock mode enabled - no API costs

# During execution:
🔄 Starting optimization with TraiGent...
   Mock mode: true
```

## 🛠️ Troubleshooting Common Issues

### Issue 1: Empty Parameter List Error
```bash
# Error: configuration_space.model: Parameter list cannot be empty
# Solution: Never enter 0 for "How many values to use"

# Fixed in latest version - automatically ensures at least 1 value
# Use the safe_cli_runner.py for predefined configurations:
python safe_cli_runner.py
```

### Issue 2: Dataset Not Found
```bash
# Error: FileNotFoundError: support_classification_dataset.json
# Solution: Ensure you're in the quickstart directory
cd quickstart
ls support_classification_dataset.json  # Should exist

# If missing, you're in the wrong directory
pwd  # Should end with /traigent-sandbox/quickstart
```

### Issue 2: Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'traigent'
# Solution: Ensure TraiGent is installed and venv is activated

# Check virtual environment
which python  # Should point to venv

# Reinstall if needed
cd ../Traigent
pip install -e ".[all]"
```

### Issue 3: API Key Errors in Mock Mode
```bash
# Error: OpenAI API key not found
# Solution: Ensure mock mode is properly set

# Check environment variables
echo $TRAIGENT_MOCK_MODE  # Should be 'true'
echo $OPENAI_API_KEY      # Should be 'mock-key-for-demos'

# Reset mock mode
export TRAIGENT_MOCK_MODE=true
export OPENAI_API_KEY=mock-key-for-demos
```

### Issue 4: Configuration Validation Errors
```bash
# Error: Invalid parameter configuration
# Solution: Start with minimal parameters

# Use these safe defaults for first run:
# - Model: 2 values (gpt-3.5-turbo, gpt-4o-mini)
# - Temperature: 2 values (0.0, 0.5)
# - Examples: 10 or fewer
# - Mock mode: enabled
```

## 🎯 Next Steps and Advanced Usage

### Scenario 4: Real API Testing (Small Scale)
```bash
# Only run this if you have API keys and want to test real calls

# Set up real API keys
cat > .env << 'EOF'
OPENAI_API_KEY=your-real-key-here
TRAIGENT_EXECUTION_MODE=local
TRAIGENT_MOCK_MODE=false
EOF

# Use minimal configuration to limit costs:
# - 5 examples maximum
# - 2 parameters maximum
# - Local execution mode

python traigent_benchmark_cli.py
# Choose very conservative settings!
```

### Scenario 5: Configuration File Workflow
```bash
# 1. Create configuration via CLI (mock mode)
python traigent_benchmark_cli.py
# Save as: production_template.yaml

# 2. Manually edit for production use
nano benchmark_configs/production_template.yaml

# 3. Create variations
cp benchmark_configs/production_template.yaml benchmark_configs/experiment_1.yaml
cp benchmark_configs/production_template.yaml benchmark_configs/experiment_2.yaml

# Edit each for different parameter spaces
```

### Performance Testing
```bash
# Test CLI performance with larger datasets
python traigent_benchmark_cli.py

# Configuration:
# - Examples: 50
# - Parameters: 4-5 different parameters
# - Strategy: random with max_trials: 20
# - Mock mode: enabled
```

## 📚 Additional Resources

### Dataset Information
```bash
# Explore the dataset structure
python -c "
import json
with open('support_classification_dataset.json', 'r') as f:
    data = json.load(f)
    print(f'Total examples: {data[\"metadata\"][\"total_examples\"]}')
    print(f'Categories: {data[\"metadata\"][\"categories\"]}')
    print(f'Difficulty levels: {data[\"metadata\"][\"difficulty_levels\"]}')
"
```

### CLI Tool Architecture
```bash
# Explore the CLI source code
less traigent_benchmark_cli.py

# Key classes:
# - ParameterRegistry: Available parameters
# - DatasetLoader: Dataset handling
# - PromptBuilder: Prompt engineering
# - TraiGentBenchmarkCLI: Main application
```

### Integration with TraiGent SDK
```bash
# The CLI tool uses TraiGent's @optimize decorator
# Study the create_optimized_function method in the CLI source
# This shows how to integrate TraiGent with custom applications
```

This guide provides a comprehensive foundation for using the TraiGent Benchmark CLI tool. Start with mock mode scenarios to understand the interface, then gradually explore more advanced configurations as you become comfortable with the tool.