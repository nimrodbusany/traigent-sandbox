#!/usr/bin/env python3
"""
Run TraiGent optimization in true mock mode
This script ensures no real API calls are made
"""

import os
import sys
import json
import random
from unittest.mock import Mock, patch

# Force all mock environment variables
os.environ["TRAIGENT_MOCK_MODE"] = "true"
os.environ["OPENAI_API_KEY"] = "sk-mock-test-key"
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-mock-test-key"
os.environ["TRAIGENT_EXECUTION_MODE"] = "local"
os.environ["TRAIGENT_API_KEY"] = "sk_n_8mXqLXt-eIpWeBpcOfoE8gfq44f1TMGYats_rQ-P4"
os.environ["TRAIGENT_BACKEND_URL"] = "http://localhost:5000"

# Print to verify the key is set
print("🔑 TRAIGENT_API_KEY is set to:", os.environ.get("TRAIGENT_API_KEY"))
print("🌐 TRAIGENT_BACKEND_URL is set to:", os.environ.get("TRAIGENT_BACKEND_URL"))
print("✅ TRAIGENT_MOCK_MODE is set to:", os.environ.get("TRAIGENT_MOCK_MODE"))

# Mock the OpenAI module BEFORE any imports
mock_openai = Mock()
mock_client = Mock()

# Create mock response
def create_mock_response(*args, **kwargs):
    """Create a mock OpenAI response"""
    classifications = ['technical', 'billing', 'general', 'feedback']
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = random.choice(classifications)
    return mock_response

# Set up the mock client
mock_client.chat.completions.create = create_mock_response
mock_openai.OpenAI = Mock(return_value=mock_client)
mock_openai.ChatCompletion = Mock()
mock_openai.ChatCompletion.create = create_mock_response

# Patch the openai module
sys.modules['openai'] = mock_openai

# Now we can safely import everything else
import traigent
import tempfile
from pathlib import Path

def create_test_dataset(num_examples=10):
    """Create a test dataset for optimization"""
    examples = [
        {"input": {"text": "My app crashes when I upload files"}, "output": "technical"},
        {"input": {"text": "I was charged twice"}, "output": "billing"},
        {"input": {"text": "How do I reset my password?"}, "output": "general"},
        {"input": {"text": "Great product!"}, "output": "feedback"},
        {"input": {"text": "Login page shows error"}, "output": "technical"},
        {"input": {"text": "Cancel my subscription"}, "output": "billing"},
        {"input": {"text": "What are your hours?"}, "output": "general"},
        {"input": {"text": "This needs improvement"}, "output": "feedback"},
        {"input": {"text": "API returns 500 error"}, "output": "technical"},
        {"input": {"text": "Refund request"}, "output": "billing"},
    ]
    
    # Create JSONL file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for example in examples[:num_examples]:
            json.dump(example, f)
            f.write('\n')
        return f.name

def run_mock_optimization():
    """Run a mock optimization with TraiGent"""
    
    print("🎯 TraiGent Mock Optimization Demo")
    print("=" * 50)
    print("✅ Mock mode enabled - no API costs")
    print("✅ Using TraiGent API key for telemetry")
    print()
    
    # Create test dataset
    dataset_file = create_test_dataset(10)
    print(f"📊 Created test dataset: {dataset_file}")
    
    # Define configuration space
    config_space = {
        "model": ["gpt-3.5-turbo", "gpt-4o-mini"],
        "temperature": [0.0, 0.5, 1.0],
        "max_tokens": [50, 100]
    }
    
    total_combinations = len(config_space["model"]) * len(config_space["temperature"]) * len(config_space["max_tokens"])
    print(f"🔧 Configuration space: {total_combinations} combinations")
    for param, values in config_space.items():
        print(f"   • {param}: {values}")
    
    print(f"\n🚀 Starting optimization...")
    print("=" * 50)
    
    # Create optimized function
    @traigent.optimize(
        eval_dataset=dataset_file,
        objectives=["accuracy"],
        configuration_space=config_space,
        max_trials=total_combinations,
        algorithm="grid",
        execution_mode="local",
        minimal_logging=True
    )
    def classify_text(text: str, model: str = "gpt-3.5-turbo", temperature: float = 0.5, max_tokens: int = 50) -> str:
        """Classify customer support text (mocked)"""
        # This would normally call OpenAI, but our mock intercepts it
        client = mock_openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": "Classify the text as: technical, billing, general, or feedback"},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    
    # Run optimization
    try:
        import asyncio
        
        async def optimize():
            results = await classify_text.optimize()
            return results
        
        results = asyncio.run(optimize())
        
        print("\n✅ Optimization Complete!")
        print("=" * 50)
        print(f"Best configuration found:")
        for key, value in results.best_config.items():
            print(f"  • {key}: {value}")
        print(f"\nBest score: {results.best_score:.1%}")
        
        # Show all trials
        if hasattr(results, 'trials') and len(results.trials) > 1:
            print(f"\n📊 All {len(results.trials)} trials completed successfully")
            
    except Exception as e:
        print(f"\n❌ Error during optimization: {e}")
        import traceback
        traceback.print_exc()
    
    # Clean up
    try:
        os.unlink(dataset_file)
    except:
        pass
    
    print("\n✨ Demo complete!")

if __name__ == "__main__":
    run_mock_optimization()