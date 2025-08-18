#!/usr/bin/env python3
"""
Test that TraiGent is using the API key correctly
"""

import os
import sys
import json

# Set the environment variables
os.environ["TRAIGENT_API_KEY"] = "sk_n_8mXqLXt-eIpWeBpcOfoE8gfq44f1TMGYats_rQ-P4"
os.environ["TRAIGENT_BACKEND_URL"] = "http://localhost:5000"
os.environ["TRAIGENT_EXECUTION_MODE"] = "local"
os.environ["TRAIGENT_MOCK_MODE"] = "true"

print("=" * 60)
print("🔑 Testing TraiGent API Key Usage")
print("=" * 60)
print(f"TRAIGENT_API_KEY is set to: {os.environ.get('TRAIGENT_API_KEY')}")
print(f"TRAIGENT_BACKEND_URL is set to: {os.environ.get('TRAIGENT_BACKEND_URL')}")
print("=" * 60)

# Add Traigent to path
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/Traigent')

# Monkey-patch aiohttp to intercept and log requests
import aiohttp
original_request = aiohttp.ClientSession._request

async def logged_request(self, method, url, **kwargs):
    """Log all HTTP requests to see what's being sent"""
    print(f"\n📤 HTTP Request:")
    print(f"   Method: {method}")
    print(f"   URL: {url}")
    
    # Check for headers - they might be in different places
    headers = kwargs.get('headers', {})
    if not headers and hasattr(self, '_default_headers'):
        headers = dict(self._default_headers)
    
    if headers:
        print(f"   Headers:")
        for key, value in headers.items():
            if key.lower() == "authorization":
                # Show partial key for security
                value_str = str(value)
                if value_str.startswith("Bearer "):
                    token = value_str[7:]
                    print(f"      {key}: Bearer {token[:30]}...")
                else:
                    print(f"      {key}: {value_str[:30]}...")
            else:
                print(f"      {key}: {value}")
    else:
        print(f"   Headers: No headers found in request!")
        print(f"   kwargs keys: {list(kwargs.keys())}")
    
    # Call original method
    return await original_request(self, method, url, **kwargs)

# Apply the patch
aiohttp.ClientSession._request = logged_request

# Now import and use TraiGent
import traigent
import tempfile
import asyncio

# Create a simple test dataset
def create_test_dataset():
    examples = [
        {"input": {"text": "test1"}, "output": "result1"},
        {"input": {"text": "test2"}, "output": "result2"},
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for example in examples:
            json.dump(example, f)
            f.write('\n')
        return f.name

# Create a simple function to optimize
@traigent.optimize(
    eval_dataset=create_test_dataset(),
    objectives=["accuracy"],
    configuration_space={
        "model": ["gpt-3.5-turbo"],
        "temperature": [0.5]
    },
    max_trials=1,
    algorithm="grid",
    execution_mode="local"
)
def test_function(text: str, model: str = "gpt-3.5-turbo", temperature: float = 0.5) -> str:
    """Test function that returns a mock result"""
    return "mock_result"

# Run the optimization
async def run_test():
    print("\n🚀 Starting optimization...")
    print("This will show all HTTP requests made by TraiGent")
    print("-" * 60)
    
    try:
        results = await test_function.optimize()
        print("\n✅ Optimization completed!")
        print(f"Best config: {results.best_config}")
        print(f"Best score: {results.best_score:.1%}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

# Run the test
if __name__ == "__main__":
    asyncio.run(run_test())
    print("\n" + "=" * 60)
    print("✅ Test complete - check the logs above to see if the")
    print("   TRAIGENT_API_KEY was included in the Authorization header")
    print("=" * 60)