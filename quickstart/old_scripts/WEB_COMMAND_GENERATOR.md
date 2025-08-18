# 🎯 TraiGent CLI Command Generator Web Tools

Since working with the interactive CLI can be complex, we've created two web-based tools to generate copy-paste commands with your desired parameters.

## Option 1: HTML Generator (No Installation Required)

### Quick Start
Simply open the HTML file in your browser:
```bash
# Navigate to quickstart directory
cd /home/nimrodbu/projects/traigent-sandbox/quickstart

# Open in default browser
open cli_generator.html
# OR
xdg-open cli_generator.html  # Linux
# OR just double-click the file in your file manager
```

### Features
- ✅ **No dependencies** - Works in any modern browser
- ✅ **Visual interface** - Checkboxes and dropdowns for easy configuration
- ✅ **Real-time updates** - See parameter combinations instantly
- ✅ **Multiple output formats** - Echo, Heredoc, and Python script
- ✅ **Copy to clipboard** - One-click copying

### Screenshot of Interface
```
🎯 TraiGent CLI Command Generator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Configuration          │ Summary
─────────────────────  │ ────────────
Experiment: test_20    │ Total: 18
Examples: 10           │ Models: 2
                       │ Params: 3
☑ GPT-3.5  ☑ GPT-4mini │
☑ 0.0  ☑ 0.5  ☑ 1.0   │ ✅ Mock mode
☑ 50   ☑ 100  ☑ 200   │
```

## Option 2: Streamlit App (Advanced Features)

### Installation
```bash
# Install Streamlit if not already installed
pip install streamlit

# OR use the virtual environment
source cli_venv/bin/activate
pip install streamlit
```

### Launch
```bash
# Using the launch script
./run_webapp.sh

# OR directly with streamlit
streamlit run cli_command_generator.py
```

Then open http://localhost:8501 in your browser.

### Additional Features
- 📊 More detailed parameter options
- 💰 Cost estimation for non-mock mode
- 📁 Configuration export/import
- 🎨 Better UI with Streamlit components

## Example: Creating a 20-Configuration Test

### Using HTML Generator:
1. Open `cli_generator.html` in browser
2. Select:
   - 2 models (GPT-3.5, GPT-4 Mini)
   - 3 temperatures (0.0, 0.5, 1.0)
   - Check "Include Max Tokens"
   - Select 3 max token values (50, 100, 200)
   - Total: 2 × 3 × 3 = 18 configurations
3. Copy the generated command
4. Paste in terminal and run

### Generated Command Example:
```bash
source cli_venv/bin/activate
python traigent_benchmark_cli.py << 'EOF'
2
test_18_configs
10
3
y
y
y
gpt-3.5-turbo,gpt-4o-mini
y
y
0.0,0.5,1.0
y
y
50,100,200
n
n
n
n
1
y
n
y
y
y
EOF
```

## Common Configuration Examples

### Quick Test (4 configs)
- 2 models × 2 temperatures
- Models: gpt-3.5-turbo, gpt-4o-mini
- Temperatures: 0.0, 0.7

### Medium Test (18 configs)
- 2 models × 3 temperatures × 3 max_tokens
- Models: gpt-3.5-turbo, gpt-4o-mini
- Temperatures: 0.0, 0.5, 1.0
- Max tokens: 50, 100, 200

### Large Test (24 configs)
- 3 models × 4 temperatures × 2 few_shot
- Models: gpt-3.5-turbo, gpt-4o-mini, gpt-4o
- Temperatures: 0.0, 0.3, 0.7, 1.0
- Few-shot: 0, 3

### Comprehensive Test (36 configs)
- 3 models × 3 temperatures × 2 max_tokens × 2 few_shot
- All parameter types enabled

## Tips for Using the Generators

1. **Start with Mock Mode** - Always test with mock mode first to ensure configuration works
2. **Use Sequential Sampling** - Faster for initial tests (option 3)
3. **Save Configurations** - Answer "y" to save for reuse
4. **Monitor Output** - Watch for the "Optimization Complete!" message
5. **Check All Trials** - Results show every parameter combination tested

## Understanding the Output

When you run the generated command, you'll see:

```
🎯 Running optimization...
==================================================

✅ Optimization Complete!
==================================================
Best configuration found:
  • model: gpt-3.5-turbo
  • temperature: 0.5
  • max_tokens: 100

Best score: 0.0%

📊 All Trials (18 total):
  Trial 1: Score = 0.0%, Config = {'model': 'gpt-3.5-turbo', 'temperature': 0.0, 'max_tokens': 50}
  Trial 2: Score = 0.0%, Config = {'model': 'gpt-3.5-turbo', 'temperature': 0.0, 'max_tokens': 100}
  ...
```

## Troubleshooting

### Command doesn't run
- Make sure you're in the `quickstart` directory
- Activate the virtual environment: `source cli_venv/bin/activate`
- Check that `traigent_benchmark_cli.py` exists

### HTML page doesn't work
- Use a modern browser (Chrome, Firefox, Safari, Edge)
- Make sure JavaScript is enabled
- Try the Streamlit version instead

### Streamlit won't start
- Install streamlit: `pip install streamlit`
- Check port 8501 isn't already in use
- Try a different port: `streamlit run cli_command_generator.py --server.port 8502`

## Next Steps

1. Generate a command with desired parameters
2. Run it to see optimization in action
3. Save successful configurations for reuse
4. Switch to real API keys when ready for actual optimization
5. Analyze results to find best parameter combinations