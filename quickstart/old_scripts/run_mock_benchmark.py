#!/usr/bin/env python3
"""
Run TraiGent benchmark in proper mock mode with auth fix
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

# Apply the auth fix for TraiGent backend
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
                    print(f"✅ Added TraiGent auth to {method} {url}")
        return await original_request(method, url, **kwargs)
    
    self._request = request_with_auth

aiohttp.ClientSession.__init__ = patched_session_init

# Now apply the OpenAI mock patch PROPERLY
def setup_mock_openai():
    """Properly mock OpenAI to avoid API calls"""
    try:
        import openai
        from unittest.mock import MagicMock, AsyncMock
        
        # Create a mock response
        def create_mock_response(model="gpt-3.5-turbo", content="Mock response", **kwargs):
            """Create a mock ChatCompletion response"""
            from types import SimpleNamespace
            
            # Create a proper mock response structure
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
        
        # Store original
        original_create = None
        if hasattr(openai.chat.completions, 'create'):
            original_create = openai.chat.completions.create
        
        # Create mock function
        def mock_create(**kwargs):
            """Mock OpenAI create function"""
            model = kwargs.get('model', 'gpt-3.5-turbo')
            print(f"🎭 Mock OpenAI call: {model}")
            return create_mock_response(model=model)
        
        async def mock_acreate(**kwargs):
            """Mock async OpenAI create function"""
            return mock_create(**kwargs)
        
        # Apply the mock
        openai.chat.completions.create = mock_create
        openai.chat.completions.acreate = mock_acreate
        
        # Also mock the client if it exists
        if hasattr(openai, 'OpenAI'):
            original_client = openai.OpenAI
            
            class MockOpenAI:
                def __init__(self, *args, **kwargs):
                    self.chat = SimpleNamespace()
                    self.chat.completions = SimpleNamespace()
                    self.chat.completions.create = mock_create
                    self.chat.completions.acreate = mock_acreate
            
            openai.OpenAI = MockOpenAI
        
        print("✅ OpenAI mocked successfully - no API calls will be made")
        return True
        
    except Exception as e:
        print(f"⚠️ Could not mock OpenAI: {e}")
        return False

# Apply OpenAI mock
setup_mock_openai()

# Now we can import traigent
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
    max_trials=6,
    algorithm="grid",
    execution_mode="local"
)
def benchmark_function(text: str, model: str = "gpt-3.5-turbo", temperature: float = 0.5) -> str:
    """Function to optimize"""
    # In mock mode, just return a fixed response
    return f"Mock response for {text}"

async def run_benchmark():
    """Run the benchmark"""
    print("\n" + "="*60)
    print("🚀 Running Mock Benchmark with Auth Fix")
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
        print(f"Total trials: {len(results.history)}")
        print("="*60)
        
        # Show first few results
        print("\n📊 Sample Results:")
        for i, trial in enumerate(results.history[:3]):
            print(f"  Trial {i+1}: {trial.config} -> {trial.score:.1%}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the benchmark
    asyncio.run(run_benchmark())