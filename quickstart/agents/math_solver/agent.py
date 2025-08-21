"""
Math Solver Agent for TraiGent Optimization

This agent specializes in solving mathematical problems across four difficulty levels:
- Easy: Elementary arithmetic and basic algebra
- Mid: Middle school math including fractions, geometry, trigonometry
- Hard: High school math with advanced algebra, calculus, complex trigonometry
- Expert: Engineering-level mathematics with calculus, differential equations, complex numbers

The agent is optimized to provide only numerical answers with exactly 2 decimal places.
"""

import json
import math
import cmath
import os
from typing import Dict, Any


def solve_math_problem(problem: str) -> str:
    """
    Solve a mathematical problem and return only the numerical result.
    
    Instructions for the AI model:
    1. ONLY output the numerical result
    2. Round to exactly 2 decimal places (e.g., 5.00, 3.14, -2.50)
    3. No explanations, working, or additional text
    4. Use standard mathematical functions: sin, cos, tan, log, ln, sqrt, etc.
    5. Handle variables by substitution (e.g., x = 5; y = 3; x + y = ? → 8.00)
    6. For trigonometry, assume degrees unless π is explicitly mentioned
    7. For complex numbers, provide the magnitude or specified component
    8. For calculus problems, use fundamental theorem and basic derivatives/integrals
    
    Examples:
    - Input: "x = 5; y = 90; x + y^2 = ?"
    - Output: "8105.00"
    
    - Input: "sin(30°) = ?"  
    - Output: "0.50"
    
    - Input: "ln(e^2) = ?"
    - Output: "2.00"
    """
    
    # This is a placeholder function. In actual TraiGent usage,
    # this function would be optimized with different LLM configurations
    # to find the best model/parameters for mathematical reasoning.
    
    # For demonstration, we return a formatted response
    # In practice, this would call an LLM with the problem
    
    return f"solve({problem}) → result rounded to 2 decimal places"


def evaluate_math_answer(predicted: str, expected: str) -> Dict[str, Any]:
    """
    Evaluate if the predicted answer matches the expected answer.
    
    Args:
        predicted: The model's predicted answer (should be numerical string)
        expected: The expected correct answer (numerical string)
        
    Returns:
        Dictionary with evaluation metrics
    """
    try:
        pred_num = float(predicted.strip())
        exp_num = float(expected.strip())
        
        # Check exact match (to 2 decimal places)
        exact_match = abs(pred_num - exp_num) < 0.005  # Within rounding tolerance
        
        # Calculate absolute error
        absolute_error = abs(pred_num - exp_num)
        
        # Calculate relative error (avoid division by zero)
        relative_error = absolute_error / max(abs(exp_num), 0.01) if exp_num != 0 else absolute_error
        
        return {
            "exact_match": exact_match,
            "absolute_error": absolute_error,
            "relative_error": relative_error,
            "predicted_value": pred_num,
            "expected_value": exp_num,
            "within_tolerance": absolute_error < 0.01  # 1% tolerance
        }
        
    except (ValueError, TypeError) as e:
        return {
            "exact_match": False,
            "absolute_error": float('inf'),
            "relative_error": float('inf'),
            "predicted_value": None,
            "expected_value": None,
            "error": str(e),
            "within_tolerance": False
        }


def load_math_dataset() -> Dict[str, Any]:
    """Load the math problems dataset."""
    dataset_path = os.path.join(os.path.dirname(__file__), "dataset.json")
    with open(dataset_path, 'r') as f:
        return json.load(f)


def get_problems_by_difficulty(difficulty: str) -> list:
    """Get all problems for a specific difficulty level."""
    dataset = load_math_dataset()
    return [ex for ex in dataset["examples"] if ex["difficulty"] == difficulty]


def validate_dataset():
    """Validate that the dataset has exactly 100 problems with correct distribution."""
    dataset = load_math_dataset()
    examples = dataset["examples"]
    
    total = len(examples)
    difficulties = {}
    
    for example in examples:
        diff = example["difficulty"]
        difficulties[diff] = difficulties.get(diff, 0) + 1
    
    print(f"📊 Dataset Validation:")
    print(f"   Total problems: {total}")
    print(f"   Easy: {difficulties.get('easy', 0)}")
    print(f"   Mid: {difficulties.get('mid', 0)}")
    print(f"   Hard: {difficulties.get('hard', 0)}")
    print(f"   Expert: {difficulties.get('expert', 0)}")
    
    # Validate IDs are unique and sequential
    ids = [ex["id"] for ex in examples]
    expected_ids = list(range(1, 101))
    
    if sorted(ids) == expected_ids:
        print("✅ All IDs are unique and sequential (1-100)")
    else:
        print("❌ ID validation failed")
        missing = set(expected_ids) - set(ids)
        duplicates = [id for id in ids if ids.count(id) > 1]
        if missing:
            print(f"   Missing IDs: {missing}")
        if duplicates:
            print(f"   Duplicate IDs: {duplicates}")


if __name__ == "__main__":
    # Validate the dataset when run directly
    validate_dataset()
    
    # Show sample problems from each difficulty
    dataset = load_math_dataset()
    print("\n🧮 Sample Problems by Difficulty:")
    
    for difficulty in ["easy", "mid", "hard", "expert"]:
        problems = get_problems_by_difficulty(difficulty)
        if problems:
            sample = problems[0]  # First problem of each difficulty
            print(f"\n{difficulty.upper()}: ID {sample['id']}")
            print(f"   Problem: {sample['input']}")
            print(f"   Expected: {sample['expected_output']}")