#!/usr/bin/env python3
"""
TraiGent Mock Wrapper - Ensures mock mode works properly
This wrapper intercepts and mocks all LLM calls when in mock mode
"""

import os
import sys
import random
from unittest.mock import Mock, patch
from typing import Any, Dict, List

# Force mock environment setup
os.environ["TRAIGENT_MOCK_MODE"] = "true"
os.environ["OPENAI_API_KEY"] = "mock-key-for-demos"
os.environ["ANTHROPIC_API_KEY"] = "mock-key-for-demos"
os.environ["TRAIGENT_EXECUTION_MODE"] = "local"

class MockLLMResponse:
    """Mock response that mimics OpenAI response structure"""
    def __init__(self, content: str):
        self.choices = [Mock(message=Mock(content=content))]
        self.usage = {"total_tokens": 10, "prompt_tokens": 5, "completion_tokens": 5}

def mock_openai_create(*args, **kwargs):
    """Mock OpenAI create method"""
    # Return random classification for demo
    classifications = ['technical', 'billing', 'general', 'feedback']
    return MockLLMResponse(random.choice(classifications))

def mock_anthropic_create(*args, **kwargs):
    """Mock Anthropic create method"""
    classifications = ['technical', 'billing', 'general', 'feedback']
    return Mock(content=[Mock(text=random.choice(classifications))])

# Patch OpenAI before any imports
with patch('openai.OpenAI') as mock_openai_class:
    mock_client = Mock()
    mock_client.chat.completions.create = mock_openai_create
    mock_openai_class.return_value = mock_client
    
    # Also patch the direct import
    sys.modules['openai'] = Mock(OpenAI=mock_openai_class)

# Now we can safely import and run the actual CLI
if __name__ == "__main__":
    # Import after patching
    from traigent_benchmark_cli import main
    
    print("🎭 Running in MOCK MODE - No API costs")
    print("=" * 50)
    
    # Run the CLI
    main()