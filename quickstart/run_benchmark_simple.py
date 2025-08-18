#!/usr/bin/env python3
"""
Simple benchmark runner using TraiGent's dry run mode
This avoids all API key issues by using TraiGent's built-in mocking
"""

import os
import sys
import json
import tempfile
import asyncio

# Set environment for dry run mode
os.environ["TRAIGENT_API_KEY"] = "sk_n_8mXqLXt-eIpWeBpcOfoE8gfq44f1TMGYats_rQ-P4"
os.environ["TRAIGENT_BACKEND_URL"] = "http://localhost:5000"
os.environ["TRAIGENT_EXECUTION_MODE"] = "local"

# Add paths
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/Traigent')
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/quickstart')

# Apply the auth and max_trials fixes
import aiohttp

original_session_init = aiohttp.ClientSession.__init__

def patched_session_init(self, *args, **kwargs):
    """Patch ClientSession to include TraiGent API key"""
    original_session_init(self, *args, **kwargs)
    original_request = self._request
    
    async def request_with_auth(method, url, **kwargs):
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

# Import TraiGent
import traigent

def create_dataset(num_examples=10):
    """Create a simple test dataset"""
    examples = []
    for i in range(num_examples):
        examples.append({
            "input": {"text": f"Question {i}: What is the capital of France?"},
            "output": "Paris"
        })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for example in examples:
            json.dump(example, f)
            f.write('\n')
        return f.name

async def run_benchmark():
    """Run a simple benchmark with dry run mode"""
    print("=" * 60)
    print("🚀 Running TraiGent Benchmark (Dry Run Mode)")
    print("=" * 60)
    
    # Create a simple function to optimize
    # Use dry_run=True to avoid API calls
    @traigent.optimize(
        eval_dataset=create_dataset(5),  # Small dataset for testing
        objectives=["accuracy"],
        configuration_space={
            "model": ["gpt-3.5-turbo", "gpt-4o-mini"],
            "temperature": [0.0, 0.5, 1.0]
        },
        max_trials=6,
        algorithm="grid",
        execution_mode="local",
        dry_run=True  # This enables TraiGent's built-in dry run mode
    )
    def test_function(text: str, model: str = "gpt-3.5-turbo", temperature: float = 0.5) -> str:
        """Simple test function"""
        # In dry run mode, this won't actually call any LLM
        return "Paris"  # Mock response
    
    try:
        # Run the optimization
        results = await test_function.optimize()
        
        print("\n✅ Optimization Complete!")
        print("=" * 60)
        print(f"Best configuration found:")
        print(f"  Model: {results.best_config.get('model')}")
        print(f"  Temperature: {results.best_config.get('temperature')}")
        print(f"  Score: {results.best_score:.1%}")
        print("=" * 60)
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("\n🔧 TraiGent Simple Benchmark Runner")
    print("=" * 60)
    print("This script uses TraiGent's dry run mode to avoid API issues")
    print("No actual API calls will be made")
    print("=" * 60)
    
    # Parse simple command line arguments if provided
    if len(sys.argv) > 1:
        # Allow passing configuration as arguments
        # Example: python run_benchmark_simple.py "model=['gpt-3.5-turbo','gpt-4o']" "temperature=[0.3,0.7]"
        config_space = {}
        for arg in sys.argv[1:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                try:
                    # Evaluate the value as Python literal
                    config_space[key] = eval(value)
                except:
                    config_space[key] = value
        
        if config_space:
            print(f"\nUsing custom configuration space:")
            for key, value in config_space.items():
                print(f"  {key}: {value}")
            
            # Create custom optimized function
            @traigent.optimize(
                eval_dataset=create_dataset(5),
                objectives=["accuracy"],
                configuration_space=config_space,
                max_trials=min(50, len(config_space) * 10),  # Reasonable max
                algorithm="grid",
                execution_mode="local",
                dry_run=True
            )
            def custom_function(text: str, **kwargs) -> str:
                return "Paris"
            
            async def run_custom():
                return await custom_function.optimize()
            
            results = asyncio.run(run_custom())
        else:
            results = asyncio.run(run_benchmark())
    else:
        results = asyncio.run(run_benchmark())
    
    if results:
        print("\n✅ Benchmark completed successfully!")
    else:
        print("\n⚠️ Benchmark failed - check the errors above")