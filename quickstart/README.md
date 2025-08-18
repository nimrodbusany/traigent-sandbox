# 🚀 QuickStart - TraiGent Examples & Benchmark CLI Tool

**START HERE** - Your fastest path to understanding TraiGent optimization + Advanced CLI tool for experiments.

## 📋 What You'll Learn

In just 5 minutes, you'll understand:
- ✅ How TraiGent works (30 seconds)
- ✅ Basic optimization concepts (2 minutes)  
- ✅ Real-world application (3 minutes)
- ✅ **NEW**: Advanced CLI Benchmark Tool for comprehensive experiments

## 🎯 Three Essential Examples

### 1. **hello_traigent.py** ⭐ *Start Here*
```bash
python hello_traigent.py
```
**What it does:** Proves TraiGent works with a simple "hello world" optimization  
**Time:** 30 seconds  
**Key Learning:** Basic decorator usage and immediate results

### 2. **basic_optimization.py** 
```bash
python basic_optimization.py
```
**What it does:** Shows core optimization concepts with configuration spaces  
**Time:** 2 minutes  
**Key Learning:** How to define what to optimize and measure success

### 3. **real_use_case.py**
```bash
python real_use_case.py
```
**What it does:** Realistic sentiment analysis optimization scenario  
**Time:** 3 minutes  
**Key Learning:** Practical application with real datasets and metrics

## 🎯 Advanced Benchmark CLI Tool

### **traigent_benchmark_cli.py** - Interactive Optimization Experiments

⚠️ **Update**: Fixed empty parameter issue. Use `safe_cli_runner.py` for foolproof configurations.
```bash
# Quick setup (one-time)
python3 -m venv cli_venv
source cli_venv/bin/activate
pip install openai pandas pyyaml
cd ../Traigent && pip install -e . && cd ../quickstart

# Run the CLI tool
python traigent_benchmark_cli.py
```

**Features:**
- 🎮 Interactive configuration wizard
- 💰 Mock mode (no API costs)
- 🔧 12+ optimization parameters
- 📊 30-example test dataset
- 📈 Multiple optimization algorithms

**Quick Test Input** (copy-paste when prompted):
```
2 → test → 5 → 1 → 2 2 1 0 → y → y y n 2 y y n 2 → n n n → 1 y n → y y y
```

## 🎉 Next Steps

After completing quickstart:

1. **🎮 Try CLI Tool**: Advanced experiments with `traigent_benchmark_cli.py`
2. **📚 Learn More**: → `../Traigent/examples/` - Deeper SDK concepts
3. **💼 Use Cases**: → Real-world optimization scenarios  
4. **🔌 Integrate**: → Framework integrations with LangChain, OpenAI

## 📂 Additional Files

- **`demo_cli_usage.py`** - Demonstration of CLI components
- **`support_classification_dataset.json`** - 30-example test dataset
- **`load_env.py`** - Environment configuration (auto-creates mock mode)
- **`benchmark_configs/`** - Saved CLI configurations

## 🆘 Need Help?

- **CLI Setup Issues?** Run: `source cli_venv/bin/activate`
- **Import Errors?** Install: `pip install openai pandas pyyaml`
- **Mock Mode?** Check `.env` has: `TRAIGENT_MOCK_MODE=true`
- **Full Guide?** See: `../TRAIGENT_CLI_GUIDE.md`

---
*Basic examples: 5 minutes • CLI setup: 2 minutes • Ready for: Advanced optimization experiments*