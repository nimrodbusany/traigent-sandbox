"""
TraiGent Basic Sentiment Analysis Tuning Demo
============================================

A simple demo showing how TraiGent can optimize sentiment analysis.

Run from project root:
    python -m demos.01-fundamentals.00-sdk-basic-usage.01_basic_sentiment_analysis_tuning.basic_sentiment_tuning
"""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

from anthropic import Anthropic
from load_env import load_demo_env
from shared_utils.caching import create_llm_cache_key, setup_demo_cache
from shared_utils.mock_llm import setup_mock_mode

import traigent
from traigent.utils.callbacks import DetailedProgressCallback

# Add shared_utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared_utils"))

# Load demo environment variables
load_demo_env()

# Initialize demo cache
_demo_cache = setup_demo_cache("basic-sentiment-tuning")

# Check if we have Anthropic installed
try:
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


async def create_dataset() -> str:
    """Create a simple sentiment analysis dataset."""
    examples = [
        # Sarcasm examples
        {
            "input": {
                "text": "Oh great, another software update that breaks everything!"
            },
            "output": "negative",
        },
        {
            "input": {"text": "Wow, paying $5 for water. What a bargain!"},
            "output": "negative",
        },
        # Mixed sentiment
        {"input": {"text": "The movie was bad but entertaining."}, "output": "mixed"},
        {"input": {"text": "Good book, kept me up all night."}, "output": "positive"},
        # Neutral/subtle
        {"input": {"text": "It's fine, I guess."}, "output": "neutral"},
        {
            "input": {"text": "Service was adequate, better than expected."},
            "output": "mixed",
        },
        # Clear sentiment (baseline)
        {"input": {"text": "Absolutely fantastic! Best ever!"}, "output": "positive"},
        {
            "input": {"text": "Terrible experience. Would not recommend."},
            "output": "negative",
        },
    ]

    # Save to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for example in examples:
            json.dump(example, f)
            f.write("\n")
        return f.name


@traigent.optimize(
    configuration_space={
        "model": [
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229",
        ],
        "temperature": [0.0, 0.3, 0.5],
    },
    objectives=["accuracy"],
    execution_mode="local",
)
async def analyze_sentiment(
    text: str, model: str = "claude-3-haiku-20240307", temperature: float = 0.0
) -> str:
    """Analyze sentiment with optimization."""

    # Mock mode for testing without API calls
    if os.getenv("MOCK_MODE", "false").lower() == "true":
        text_lower = text.lower()
        if any(word in text_lower for word in ["fantastic", "best"]):
            result = "positive"
        elif any(word in text_lower for word in ["terrible", "worst"]):
            result = "negative"
        elif "bad but" in text_lower or "adequate" in text_lower:
            result = "mixed"
        else:
            result = "neutral"

        # For now, just return the string result
        # Token tracking for mock mode would need deeper integration
        # with the evaluation framework to work properly
        return result

    # Check for dry run mode
    if os.getenv("TRAIGENT_DRY_RUN", "false").lower() == "true":
        # In dry run, return mock results
        text_lower = text.lower()
        if any(word in text_lower for word in ["fantastic", "best"]):
            return "positive"
        elif any(word in text_lower for word in ["terrible", "worst"]):
            return "negative"
        elif "bad but" in text_lower or "adequate" in text_lower:
            return "mixed"
        else:
            return "neutral"

    # Real API call
    if not HAS_ANTHROPIC:
        raise ImportError("Install anthropic: pip install anthropic")

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not set. Please set it or use:\n"
            "  MOCK_MODE=true for mock mode\n"
            "  TRAIGENT_DRY_RUN=true for dry run mode"
        )

    # Build prompt
    prompt = f"""Analyze the sentiment of this text.
Consider sarcasm, context, and mixed feelings.

Text: "{text}"

Reply with ONE word: positive, negative, neutral, or mixed."""

    # Create cache key
    cache_key = create_llm_cache_key(
        prompt=prompt, model=model, temperature=temperature, max_tokens=10
    )

    # Check cache first
    llm_cache = _demo_cache._cache.get("llm_responses", {})
    if cache_key in llm_cache:
        print(f"💾 Cache hit for {model} (temp={temperature})")
        return llm_cache[cache_key]

    # Make API call
    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=10,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )

    result = response.content[0].text.strip().lower()

    # Cache the result
    if "llm_responses" not in _demo_cache._cache:
        _demo_cache._cache["llm_responses"] = {}
    _demo_cache._cache["llm_responses"][cache_key] = result
    _demo_cache.save()

    return result


