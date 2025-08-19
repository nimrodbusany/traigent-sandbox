"""
Intelligent Mock OpenAI API patch for TraiGent demos.
This provides more realistic responses based on input content.
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


def get_intelligent_response(messages: List[Dict], model: str = "gpt-3.5-turbo") -> str:
    """Generate an intelligent mock response based on the input."""
    
    if not messages:
        return "general"
    
    # Get the last user message
    last_message = ""
    for msg in reversed(messages):
        if isinstance(msg, dict) and msg.get('role') == 'user':
            last_message = msg.get('content', '')
            break
    
    if not last_message:
        last_message = str(messages[-1]) if messages else ""
    
    # Convert to lowercase for analysis
    text_lower = last_message.lower()
    
    # Classification logic based on keywords
    if any(word in text_lower for word in ['billing', 'payment', 'invoice', 'charge', 'subscription', 'cost', 'price', 'refund']):
        return "billing"
    elif any(word in text_lower for word in ['password', 'login', 'error', 'bug', 'technical', 'reset', 'update', 'install', 'software']):
        return "technical"
    elif any(word in text_lower for word in ['feedback', 'suggestion', 'improve', 'feature', 'request']):
        return "feedback"
    elif any(word in text_lower for word in ['general', 'information', 'help', 'question', 'how', 'what']):
        return "general"
    
    # Default response based on common patterns
    if 'classify' in text_lower or 'category' in text_lower:
        # Return a deterministic classification based on text hash
        # This ensures consistency across trials
        categories = ['technical', 'billing', 'general', 'feedback']
        index = hash(last_message) % len(categories)
        return categories[index]
    
    return "general"


def patch_openai():
    """Patch OpenAI to use intelligent mock responses when in mock mode."""
    
    # Only patch if in mock mode
    if os.environ.get("TRAIGENT_MOCK_MODE", "").lower() != "true":
        return
    
    try:
        import openai
        from openai import OpenAI
        
        class MockOpenAI:
            """Mock OpenAI client that returns intelligent mock responses."""
            
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
                
                # Generate intelligent response
                mock_response = get_intelligent_response(messages, model)
                
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
        
        print("🔧 OpenAI patched with intelligent mock mode")
        
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
    
    print("✅ Intelligent mock environment configured")


# Auto-patch when imported in mock mode
if os.environ.get("TRAIGENT_MOCK_MODE", "").lower() == "true":
    patch_openai()