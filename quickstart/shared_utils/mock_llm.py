"""Mock LLM utilities for TraiGent examples."""

import os


def setup_mock_mode() -> bool:
    """
    Setup mock mode for TraiGent examples.

    This sets the TRAIGENT_MOCK_MODE environment variable to enable
    mock mode in examples, which saves API costs during demonstrations.

    Returns:
        True if mock mode was activated
    """
    # Enable TraiGent's built-in mock mode
    os.environ["TRAIGENT_MOCK_MODE"] = "true"
    
    # Check if we have real API keys already
    current_openai = os.environ.get("OPENAI_API_KEY", "")
    current_anthropic = os.environ.get("ANTHROPIC_API_KEY", "")
    
    # Only set mock keys if NO keys are present (preserve real keys)
    if not current_openai:
        # Only set a mock key if there's no key at all
        os.environ["OPENAI_API_KEY"] = "sk-mock-traigent-placeholder"
    
    if not current_anthropic:
        # Only set a mock key if there's no key at all  
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-mock-traigent-placeholder"
    
    # Set execution mode to local for mock
    os.environ["TRAIGENT_EXECUTION_MODE"] = "local"
    
    print("✅ TraiGent mock mode activated - no API costs will be incurred")
    print("   TraiGent will handle all mocking internally")
    return True


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string.

    This is a simple approximation used for mock mode.
    Real token counting would require the actual tokenizer.

    Args:
        text: The text to estimate tokens for

    Returns:
        Estimated number of tokens
    """
    # Simple approximation: 1 token per 4 characters
    # Return 0 for empty strings
    if not text:
        return 0
    return max(1, len(text) // 4)


def get_mock_response(prompt: str, model: str = "gpt-3.5-turbo") -> dict:
    """
    Generate a mock response for LLM calls.

    Args:
        prompt: The input prompt
        model: The model name

    Returns:
        Mock response dictionary
    """
    return {
        "response": f"Mock response for: {prompt[:50]}...",
        "model": model,
        "tokens": estimate_tokens(prompt),
        "cost": 0.0,
        "mock_mode": True
    }