async def main():
    """Run the demo."""

    print("\n" + "=" * 60)
    print("🚀 TraiGent: Basic Sentiment Analysis Tuning")
    print("=" * 60)

    # Show cache status
    llm_cache = _demo_cache._cache.get("llm_responses", {})
    print(f"💾 Cache status: {len(llm_cache)} cached LLM responses")

    # Ask user for mode preference
    print("\nHow would you like to run this demo?")
    print("1. Mock mode (no API calls, simulated results)")
    print("2. Real API mode (requires Anthropic API key, ~$0.07 cost)")
    if llm_cache:
        print("   💡 Cache hits will reduce actual API costs!")

    choice = input("\nEnter your choice (1 or 2): ").strip()

    if choice == "1":
        print("\n✅ Running in MOCK MODE - No API calls")
        os.environ["MOCK_MODE"] = "true"
        setup_mock_mode()
    elif choice == "2":
        print("\n💰 LIVE MODE - Real API calls")
        print("💰 Estimated cost: ~$0.07 (8 examples × 9 configs)")

        # Check if API key is available
        api_key_env = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key_env:
            print("\n⚠️  No ANTHROPIC_API_KEY found.")
            print(
                "Please enter your Anthropic API key (or press Enter to switch to mock mode):"
            )
            api_key = input().strip()

            if api_key:
                os.environ["ANTHROPIC_API_KEY"] = api_key
                print("✅ API key set for this session")
            else:
                print("✅ Switching to MOCK MODE")
                os.environ["MOCK_MODE"] = "true"
                setup_mock_mode()
        else:
            print("✅ Using existing ANTHROPIC_API_KEY")
    else:
        print("\n❌ Invalid choice. Running in MOCK MODE by default.")
        os.environ["MOCK_MODE"] = "true"
        setup_mock_mode()

    # Create dataset
    print("\n📊 Creating dataset...")
    dataset_path = await create_dataset()
    print("   8 sentiment examples created")

    # Test one example first
    test_text = "Oh great, another software update that breaks everything!"
    print(f"\n🧪 Testing: '{test_text}'")
    result = await analyze_sentiment(test_text)
    print(f"   Result: {result}")

    # Run optimization
    print("\n🔄 Running optimization...")
    print("   Testing 9 configurations (3 models × 3 temperatures)")

    # Set dataset and run
    analyze_sentiment.eval_dataset = dataset_path

    results = await analyze_sentiment.optimize(
        max_trials=9,
        callbacks=[DetailedProgressCallback()],
    )

    # Show results
    print("\n📈 Results:")
    print(f"   Best config: {results.best_config.get('model', 'Unknown')}")
    print(f"   Temperature: {results.best_config.get('temperature', 0.0)}")
    print(f"   Accuracy: {results.best_score:.2%}")

    # Note about accuracy
    if results.best_score <= 0.5:
        print("\n⚠️  Note: All models achieved similar accuracy (~50%)")
        print(
            "   This dataset is challenging - models struggle with sarcasm and mixed sentiment."
        )
        print("   In real use, you'd iterate on prompts or use more training data.")
    else:
        print("\n✅ Optimization found a better configuration!")

    # Cache statistics
    llm_cache = _demo_cache._cache.get("llm_responses", {})
    if llm_cache:
        print("\n💾 Cache Statistics:")
        print(f"   Cached LLM responses: {len(llm_cache)}")
        print(f"   Cache file: {_demo_cache.cache_file}")
        print("   💡 Cache hits reduce API costs for repeated runs!")

    # Cleanup
    Path(dataset_path).unlink(missing_ok=True)

    print("\n" + "=" * 60)
    print("✨ Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("\nUsage: python basic_sentiment_tuning.py")
        print("\nThis demo will ask you whether to run in:")
        print("  - Mock mode (no API calls, simulated results)")
        print("  - Real API mode (requires Anthropic API key)")
        print("\nNo environment variables required!")
        sys.exit(0)

    asyncio.run(main())
