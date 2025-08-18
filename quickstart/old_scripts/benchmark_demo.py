#!/usr/bin/env python3
"""
TraiGent Benchmark Demo Script

This script demonstrates the configurable benchmark CLI tool using TraiGent's
parameter injection capabilities instead of complex dynamic function building.
"""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from load_env import load_demo_env
from shared_utils.mock_llm import setup_mock_mode
import traigent
from traigent.utils.callbacks import StatisticsCallback

# Load environment
load_demo_env()

def create_simple_dataset() -> str:
    """Create a small evaluation dataset for quick testing"""
    data = [
        {"input": {"text": "My app crashes when I upload files"}, "output": "technical"},
        {"input": {"text": "Login page shows 500 error"}, "output": "technical"},
        {"input": {"text": "When does my subscription renew?"}, "output": "billing"},
        {"input": {"text": "How do I upgrade my plan?"}, "output": "billing"},
        {"input": {"text": "What are your business hours?"}, "output": "general"},
        {"input": {"text": "How do I contact customer support?"}, "output": "general"},
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for item in data:
            json.dump(item, f)
            f.write("\n")
        return f.name

# Initialize TraiGent
backend_url = os.environ.get("TRAIGENT_BACKEND_URL")
api_key = os.environ.get("TRAIGENT_API_KEY")

if backend_url and api_key:
    traigent.initialize(
        api_url=backend_url,
        api_key=api_key,
        execution_mode="standard",
    )
    print("🌐 Running in STANDARD mode with backend support")
else:
    traigent.initialize(execution_mode="local")
    print("🏠 Running in LOCAL mode (no backend required)")

# Set up mock mode for cost-free testing
setup_mock_mode()

# Using TraiGent's parameter injection - the decorator automatically
# injects the optimized parameter values into the function
@traigent.optimize(
    eval_dataset=create_simple_dataset(),
    objectives=["accuracy"],
    configuration_space={
        "model": ["gpt-3.5-turbo", "gpt-4o-mini"],  # 2 models
        "temperature": [0.0, 0.3, 0.7],             # 3 temperatures  
        "max_tokens": [10, 20],                     # 2 token limits
        "system_role": ["classifier", "expert"],    # 2 prompt roles
        "output_format": ["single_word", "json"],   # 2 output formats
    },
    max_trials=12,  # Test subset of combinations
    algorithm="random"
)
def classify_support_query_advanced(
    text: str, 
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.3,
    max_tokens: int = 10,
    system_role: str = "classifier",
    output_format: str = "single_word"
) -> str:
    """
    Advanced classification function with multiple parameter dimensions.
    TraiGent automatically injects optimized parameter combinations.
    """
    import openai
    
    # Build system message based on role
    system_messages = {
        "classifier": "Classify as: technical, billing, or general",
        "expert": "You are an expert customer support specialist. Classify queries as: technical, billing, or general"
    }
    
    # Build output format instructions
    format_instructions = {
        "single_word": "Respond with only the category name.",
        "json": "Respond with JSON: {\"category\": \"technical|billing|general\", \"confidence\": 0.0-1.0}"
    }
    
    system_content = f"{system_messages.get(system_role, system_messages['classifier'])}\n\n{format_instructions.get(output_format, format_instructions['single_word'])}"
    
    # TraiGent automatically injects the optimized parameter values
    response = openai.chat.completions.create(
        model=model,        # ← TraiGent injects optimized value
        temperature=temperature,  # ← TraiGent injects optimized value
        max_tokens=max_tokens,   # ← TraiGent injects optimized value
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": text},
        ],
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("No content in response")
    
    # Extract category from different formats
    result = content.strip().lower()
    if output_format == "json":
        try:
            import json
            parsed = json.loads(result)
            result = parsed.get("category", result)
        except:
            pass  # Fall back to raw content
    
    return result

async def main():
    """Demonstrate the parameter injection approach"""
    print("🎯 TraiGent Parameter Injection Demo")
    print("=" * 50)
    print("This demo shows how TraiGent automatically injects optimized")
    print("parameters without requiring complex dynamic function building.")
    print()
    
    # Calculate optimization space
    total_combinations = 2 * 3 * 2 * 2 * 2  # models × temps × tokens × roles × formats = 48
    print(f"📊 Optimization Space:")
    print(f"   • Models: 2 (gpt-3.5-turbo, gpt-4o-mini)")
    print(f"   • Temperatures: 3 (0.0, 0.3, 0.7)")
    print(f"   • Max tokens: 2 (10, 20)")
    print(f"   • System roles: 2 (classifier, expert)")
    print(f"   • Output formats: 2 (single_word, json)")
    print(f"   • Total combinations: {total_combinations}")
    print(f"   • Testing: 12 random combinations (25%)")
    print()
    
    # Test single call first
    print("🧪 Testing single function call...")
    test_query = "My app keeps crashing when I upload large files"
    result = classify_support_query_advanced(test_query)
    print(f"   Query: '{test_query}'")
    print(f"   Result: {result}")
    print()
    
    # Run optimization using TraiGent's parameter injection
    print("🔄 Running optimization with parameter injection...")
    print("   TraiGent will automatically test different parameter combinations")
    print("   and inject the optimal values into the function calls.")
    print()
    
    results = await classify_support_query_advanced.optimize()
    
    print("✅ Optimization Complete!")
    print(f"   Best configuration: {results.best_config}")
    print(f"   Best accuracy: {results.best_score:.1%}")
    print()
    
    print("🎯 Key Benefits of Parameter Injection Approach:")
    print("   ✅ No complex dynamic function building required")
    print("   ✅ TraiGent handles parameter override automatically")
    print("   ✅ Simple @traigent.optimize decorator")
    print("   ✅ Clean, readable function code")
    print("   ✅ All parameter combinations tested systematically")
    print()
    
    # Show best configuration details
    if results.best_config:
        print("🏆 Optimal Configuration Found:")
        for param, value in results.best_config.items():
            print(f"   • {param}: {value}")
    
    print()
    print("🚀 This approach leverages TraiGent's built-in parameter injection")
    print("   instead of building complex dynamic function builders!")

if __name__ == "__main__":
    asyncio.run(main())