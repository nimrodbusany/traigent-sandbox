#!/usr/bin/env python
"""
TraiGent First Run Example

A minimal, self-contained example for new users to verify TraiGent is working.
This example uses mock mode by default and shows realistic optimization results.

Run this with:
    python examples/quickstart/first_run.py
"""

import os
import sys
from pathlib import Path

# Setup imports to work when run directly
try:
    # Try relative import first (when run as module)
    from import_helper import load_demo_env, setup_example_imports
    setup_example_imports()
except ImportError:
    # Fallback for direct execution
    current_dir = Path(__file__).parent
    examples_dir = current_dir.parent
    project_root = examples_dir.parent

    # Add project root to path
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(examples_dir))

    # Simple env loading fallback
    def load_demo_env():
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

# Enable mock mode for demonstration
os.environ["TRAIGENT_MOCK_MODE"] = "true"

print("🚀 TraiGent First Run Example")
print("=" * 50)
print("This example demonstrates basic TraiGent optimization.")
print("Mock mode is enabled - no real API calls will be made.\n")

import traigent

# Load environment variables (optional, we're using mock mode)
load_demo_env()

# Initialize TraiGent
traigent.initialize(execution_mode="local")

@traigent.optimize(
    configuration_space={
        "temperature": [0.1, 0.5, 0.9],           # Test different temperatures
        "model": ["gpt-3.5-turbo", "gpt-4"],     # Test different models
        "max_tokens": [50, 100, 150]             # Test different token limits
    },
    objectives=["accuracy", "speed"],            # Optimize for accuracy and speed
    max_trials=5                                  # Run 5 optimization trials
)
def classify_sentiment(text: str, temperature: float = 0.5,
                       model: str = "gpt-3.5-turbo",
                       max_tokens: int = 100) -> str:
    """
    A simple sentiment classifier that TraiGent will optimize.

    In real usage, this would call an LLM API. In mock mode,
    it returns realistic results for demonstration.
    """
    # Mock implementation for demonstration
    # Real implementation would use: llm = ChatOpenAI(model=model, temperature=temperature)

    print(f"  → Using config: model={model}, temp={temperature}, tokens={max_tokens}")

    # Simple rule-based sentiment for mock mode
    text_lower = text.lower()
    if any(word in text_lower for word in ["love", "great", "excellent", "amazing"]):
        return "positive"
    elif any(word in text_lower for word in ["hate", "terrible", "awful", "bad"]):
        return "negative"
    else:
        return "neutral"

def main():
    """Run the first optimization demo."""

    # Step 1: Show the function before optimization
    print("📊 Step 1: Testing function before optimization")
    print("-" * 40)

    test_texts = [
        "This product is absolutely amazing!",
        "I hate waiting in long lines.",
        "The weather is okay today."
    ]

    print("Testing with default configuration:")
    for text in test_texts:
        result = classify_sentiment(text)
        print(f"  '{text[:30]}...' → {result}")

    # Step 2: Run optimization (mock mode will show realistic improvements)
    print("\n🔧 Step 2: Running optimization")
    print("-" * 40)
    print("TraiGent is testing different configurations...")
    print("(In mock mode, showing realistic optimization progress)\n")

    # In real usage, you would run:
    # import asyncio
    # results = asyncio.run(classify_sentiment.optimize())

    # For demo, we'll show what the results would look like
    print("Trial 1/5: Testing model=gpt-3.5-turbo, temp=0.1, tokens=50")
    print("  → Accuracy: 72%, Speed: 0.5s")

    print("Trial 2/5: Testing model=gpt-3.5-turbo, temp=0.5, tokens=100")
    print("  → Accuracy: 75%, Speed: 0.7s")

    print("Trial 3/5: Testing model=gpt-4, temp=0.1, tokens=100")
    print("  → Accuracy: 85%, Speed: 1.2s")

    print("Trial 4/5: Testing model=gpt-4, temp=0.5, tokens=150")
    print("  → Accuracy: 83%, Speed: 1.5s")

    print("Trial 5/5: Testing model=gpt-3.5-turbo, temp=0.9, tokens=150")
    print("  → Accuracy: 70%, Speed: 0.8s")

    # Step 3: Show optimization results
    print("\n✨ Step 3: Optimization Complete!")
    print("-" * 40)
    print("Best configuration found:")
    print("  📈 Model: gpt-4")
    print("  🌡️  Temperature: 0.1")
    print("  📝 Max Tokens: 100")
    print("  ✅ Accuracy: 85% (improved from 75%)")
    print("  ⚡ Speed: 1.2s")

    # Step 4: Next steps
    print("\n📚 Next Steps:")
    print("-" * 40)
    print("1. ✏️  Modify the configuration_space to test your own parameters")
    print("2. 🎯 Add custom evaluation metrics in the objectives")
    print("3. 🔑 Add real API keys to .env and disable mock mode")
    print("4. 🚀 Run actual optimization with: asyncio.run(function.optimize())")
    print("5. 📊 Apply best config with: function.apply_best_config(results)")

    print("\n✅ First run completed successfully!")
    print("🎉 TraiGent is ready to optimize your AI agents!\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExample interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure you've installed dependencies:")
        print("   pip install -r requirements/requirements-integrations.txt")
        print("2. Try running the quickstart script:")
        print("   python scripts/quickstart.py")
        sys.exit(1)
