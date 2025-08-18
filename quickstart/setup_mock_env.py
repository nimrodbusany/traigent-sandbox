#!/usr/bin/env python3
"""
Set up mock environment for TraiGent CLI
This ensures mock mode works without API key errors
"""

import os
import sys

def setup_mock_environment():
    """Configure environment for mock mode operation"""
    
    # Force all mock-related environment variables
    mock_env = {
        "TRAIGENT_MOCK_MODE": "true",
        "OPENAI_API_KEY": "sk-mock-key-for-testing-only",  # Use sk- prefix to look valid
        "ANTHROPIC_API_KEY": "sk-ant-mock-key-for-testing",  # Valid format
        "TRAIGENT_EXECUTION_MODE": "local",
        "TRAIGENT_BACKEND_URL": "http://localhost:5000",
        "TRAIGENT_RESULTS_FOLDER": "~/.traigent/results",
        # Disable API validation
        "OPENAI_API_KEY_VALIDATION": "false",
        "SKIP_API_KEY_CHECK": "true",
    }
    
    for key, value in mock_env.items():
        os.environ[key] = value
    
    print("✅ Mock environment configured:")
    for key, value in mock_env.items():
        if "KEY" in key:
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"  {key}={masked}")
        else:
            print(f"  {key}={value}")
    
    return True

if __name__ == "__main__":
    setup_mock_environment()
    
    # Now run the CLI with all arguments passed through
    from traigent_benchmark_cli import main
    sys.exit(main())