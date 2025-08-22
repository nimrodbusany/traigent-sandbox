# LiveBench Math Agent for TraiGent

This agent integrates LiveBench's mathematical problem datasets with TraiGent's optimization framework.

## Overview

The LiveBench Math Agent is designed to solve problems from LiveBench's math categories:
- **math_competition_problems**: AMC, AIME, IMO competition problems
- **amps_hard**: Advanced mathematical problem solving
- **proof_rearrangement**: Mathematical proof tasks

## Setup Instructions

### 1. Install LiveBench

```bash
# Clone the LiveBench repository
git clone https://github.com/livebench/livebench
cd livebench

# Install LiveBench
pip install -e .
```

### 2. Download LiveBench Math Questions

```bash
# Download the latest LiveBench questions
python -m livebench.download_questions

# Questions will be downloaded to:
# livebench/data/math/math_competition_problems/question.jsonl
# livebench/data/math/amps_hard/question.jsonl
# livebench/data/math/proof_rearrangement/question.jsonl
```

### 3. Convert LiveBench Data for TraiGent

After downloading LiveBench questions, you'll need to convert them to TraiGent format:

```python
import json

# Load LiveBench questions
with open('livebench/data/math/math_competition_problems/question.jsonl', 'r') as f:
    questions = [json.loads(line) for line in f]

# Convert to TraiGent format
traigent_examples = []
for q in questions:
    example = {
        "id": q["question_id"],
        "input": {"problem": q["turns"][0]},  # LiveBench questions are in "turns"
        "output": q["ground_truth"],
        "difficulty": q.get("difficulty", "medium"),
        "task": q["task"]
    }
    traigent_examples.append(example)

# Save for TraiGent
with open('agents/livebench_competition_math/dataset.json', 'w') as f:
    json.dump({
        "examples": traigent_examples,
        "metadata": {
            "source": "LiveBench",
            "categories": ["math_competition_problems"]
        }
    }, f, indent=2)
```

## Using with TraiGent CLI

Once you have LiveBench data in place:

```bash
# List available agents (should show livebench_competition_math)
python traigent_cli.py --list-agents

# Run optimization on LiveBench math problems
python traigent_cli.py \
    --agent livebench_competition_math \
    --models gpt-4o gpt-4 \
    --temperature 0.0 0.1 0.2 \
    --num-examples 10 \
    --algorithm grid \
    --max-trials 20
```

## Agent Parameters

The agent optimizes several parameters for LiveBench math:

### Core LLM Parameters
- **model**: LLM model (gpt-4o recommended for math)
- **temperature**: Low values (0.0-0.3) for consistent reasoning
- **max_tokens**: 500-2000 for complete solutions

### Problem-Solving Parameters
- **system_role**: Mathematical expertise persona
  - `livebench_solver`: General LiveBench optimization
  - `competition_expert`: For AMC/AIME/IMO problems
  - `proof_specialist`: For proof tasks
  
- **solution_approach**: Problem-solving strategy
  - `systematic`: Step-by-step approach
  - `pattern_matching`: Competition techniques
  - `direct`: Formula application
  - `construction`: Build from first principles

### LiveBench-Specific Parameters
- **answer_format**: Output format for LiveBench evaluation
  - `livebench_standard`: Auto-detect format
  - `amc_format`: Multiple choice (A-E)
  - `aime_format`: Integer (000-999)
  - `proof_format`: Numbered proof steps

## LiveBench Evaluation

LiveBench uses automatic ground-truth evaluation:

1. **AMC/SMC Problems**: Letter choice matching
2. **AIME Problems**: Exact integer matching
3. **Proof Problems**: Step verification
4. **AMPS Problems**: Numerical answer matching

The agent formats answers according to LiveBench's expectations for proper evaluation.

## Example Problem Types

### Competition Math (AMC)
```
Problem: "Find the number of positive integers n ≤ 1000 such that 15n is a perfect square."
Expected: "66"
```

### AIME Format
```
Problem: "If x + 1/x = 3, find x^4 + 1/x^4"
Expected: "047" (3-digit format)
```

### Proof Task
```
Problem: "Prove that n^5 - n is divisible by 30 for all positive integers n"
Expected: Structured proof with numbered steps
```

## Integration with LiveBench Evaluation

To evaluate your optimized model with LiveBench:

```bash
# Run LiveBench evaluation
cd livebench
python run_livebench.py \
    --model your_optimized_model \
    --bench-name live_bench/math \
    --livebench-release-option 2024-11-25

# View results
python show_livebench_result.py --model-name your_optimized_model
```

## Notes

- This agent is designed to work with actual LiveBench data
- Strong models (GPT-4, Claude-3) recommended for mathematical reasoning
- Low temperature values typically work better for math
- Chain-of-thought reasoning improves accuracy
- Few-shot examples from LiveBench can significantly help

## References

- LiveBench Repository: https://github.com/livebench/livebench
- LiveBench Paper: https://livebench.ai
- HuggingFace Dataset: https://huggingface.co/datasets/livebench/livebench