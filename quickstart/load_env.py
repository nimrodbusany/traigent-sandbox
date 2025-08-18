"""Simple environment loader for TraiGent quickstart demos."""

import os
from pathlib import Path


def load_demo_env():
    """Load environment variables from .env file if it exists."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"Loading environment from: {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        # Force set the environment variable (override any existing)
                        os.environ[key] = value
                        if key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]:
                            # Show masked key for verification
                            masked_value = value[:8] + "..." if len(value) > 8 else "***"
                            print(f"  {key}={masked_value}")
                        else:
                            print(f"  {key}={value}")
    else:
        print(f"No .env file found at: {env_file}")
        print("Creating default mock mode .env file...")
        
        # Create default .env for mock mode
        with open(env_file, 'w') as f:
            f.write("""# TraiGent Mock Mode Configuration (No API Costs)
OPENAI_API_KEY=mock-key-for-demos
ANTHROPIC_API_KEY=mock-key-for-demos
TRAIGENT_EXECUTION_MODE=local
TRAIGENT_MOCK_MODE=true
""")
        
        # Load the created environment
        load_demo_env()


# Auto-load when imported
if __name__ != "__main__":
    load_demo_env()