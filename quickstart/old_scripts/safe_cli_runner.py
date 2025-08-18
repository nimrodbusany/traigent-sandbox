#!/usr/bin/env python3
"""
Safe CLI Runner for TraiGent Benchmark Tool
Provides predefined configurations to avoid parameter validation issues
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print the application banner"""
    print("\n" + "=" * 60)
    print("   🎯 TraiGent CLI - Safe Configuration Runner")
    print("=" * 60)
    print()

def show_menu():
    """Show configuration menu"""
    print("Select a predefined configuration:")
    print()
    print("1. 🚀 Quick Test (5 examples, 2 parameters)")
    print("2. 📊 Basic Test (10 examples, 3 parameters)")
    print("3. 🔬 Advanced Test (15 examples, 5 parameters)")
    print("4. 🎮 Interactive Mode (manual configuration)")
    print("5. 📖 Show Help")
    print("6. ❌ Exit")
    print()
    
    while True:
        choice = input("Choice (1-6): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6']:
            return int(choice)
        print("Please enter a number between 1 and 6")

def get_config(choice):
    """Get configuration based on choice"""
    
    configs = {
        1: {  # Quick Test
            "name": "quick_test",
            "input": """2
quick_test
5
1
2
2
1
0
y
y
n
2
y
n
2
n
n
n
n
n
n
1
y
n
y
y
y
"""
        },
        2: {  # Basic Test
            "name": "basic_test",
            "input": """2
basic_test
10
1
3
3
2
2
y
y
n
2
y
n
2
y
n
2
n
n
n
n
n
n
1
y
n
y
y
y
"""
        },
        3: {  # Advanced Test
            "name": "advanced_test",
15
1
4
4
4
3
y
y
n
2
y
n
3
y
n
2
n
y
y
n
2
y
n
2
n
n
n
n
n
1
y
n
y
y
y
"""
        }
    }
    
    return configs.get(choice)

def run_cli_with_config(config):
    """Run the CLI with predefined configuration"""
    print(f"\n🔄 Running configuration: {config['name']}")
    print("-" * 40)
    
    # Create temporary input file
    input_file = Path("temp_input.txt")
    with open(input_file, 'w') as f:
        f.write(config['input'])
    
    # Run the CLI with input
    try:
        with open(input_file, 'r') as f:
            result = subprocess.run(
                [sys.executable, "traigent_benchmark_cli.py"],
                stdin=f,
                capture_output=False,
                text=True
            )
    finally:
        # Clean up temp file
        if input_file.exists():
            input_file.unlink()
    
    return result

def show_help():
    """Show help information"""
    print("\n📖 Help Information")
    print("=" * 60)
    print()
    print("This safe runner provides predefined configurations that avoid")
    print("common parameter validation issues:")
    print()
    print("• Quick Test: Minimal configuration for testing")
    print("  - 5 examples, 2 parameters (model + temperature)")
    print("  - Estimated time: < 1 minute")
    print()
    print("• Basic Test: Standard configuration")
    print("  - 10 examples, 3 parameters")
    print("  - Estimated time: 2-3 minutes")
    print()
    print("• Advanced Test: Comprehensive configuration")
    print("  - 15 examples, 5 parameters")
    print("  - Estimated time: 5-10 minutes")
    print()
    print("All configurations use MOCK MODE (no API costs)")
    print()
    print("Common Issues Avoided:")
    print("✅ Empty parameter lists")
    print("✅ Invalid value counts")
    print("✅ Missing required parameters")
    print()
    input("Press Enter to continue...")

def main():
    """Main application"""
    
    # Ensure we're in the right directory
    if not Path("traigent_benchmark_cli.py").exists():
        print("❌ Error: traigent_benchmark_cli.py not found")
        print("Please run this script from the quickstart directory")
        sys.exit(1)
    
    # Check for virtual environment
    if not Path("cli_venv").exists():
        print("⚠️  Virtual environment not found")
        print("Please run: python3 -m venv cli_venv")
        print("Then: source cli_venv/bin/activate")
        print("And: pip install openai pandas pyyaml")
        sys.exit(1)
    
    print_banner()
    
    while True:
        choice = show_menu()
        
        if choice == 6:  # Exit
            print("\n👋 Goodbye!")
            break
        elif choice == 5:  # Help
            show_help()
        elif choice == 4:  # Interactive
            print("\n🎮 Starting interactive mode...")
            print("Tip: Always use at least 1 value for each parameter!")
            print()
            subprocess.run([sys.executable, "traigent_benchmark_cli.py"])
        else:  # Predefined configs
            config = get_config(choice)
            if config:
                run_cli_with_config(config)
                print("\n✅ Configuration complete!")
                input("Press Enter to continue...")
        
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
        sys.exit(0)