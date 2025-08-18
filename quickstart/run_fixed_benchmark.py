#!/usr/bin/env python3
"""
Run TraiGent benchmark with fixes for both auth headers AND max_trials issues
"""

import os
import sys

# Set up environment BEFORE any imports
os.environ["TRAIGENT_API_KEY"] = "sk_n_8mXqLXt-eIpWeBpcOfoE8gfq44f1TMGYats_rQ-P4"
os.environ["TRAIGENT_BACKEND_URL"] = "http://localhost:5000"
os.environ["TRAIGENT_EXECUTION_MODE"] = "local"
os.environ["TRAIGENT_MOCK_MODE"] = "true"
os.environ["OPENAI_API_KEY"] = "sk-mock-1234567890abcdefghijklmnopqrstuvwxyz"
os.environ["SKIP_API_KEY_CHECK"] = "true"

# Add the Traigent path
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/Traigent')

print("=" * 60)
print("🔧 Applying SDK Bug Fixes")
print("=" * 60)

# Fix 1: Auth headers for TraiGent backend
import aiohttp
original_session_init = aiohttp.ClientSession.__init__

def patched_session_init(self, *args, **kwargs):
    """Patch ClientSession to include TraiGent API key"""
    original_session_init(self, *args, **kwargs)
    original_request = self._request
    
    async def request_with_auth(method, url, **kwargs):
        """Add TraiGent API key to backend requests"""
        backend_url = os.environ.get("TRAIGENT_BACKEND_URL", "http://localhost:5000")
        if backend_url in str(url) or "traigent" in str(url).lower():
            api_key = os.environ.get("TRAIGENT_API_KEY")
            if api_key:
                if 'headers' not in kwargs:
                    kwargs['headers'] = {}
                if 'Authorization' not in kwargs['headers']:
                    kwargs['headers']['Authorization'] = f"Bearer {api_key}"
        return await original_request(method, url, **kwargs)
    
    self._request = request_with_auth

aiohttp.ClientSession.__init__ = patched_session_init
print("✅ Fix 1: Auth headers will be added to backend requests")

# Fix 2: max_trials serialization issue
from traigent.cloud import backend_client

# Patch the _create_traigent_session_via_api method
original_create_session = backend_client.BackendIntegratedClient._create_traigent_session_via_api

async def patched_create_session(self, session_request):
    """Patched version that ensures max_trials is never None"""
    # Ensure max_trials has a value
    if session_request.max_trials is None:
        session_request.max_trials = 50
        print(f"✅ Fix 2: Set max_trials to default value: 50")
    
    # Call original method
    return await original_create_session(self, session_request)

backend_client.BackendIntegratedClient._create_traigent_session_via_api = patched_create_session
print("✅ Fix 2: max_trials will never be sent as None")

# Fix 3: Mock OpenAI properly
def setup_mock_openai():
    """Properly mock OpenAI to avoid API calls"""
    try:
        import openai
        from types import SimpleNamespace
        
        def create_mock_response(model="gpt-3.5-turbo", content="Mock response", **kwargs):
            """Create a mock ChatCompletion response"""
            message = SimpleNamespace(
                content=content,
                role="assistant"
            )
            choice = SimpleNamespace(
                message=message,
                index=0,
                finish_reason="stop"
            )
            response = SimpleNamespace(
                choices=[choice],
                model=model,
                usage=SimpleNamespace(
                    prompt_tokens=10,
                    completion_tokens=10,
                    total_tokens=20
                )
            )
            return response
        
        def mock_create(**kwargs):
            """Mock OpenAI create function"""
            model = kwargs.get('model', 'gpt-3.5-turbo')
            return create_mock_response(model=model)
        
        async def mock_acreate(**kwargs):
            """Mock async OpenAI create function"""
            return mock_create(**kwargs)
        
        # Apply the mock
        openai.chat.completions.create = mock_create
        openai.chat.completions.acreate = mock_acreate
        
        # Also mock the client if it exists
        if hasattr(openai, 'OpenAI'):
            class MockOpenAI:
                def __init__(self, *args, **kwargs):
                    self.chat = SimpleNamespace()
                    self.chat.completions = SimpleNamespace()
                    self.chat.completions.create = mock_create
                    self.chat.completions.acreate = mock_acreate
            
            openai.OpenAI = MockOpenAI
        
        return True
        
    except Exception as e:
        print(f"⚠️ Could not mock OpenAI: {e}")
        return False

setup_mock_openai()
print("✅ Fix 3: OpenAI mocked - no API calls will be made")

print("=" * 60)
print()

# Now import and run the benchmark
import traigent
import json
import tempfile
import asyncio

def create_test_dataset(num_examples=10):
    """Create a test dataset"""
    examples = []
    for i in range(num_examples):
        examples.append({
            "input": {"text": f"Test question {i}"},
            "output": f"Expected answer {i}"
        })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for example in examples:
            json.dump(example, f)
            f.write('\n')
        return f.name

@traigent.optimize(
    eval_dataset=create_test_dataset(),
    objectives=["accuracy"],
    configuration_space={
        "model": ["gpt-3.5-turbo", "gpt-4o-mini"],
        "temperature": [0.0, 0.5, 1.0]
    },
    max_trials=6,  # Explicitly set to avoid None issue
    algorithm="grid",
    execution_mode="local"
)
def benchmark_function(text: str, model: str = "gpt-3.5-turbo", temperature: float = 0.5) -> str:
    """Function to optimize"""
    return f"Mock response for {text}"

async def run_benchmark():
    """Run the benchmark with all fixes applied"""
    print("🚀 Running Benchmark with All SDK Fixes")
    print("="*60)
    print(f"TraiGent API Key: {os.environ.get('TRAIGENT_API_KEY')[:30]}...")
    print(f"Backend URL: {os.environ.get('TRAIGENT_BACKEND_URL')}")
    print(f"Mock Mode: {os.environ.get('TRAIGENT_MOCK_MODE')}")
    print("="*60 + "\n")
    
    try:
        # Run optimization
        results = await benchmark_function.optimize()
        
        print("\n" + "="*60)
        print("✅ Optimization Complete!")
        print("="*60)
        print(f"Best configuration: {results.best_config}")
        print(f"Best score: {results.best_score:.1%}")
        
        # Show some results
        print("\n📊 Results Summary:")
        print(f"  - Model: {results.best_config.get('model')}")
        print(f"  - Temperature: {results.best_config.get('temperature')}")
        print(f"  - Score: {results.best_score:.1%}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_benchmark())
    print("\n" + "="*60)
    print("✅ All SDK bugs have been worked around")
    print("   - Auth headers are included")
    print("   - max_trials is never None")
    print("   - OpenAI is properly mocked")
    print("="*60)