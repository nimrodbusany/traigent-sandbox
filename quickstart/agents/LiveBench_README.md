# LiveBench Integration Guide

## Overview

[LiveBench](https://github.com/livebench/livebench) is a challenging, contamination-free LLM benchmark designed to provide objective evaluation of language models across diverse tasks. It features monthly updates with new questions based on recent datasets, arXiv papers, news articles, and IMDb movie synopses.

**Key Features:**
- 🎯 Objective ground-truth answers without LLM judges
- 🔄 Monthly question releases to prevent contamination
- 📊 18 diverse tasks across 6 categories
- 🚀 Parallel evaluation support
- 🔌 OpenAI-compatible API support

## Dataset Categories and Tasks

| Category | Description | Dataset Location | Evaluation Focus |
|----------|-------------|------------------|------------------|
| **Reasoning** | Logical and analytical thinking tasks | `livebench/data/reasoning/*/question.jsonl` | Logical deduction, pattern recognition |
| **Math** | Mathematical problem-solving | `livebench/data/math/*/question.jsonl` | Computation, proofs, word problems |
| **Coding** | Programming challenges | `livebench/data/coding/*/question.jsonl` | Code generation, debugging, algorithms |
| **Language** | Natural language understanding | `livebench/data/language/*/question.jsonl` | Comprehension, generation, translation |
| **Data Analysis** | Data interpretation and analysis | `livebench/data/data_analysis/*/question.jsonl` | Statistical analysis, visualization interpretation |
| **Instruction Following** | Following complex instructions | `livebench/data/instruction_following/*/question.jsonl` | Multi-step instructions, constraint satisfaction |

## Dataset Characteristics

| Property | Details |
|----------|---------|
| **Total Categories** | 6 |
| **Total Tasks** | 18 (distributed across categories) |
| **Question Format** | JSONL with structured fields |
| **Update Frequency** | Monthly releases |
| **Difficulty Levels** | Not explicitly specified (varies by task) |
| **Dataset Size** | Varies by release date and task |
| **Source Materials** | Recent datasets, arXiv papers, news, IMDb synopses |

## Repository Structure

```
livebench/
├── livebench/
│   ├── run_livebench.py              # Main evaluation script
│   ├── gen_api_answer.py             # API answer generation
│   ├── gen_ground_truth_judgment.py  # Scoring script
│   ├── show_livebench_result.py      # Results display
│   ├── download_questions.py         # Dataset downloader
│   ├── model/                        # Model configurations
│   ├── process_results/              # Result processing utilities
│   └── scripts/                      # Helper scripts
├── data/                              # Dataset storage (downloaded from HuggingFace)
│   ├── reasoning/
│   ├── math/
│   ├── coding/
│   ├── language/
│   ├── data_analysis/
│   └── instruction_following/
└── docs/                              # Documentation

```

## Dataset Format

Each dataset is stored as a JSONL file with the following structure:

```json
{
  "question_id": "unique_identifier",
  "category": "category_name",
  "task": "specific_task_name",
  "turns": ["question text"],
  "ground_truth": "correct_answer"
}
```

## Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Clone repository
git clone https://github.com/livebench/livebench.git
cd livebench

# Basic installation
pip install -e .

# For local GPU inference with flash attention
pip install -e .[flash_attn]
```

## Running Evaluations

### Basic Evaluation Example

```python
# Example 1: Run evaluation on a specific category
python run_livebench.py \
    --model gpt-4o \
    --bench-name live_bench/coding \
    --livebench-release-option 2024-11-25

# Example 2: Run on all categories with parallel processing
python run_livebench.py \
    --model gpt-4o \
    --bench-name live_bench \
    --mode parallel \
    --parallel-requests 10

# Example 3: Evaluate with custom API endpoint
python run_livebench.py \
    --model my-model \
    --api-base http://localhost:8000/v1 \
    --bench-name live_bench/math
```

### Python Integration Example

```python
import subprocess
import json

def run_livebench_evaluation(model_name, category, release_date="2024-11-25"):
    """
    Run LiveBench evaluation for a specific model and category.
    
    Args:
        model_name: Name of the model to evaluate
        category: Category to test (e.g., 'coding', 'math', 'reasoning')
        release_date: LiveBench release date to use
    
    Returns:
        dict: Evaluation results
    """
    cmd = [
        "python", "run_livebench.py",
        "--model", model_name,
        "--bench-name", f"live_bench/{category}",
        "--livebench-release-option", release_date
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse and return results
    # Results are typically saved to output files
    return parse_results(model_name, category)

def parse_results(model_name, category):
    """Parse evaluation results from output files."""
    # Implementation depends on LiveBench output format
    results_file = f"results/{model_name}_{category}.json"
    with open(results_file, 'r') as f:
        return json.load(f)

# Example usage
results = run_livebench_evaluation("gpt-3.5-turbo", "coding")
print(f"Score: {results.get('score', 'N/A')}")
```

## Available Release Dates

LiveBench provides datasets from multiple release dates:
- 2024-06-24
- 2024-07-26
- 2024-08-31
- 2024-11-25
- 2025-04-02 (upcoming)
- 2025-04-25 (upcoming)
- 2025-05-30 (upcoming)

## Evaluation Process

1. **Download Questions**: Questions are automatically downloaded from HuggingFace
2. **Generate Answers**: Models generate answers for each question
3. **Ground Truth Judgment**: Automatic scoring against objective answers
4. **Results Display**: View results using `show_livebench_result.py`

```bash
# Show results after evaluation
python show_livebench_result.py --model-name gpt-4o
```

## Key Advantages

- **Contamination-Free**: Monthly updates with new questions prevent memorization
- **Objective Scoring**: No subjective LLM judges needed
- **Diverse Tasks**: Comprehensive evaluation across multiple domains
- **API Compatibility**: Works with OpenAI-compatible APIs
- **Parallel Processing**: Fast evaluation with concurrent requests

## Integration with TraiGent

To integrate LiveBench tasks as TraiGent agents:

1. Select a specific LiveBench task/category
2. Download the corresponding dataset
3. Create an agent configuration that maps to LiveBench evaluation
4. Use TraiGent's optimization to find best model parameters

Example agent structure:
```
agents/
└── livebench_math/
    ├── agent.py          # LiveBench math task wrapper
    ├── config.json       # TraiGent configuration
    └── dataset.json      # Converted LiveBench questions
```

## References

- **GitHub Repository**: https://github.com/livebench/livebench
- **Paper**: Spotlight paper at ICLR 2025
- **HuggingFace Datasets**: https://huggingface.co/livebench
- **Leaderboard**: Available through the LiveBench website

## Utility Scripts

The repository includes utility scripts in `quickstart/agents/utils/` to help you get started with LiveBench data:

### download_livebench_data.py
Downloads LiveBench math questions directly from HuggingFace and converts them to TraiGent format:
```bash
cd quickstart/agents/utils
python download_livebench_data.py
```
This script:
- Downloads 50 LiveBench math competition problems
- Converts them to TraiGent-compatible JSON format
- Saves to `livebench_competition_math/dataset.json`

### download_livebench_simple.py
A simplified downloader for quick testing:
```bash
cd quickstart/agents/utils
python download_livebench_simple.py
```
This script:
- Creates a minimal dataset with sample problems
- Useful for initial testing and setup verification
- Saves to `livebench_competition_math/dataset.json`

## Notes

- LiveBench is designed for rigorous, objective evaluation
- Questions are based on recent, uncontaminated sources
- The benchmark evolves monthly to maintain relevance
- Supports both API-based and local model evaluation
- Use the utility scripts to quickly download and convert LiveBench data for TraiGent optimization