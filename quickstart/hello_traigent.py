#!/usr/bin/env python3
"""TraiGent Hello World - Your first optimization in 50 lines!"""

import json
import sys
import tempfile
from pathlib import Path

# Setup imports to work when run directly
try:
    # Try relative import first (when run as module)
    from import_helper import load_demo_env, setup_example_imports
    setup_example_imports()
    from shared_utils.caching import create_llm_cache_key, setup_demo_cache
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

    # Try to import caching utilities
    try:
        from shared_utils.caching import create_llm_cache_key, setup_demo_cache
    except ImportError:
        # Minimal fallback implementations
        def create_llm_cache_key(**kwargs):
            return f"cache_{hash(str(sorted(kwargs.items())))}"

        class MockCache:
            def __init__(self, name):
                self._cache = {}
            def save(self):
                pass

        def setup_demo_cache(name):
            return MockCache(name)

from anthropic import Anthropic

import traigent

# Load environment variables from .env file
load_demo_env()

# Import shared utilities for caching

# Initialize demo cache
_demo_cache = setup_demo_cache("hello-world")


# Create a simple evaluation dataset
def create_dataset() -> str:
    data = [
        {"input": {"text": "This product is amazing!"}, "output": "positive"},
        {
            "input": {"text": "Terrible service, very disappointed"},
            "output": "negative",
        },
        {"input": {"text": "It's okay, nothing special"}, "output": "neutral"},
        {"input": {"text": "Best purchase ever!"}, "output": "positive"},
        {"input": {"text": "Waste of money"}, "output": "negative"},
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for item in data:
            json.dump(item, f)
            f.write("\n")
        return f.name


# Original function - uses cheapest model
def analyze_sentiment_basic(text: str) -> str:
    """Basic sentiment analysis with Haiku (cheap but less accurate)"""
    # Cache parameters
    model = "claude-3-haiku-20240307"
    temperature = 0.0
    max_tokens = 10
    prompt = f"Sentiment of '{text}': positive, negative, or neutral?"

    # Create cache key
    cache_key = create_llm_cache_key(
        prompt=prompt, model=model, temperature=temperature, max_tokens=max_tokens
    )

    # Check cache first
    llm_cache = _demo_cache._cache.get("llm_responses", {})
    if cache_key in llm_cache:
        print("💾 Cache hit for basic function")
        return llm_cache[cache_key]

    # Make API call
    client = Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.content[0]
    if hasattr(content, "text"):
        result = content.text.strip().lower()
    else:
        result = str(content).strip().lower()

    # Cache the result
    if "llm_responses" not in _demo_cache._cache:
        _demo_cache._cache["llm_responses"] = {}
    _demo_cache._cache["llm_responses"][cache_key] = result
    _demo_cache.save()

    return result


# Same function with TraiGent optimization - finds the best model!
@traigent.optimize(
    eval_dataset=create_dataset(),
    objectives=["accuracy"],
    configuration_space={
        "model": ["claude-3-haiku-20240307", "claude-3-5-sonnet-20241022"],
        "temperature": [0.0, 0.3],
    },
    execution_mode="cloud",  # Use cloud execution mode
)
def analyze_sentiment_optimized(text: str) -> str:
    """TraiGent automatically finds the best model for accuracy!"""
    # These will be injected by TraiGent during optimization
    model = "claude-3-haiku-20240307"  # TraiGent will override this!
    temperature = 0.0  # TraiGent will override this too!
    max_tokens = 10
    prompt = f"Sentiment of '{text}': positive, negative, or neutral?"

    # Create cache key including all parameters that affect the result
    cache_key = create_llm_cache_key(
        prompt=prompt, model=model, temperature=temperature, max_tokens=max_tokens
    )

    # Check cache first
    llm_cache = _demo_cache._cache.get("llm_responses", {})
    if cache_key in llm_cache:
        print(f"💾 Cache hit for optimized function ({model})")
        return llm_cache[cache_key]

    # Make API call
    client = Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.content[0]
    if hasattr(content, "text"):
        result = content.text.strip().lower()
    else:
        result = str(content).strip().lower()

    # Cache the result
    if "llm_responses" not in _demo_cache._cache:
        _demo_cache._cache["llm_responses"] = {}
    _demo_cache._cache["llm_responses"][cache_key] = result
    _demo_cache.save()

    return result


if __name__ == "__main__":
    print("🚀 TraiGent Hello World - Sentiment Analysis\n")

    # Show cache status
    llm_cache = _demo_cache._cache.get("llm_responses", {})
    print(f"💾 Cache status: {len(llm_cache)} cached responses\n")

    test = "This framework saves me so much time!"
    print(f"Analyzing: '{test}'")
    print(f"Basic:     {analyze_sentiment_basic(test)}")
    print(f"Optimized: {analyze_sentiment_optimized(test)}")

    # Show updated cache status
    llm_cache_after = _demo_cache._cache.get("llm_responses", {})
    new_entries = len(llm_cache_after) - len(llm_cache)
    if new_entries > 0:
        print(f"\n💾 Cache updated: +{new_entries} new responses cached")

    print("\n✨ TraiGent automatically selects the best model for YOUR data!")
    print("💡 LLM responses are cached to avoid duplicate API calls and reduce costs!")
