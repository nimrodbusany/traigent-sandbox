#!/usr/bin/env python3
"""
Run TraiGent CLI with predefined configurations
Usage: python run_with_config.py [quick|basic|advanced|custom]
"""

import sys
import subprocess

# Predefined configurations
CONFIGS = {
    "quick": {
        "name": "Quick Test (5 examples, 2 params)",
        "inputs": [
            "2",           # Guided Configuration
            "quick_test",  # Experiment name
            "5",           # Number of examples
            "1",           # Stratified sampling
            "2", "2", "1", "0",  # Difficulty distribution
            "y",           # Include Core LLM
            "y", "n", "2", # Model: yes, no custom, 2 values
            "y", "n", "2", # Temperature: yes, no custom, 2 values
            "n",           # Skip max_tokens
            "n",           # Skip top_p
            "n",           # Skip few-shot
            "n",           # Skip prompt engineering
            "n",           # Skip context/retrieval
            "1",           # Local execution
            "y",           # Mock mode
            "n",           # No early stopping
            "y",           # Proceed with config
            "y",           # Save configuration
            "y"            # Run now
        ]
    },
    "basic": {
        "name": "Basic Test (10 examples, 3 params)",
        "inputs": [
            "2",           # Guided Configuration
            "basic_test",  # Experiment name
            "10",          # Number of examples
            "1",           # Stratified sampling
            "3", "3", "2", "2",  # Difficulty distribution
            "y",           # Include Core LLM
            "y", "n", "2", # Model: yes, no custom, 2 values
            "y", "n", "2", # Temperature: yes, no custom, 2 values
            "y", "n", "2", # Max tokens: yes, no custom, 2 values
            "n",           # Skip top_p
            "n",           # Skip few-shot
            "n",           # Skip prompt engineering
            "n",           # Skip context/retrieval
            "1",           # Local execution
            "y",           # Mock mode
            "n",           # No early stopping
            "y",           # Proceed with config
            "y",           # Save configuration
            "y"            # Run now
        ]
    },
    "advanced": {
        "name": "Advanced Test (15 examples, 5+ params)",
        "inputs": [
            "2",           # Guided Configuration
            "advanced_test", # Experiment name
            "15",          # Number of examples
            "1",           # Stratified sampling
            "4", "4", "4", "3",  # Difficulty distribution
            "y",           # Include Core LLM
            "y", "n", "2", # Model: yes, no custom, 2 values
            "y", "n", "3", # Temperature: yes, no custom, 3 values
            "n",           # Skip max_tokens
            "n",           # Skip top_p
            "y",           # Include Few-Shot Learning
            "y", "n", "2", # Few-shot k: yes, no custom, 2 values
            "y", "n", "2", # Few-shot strategy: yes, no custom, 2 values
            "y",           # Include Prompt Engineering
            "y", "n", "2", # System role: yes, no custom, 2 values
            "y", "n", "2", # Output format: yes, no custom, 2 values
            "n",           # Skip response_style
            "n",           # Skip chain_of_thought
            "n",           # Skip context/retrieval
            "1",           # Local execution
            "y",           # Mock mode
            "n",           # No early stopping
            "y",           # Proceed with config
            "y",           # Save configuration
            "y"            # Run now
        ]
    },
    "custom": {
        "name": "Custom Configuration (you specify)",
        "inputs": []  # Will be filled by user
    }
}

def run_cli_with_inputs(inputs):
    """Run the CLI with predefined inputs"""
    # Join all inputs with newlines
    input_string = "\n".join(inputs)
    
    # Run the CLI with piped input
    process = subprocess.Popen(
        [sys.executable, "traigent_benchmark_cli.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Send input and get output
    output, _ = process.communicate(input=input_string)
    
    # Print the output
    print(output)
    
    return process.returncode

def main():
    """Main function"""
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        config_name = sys.argv[1].lower()
    else:
        # Show available configurations
        print("🎯 TraiGent CLI Runner")
        print("=" * 40)
        print("\nAvailable configurations:")
        for key, config in CONFIGS.items():
            print(f"  {key:10} - {config['name']}")
        print("\nUsage: python run_with_config.py [quick|basic|advanced|custom]")
        print("\nExample: python run_with_config.py quick")
        sys.exit(0)
    
    # Check if configuration exists
    if config_name not in CONFIGS:
        print(f"❌ Unknown configuration: {config_name}")
        print(f"Available: {', '.join(CONFIGS.keys())}")
        sys.exit(1)
    
    config = CONFIGS[config_name]
    
    # Handle custom configuration
    if config_name == "custom":
        print("📝 Enter your custom inputs (one per line, empty line to finish):")
        inputs = []
        while True:
            line = input()
            if line == "":
                break
            inputs.append(line)
        config["inputs"] = inputs
    
    # Run the CLI
    print(f"\n🚀 Running: {config['name']}")
    print("=" * 40)
    
    return_code = run_cli_with_inputs(config["inputs"])
    
    if return_code == 0:
        print("\n✅ Configuration completed successfully!")
    else:
        print(f"\n⚠️  Configuration exited with code: {return_code}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)