# Math Solver Agent

A comprehensive mathematical problem-solving agent for TraiGent optimization with 100 carefully crafted problems across 4 difficulty levels.

## 📊 Dataset Overview

- **Total Problems**: 100 (ID 1-100)
- **Difficulty Levels**: 4 categories, 25 problems each
- **Output Format**: Numerical results rounded to exactly 2 decimal places
- **Evaluation**: Exact match with tolerance for rounding

### Difficulty Distribution

| Level | Count | Description | Examples |
|-------|--------|-------------|----------|
| **Easy** | 25 | Elementary arithmetic, basic algebra | `x = 7; y = 3; x + y = ?` |
| **Mid** | 25 | Middle school: fractions, geometry, basic trig | `sin(30°) = ?`, `Find 15% of 80` |
| **Hard** | 25 | High school: advanced algebra, calculus, trigonometry | `log₂(16) = ?`, `sin²(30°) + cos²(30°) = ?` |
| **Expert** | 25 | Engineering: calculus, complex numbers, advanced functions | `∫₀¹ x² dx = ?`, `f'(x) = 3x² - 2x; f'(2) = ?` |

## 🎯 Agent Specifications

### Problem Types Covered
- **Arithmetic**: Addition, subtraction, multiplication, division
- **Algebra**: Variable substitution, equation solving, polynomials
- **Geometry**: Area, perimeter, Pythagorean theorem
- **Trigonometry**: Sin, cos, tan functions (degrees and radians)
- **Logarithms**: Natural log (ln), base-2, base-10
- **Calculus**: Derivatives, integrals, limits
- **Complex Numbers**: Complex arithmetic, magnitude
- **Engineering Math**: Vectors, matrices, Fourier analysis

### Output Requirements
- **Format**: Numerical value only (e.g., "8105.00")
- **Precision**: Exactly 2 decimal places
- **Rounding**: Standard rounding (0.5 rounds up)
- **No Text**: No explanations, units, or additional text

## 🚀 Usage Examples

### Basic TraiGent Optimization
```python
import traigent
from quickstart.agents.math_solver.agent import solve_math_problem

@traigent.optimize(
    configuration_space={
        "model": ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"],
        "temperature": [0.0, 0.1, 0.2],
        "max_tokens": [10, 20, 50]
    },
    eval_dataset="quickstart/agents/math_solver/dataset.json",
    objectives=["accuracy"]
)
def math_solver(problem: str) -> str:
    return solve_math_problem(problem)

# Run optimization
results = math_solver.optimize(max_trials=20)
```

### Using with Benchmark CLI
```bash
cd quickstart
python traigent_benchmark_cli.py
# Select: Load existing agent configuration
# Choose: math_solver
```

### Testing Individual Problems
```python
from quickstart.agents.math_solver.agent import validate_dataset, get_problems_by_difficulty

# Validate dataset structure
validate_dataset()

# Get problems by difficulty
easy_problems = get_problems_by_difficulty("easy")
expert_problems = get_problems_by_difficulty("expert")
```

## 📈 Expected Performance

### Difficulty vs. Accuracy Expectations
- **Easy**: >95% accuracy with most models
- **Mid**: 85-95% accuracy (depends on trigonometry handling)
- **Hard**: 70-90% accuracy (complex calculations)
- **Expert**: 50-80% accuracy (advanced mathematical concepts)

### Model Performance Hints
- **GPT-4o**: Best for complex calculus and engineering problems
- **GPT-4o-mini**: Good balance of speed and accuracy
- **GPT-3.5-turbo**: Suitable for elementary and mid-level problems
- **Temperature**: Use 0.0-0.2 for consistent mathematical calculations
- **Max Tokens**: 10-20 sufficient for numerical answers

## 🧮 Problem Examples

### Easy (Elementary)
```
ID 1: x = 7; y = 3; x + y = ? → 10.00
ID 5: x = 3; x^2 = ? → 9.00
ID 8: x = 16; √x = ? → 4.00
```

### Mid (Middle School) 
```
ID 26: x = 3/4; y = 1/2; x + y = ? → 1.25
ID 31: sin(30°) = ? → 0.50
ID 29: r = 5; Area of circle = πr^2 = ? → 78.54
```

### Hard (High School)
```
ID 51: Solve x^2 - 5x + 6 = 0; Positive root x = ? → 3.00
ID 52: log₂(16) = ? → 4.00
ID 65: x = π/3; tan(x) = ? → 1.73
```

### Expert (Engineering)
```
ID 76: f(x) = x^3 - 2x^2 + x; f'(x) at x = 2 = ? → 5.00
ID 77: ∫₀¹ x^2 dx = ? → 0.33
ID 78: z₁ = 3 + 4i; z₂ = 2 - i; z₁ × z₂ = ? (Real part) → 10.00
```

## 🔧 Configuration Options

The agent supports extensive parameter optimization:

- **Model Selection**: 6 different LLM models
- **Temperature Control**: 5 levels from deterministic to creative
- **Token Management**: Optimized for numerical outputs
- **Mathematical Precision**: Multiple precision and rounding modes
- **Problem Context**: Difficulty-aware prompting
- **Verification**: Built-in answer checking capabilities

## 📝 Notes

- All problems have been manually verified for correct answers
- Problems progress logically within each difficulty level
- Covers major mathematical domains relevant to AI reasoning
- Optimized for TraiGent's optimization algorithms
- Suitable for benchmarking mathematical reasoning capabilities