#!/usr/bin/env python3
"""
Demonstration script for TraiGent CLI Benchmark Tool
Shows programmatic usage and configuration examples
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import CLI components
from traigent_benchmark_cli import (
    TraiGentBenchmarkCLI,
    ParameterRegistry,
    DatasetLoader,
    ExampleSelector,
    PromptBuilder,
    ParameterConfig,
    ExperimentConfig
)

def demonstrate_cli_components():
    """Demonstrate individual CLI components"""
    
    print("🎯 TraiGent CLI Components Demonstration")
    print("=" * 50)
    print()
    
    # 1. Parameter Registry
    print("1️⃣ Parameter Registry:")
    registry = ParameterRegistry()
    categories = registry.get_categories()
    
    for category, params in categories.items():
        print(f"   {category}: {', '.join(params)}")
    print()
    
    # 2. Dataset Loader
    print("2️⃣ Dataset Loader:")
    loader = DatasetLoader("support_classification_dataset.json")
    
    print(f"   Total examples: {len(loader.dataset['examples'])}")
    print(f"   Categories: {loader.dataset['metadata']['categories']}")
    print(f"   Difficulties: {loader.dataset['metadata']['difficulty_levels']}")
    
    # Sample examples
    sampled = loader.sample_examples(5, strategy="stratified")
    print(f"   Sampled 5 stratified examples")
    print()
    
    # 3. Prompt Builder
    print("3️⃣ Prompt Builder:")
    prompt_builder = PromptBuilder()
    
    messages = prompt_builder.build_messages(
        text="My app crashes when uploading files",
        system_role="classifier",
        output_format="single_word",
        style="concise",
        few_shot_examples=None,
        chain_of_thought=False
    )
    
    print(f"   Built message with {len(messages)} parts")
    print(f"   System message: {messages[0]['content'][:100]}...")
    print()
    
    # 4. Example Selector
    print("4️⃣ Example Selector:")
    selector = ExampleSelector(loader.dataset['examples'])
    
    few_shot_examples = selector.select_examples(
        k=3,
        strategy="diverse"
    )
    
    print(f"   Selected {len(few_shot_examples)} diverse examples")
    for ex in few_shot_examples[:2]:
        print(f"   • {ex['input']['text'][:50]}... → {ex['output']}")
    print()

def create_mock_configuration():
    """Create a mock mode configuration programmatically"""
    
    print("📝 Creating Mock Mode Configuration")
    print("=" * 50)
    
    # Define parameters
    parameters = {
        "model": ParameterConfig(
            name="model",
            param_type="categorical",
            values=["gpt-3.5-turbo", "gpt-4o-mini"],
            enabled=True,
            description="LLM model to use"
        ),
        "temperature": ParameterConfig(
            name="temperature",
            param_type="continuous",
            values=[0.0, 0.5],
            enabled=True,
            description="Sampling temperature"
        ),
        "few_shot_k": ParameterConfig(
            name="few_shot_k",
            param_type="discrete",
            values=[0, 1, 3],
            enabled=True,
            description="Number of few-shot examples"
        )
    }
    
    # Create configuration
    config = ExperimentConfig(
        name="demo_mock_test",
        dataset={
            "total_examples": 10,
            "sampling_strategy": "stratified",
            "difficulty_distribution": {
                "easy": 3,
                "medium": 3,
                "hard": 2,
                "expert": 2
            }
        },
        parameters=parameters,
        execution={
            "mode": "local",
            "mock_mode": True,
            "early_stopping": False,
            "algorithm": "grid",
            "max_trials": 12  # 2 models × 2 temps × 3 few_shot = 12
        },
        output={
            "save_results": True,
            "export_formats": ["json"],
            "create_visualizations": False
        }
    )
    
    print(f"✅ Configuration created: {config.name}")
    print(f"   • Examples: {config.dataset['total_examples']}")
    print(f"   • Parameters: {len(config.parameters)}")
    print(f"   • Total combinations: {config.execution['max_trials']}")
    print(f"   • Mock mode: {config.execution['mock_mode']}")
    print()
    
    return config

def show_usage_examples():
    """Show practical usage examples"""
    
    print("💡 Usage Examples")
    print("=" * 50)
    print()
    
    print("1. Interactive CLI Usage:")
    print("   ```bash")
    print("   source cli_venv/bin/activate")
    print("   python traigent_benchmark_cli.py")
    print("   ```")
    print()
    
    print("2. Quick Mock Test (copy-paste input):")
    print("   When prompted, enter:")
    print("   2 → test → 5 → 1 → 2 2 1 0 → y → y y n 2 y y n 2 → n n n → 1 y n → y y y")
    print()
    
    print("3. View Dataset Statistics:")
    print("   ```python")
    print("   from traigent_benchmark_cli import DatasetLoader")
    print("   loader = DatasetLoader('support_classification_dataset.json')")
    print("   print(f'Total: {len(loader.dataset[\"examples\"])}')")
    print("   ```")
    print()
    
    print("4. Check Environment:")
    print("   ```python")
    print("   import os")
    print("   print(f'Mock mode: {os.environ.get(\"TRAIGENT_MOCK_MODE\", \"false\")}')")
    print("   print(f'API key: {os.environ.get(\"OPENAI_API_KEY\", \"not set\")[:10]}...')")
    print("   ```")
    print()

def main():
    """Main demonstration"""
    
    # Ensure mock mode is enabled
    os.environ["TRAIGENT_MOCK_MODE"] = "true"
    os.environ["OPENAI_API_KEY"] = "mock-key-for-demos"
    
    print("\n" + "=" * 60)
    print("   TraiGent CLI Benchmark Tool - Component Demo")
    print("=" * 60)
    print()
    
    # Run demonstrations
    demonstrate_cli_components()
    config = create_mock_configuration()
    show_usage_examples()
    
    print("✅ Demonstration complete!")
    print("\nTo run the interactive CLI:")
    print("   python traigent_benchmark_cli.py")
    print()

if __name__ == "__main__":
    main()