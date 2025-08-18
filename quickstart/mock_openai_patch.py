"""
Mock OpenAI API patch for TraiGent demos.
This patches the OpenAI client to return mock responses instead of making real API calls.
"""

import os
import random
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class MockChoice:
    """Mock choice object for OpenAI responses."""
    index: int
    message: Any
    finish_reason: str = "stop"


@dataclass  
class MockMessage:
    """Mock message object for OpenAI responses."""
    content: str
    role: str = "assistant"


@dataclass
class MockCompletion:
    """Mock completion object for OpenAI responses."""
    id: str = "mock-completion-id"
    object: str = "chat.completion"
    created: int = 1234567890
    model: str = "gpt-3.5-turbo"
    choices: List[MockChoice] = None
    usage: Dict[str, int] = None
    
    def __post_init__(self):
        if self.choices is None:
            self.choices = []
        if self.usage is None:
            self.usage = {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }


def patch_openai():
    """Patch OpenAI to use mock responses when in mock mode."""
    
    # Only patch if in mock mode
    if os.environ.get("TRAIGENT_MOCK_MODE", "").lower() != "true":
        return
    
    try:
        import openai
        from openai import OpenAI
        
        # Store original client class
        original_client = OpenAI
        
        class MockOpenAI:
            """Mock OpenAI client that returns mock responses."""
            
            def __init__(self, *args, **kwargs):
                # Accept any initialization parameters
                self.api_key = kwargs.get('api_key', 'mock-key')
                self.chat = self
                self.completions = self
            
            def create(self, *args, **kwargs):
                """Mock create method for chat completions."""
                # Extract parameters
                messages = kwargs.get('messages', [])
                model = kwargs.get('model', 'gpt-3.5-turbo')
                
                # Generate mock response based on the task
                # For classification tasks, return random classification
                classifications = ['technical', 'billing', 'general', 'feedback']
                mock_response = random.choice(classifications)
                
                # Check if this looks like a classification task
                if messages:
                    last_message = messages[-1].get('content', '') if isinstance(messages[-1], dict) else str(messages[-1])
                    if 'classify' in last_message.lower() or 'category' in last_message.lower():
                        mock_response = random.choice(classifications)
                    else:
                        # Generic response
                        mock_response = f"Mock response for {model}"
                
                # Return mock completion
                return MockCompletion(
                    model=model,
                    choices=[
                        MockChoice(
                            index=0,
                            message=MockMessage(content=mock_response)
                        )
                    ]
                )
        
        # Monkey patch the OpenAI class
        openai.OpenAI = MockOpenAI
        
        # Also patch the client if it's already imported
        if hasattr(openai, 'ChatCompletion'):
            openai.ChatCompletion.create = lambda **kwargs: MockOpenAI().create(**kwargs)
        
        print("🔧 OpenAI patched for mock mode")
        
    except ImportError:
        # OpenAI not installed or not imported yet
        pass


def setup_mock_environment():
    """Set up complete mock environment for TraiGent demos."""
    
    # Set environment variables
    os.environ["TRAIGENT_MOCK_MODE"] = "true"
    os.environ["OPENAI_API_KEY"] = "mock-key-for-demos"
    os.environ["ANTHROPIC_API_KEY"] = "mock-key-for-demos"
    os.environ["TRAIGENT_EXECUTION_MODE"] = "local"
    
    # Patch OpenAI
    patch_openai()
    
    print("✅ Mock environment configured - no API costs will be incurred")


# Auto-patch when imported in mock mode
if os.environ.get("TRAIGENT_MOCK_MODE", "").lower() == "true":
    patch_openai()