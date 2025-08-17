#!/usr/bin/env python3
"""
TraiGent Advanced Benchmark CLI Tool

A configurable benchmarking tool for TraiGent optimization with support for:
- Dynamic parameter space configuration
- Multiple execution modes (local/standard/cloud)  
- Mock mode for cost-free testing
- Few-shot learning and prompt engineering
- Comprehensive results analysis and export
"""

import asyncio
import json
import os
import sys
import tempfile
import yaml
import random
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import uuid

import openai
import pandas as pd

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from load_env import load_demo_env
from shared_utils.mock_llm import setup_mock_mode
import traigent
from traigent.utils.callbacks import StatisticsCallback

# Load environment
load_demo_env()

BANNER = """
🎯 TraiGent Advanced Benchmark CLI Tool
========================================
Configure and run comprehensive LLM optimization experiments
with full control over parameters, datasets, and execution modes.
"""

@dataclass
class ParameterConfig:
    """Configuration for a single parameter"""
    name: str
    param_type: str  # 'categorical', 'continuous', 'discrete', 'boolean'
    values: List[Any]
    enabled: bool = True
    default: Any = None
    description: str = ""

@dataclass
class ExperimentConfig:
    """Complete experiment configuration"""
    name: str
    dataset: Dict[str, Any]
    parameters: Dict[str, ParameterConfig]
    execution: Dict[str, Any]
    output: Dict[str, Any]

class DatasetLoader:
    """Handle dataset loading and sampling"""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.dataset = self.load_dataset()
    
    def load_dataset(self) -> Dict:
        """Load dataset from JSON file"""
        with open(self.dataset_path, 'r') as f:
            return json.load(f)
    
    def get_examples_by_difficulty(self, difficulty: str) -> List[Dict]:
        """Get examples filtered by difficulty level"""
        return [ex for ex in self.dataset['examples'] if ex['difficulty'] == difficulty]
    
    def sample_examples(self, 
                       total: int, 
                       strategy: str = "stratified",
                       difficulty_dist: Optional[Dict[str, int]] = None) -> List[Dict]:
        """Sample examples from dataset"""
        
        if strategy == "random":
            return random.sample(self.dataset['examples'], min(total, len(self.dataset['examples'])))
        
        elif strategy == "stratified":
            if not difficulty_dist:
                # Default even distribution
                per_level = total // 4
                difficulty_dist = {
                    'easy': per_level,
                    'medium': per_level, 
                    'hard': per_level,
                    'expert': total - (3 * per_level)
                }
            
            sampled = []
            for difficulty, count in difficulty_dist.items():
                examples = self.get_examples_by_difficulty(difficulty)
                sampled.extend(random.sample(examples, min(count, len(examples))))
            
            return sampled
        
        elif strategy == "sequential":
            return self.dataset['examples'][:total]
        
        else:
            raise ValueError(f"Unknown sampling strategy: {strategy}")
    
    def create_dataset_file(self, examples: List[Dict]) -> str:
        """Create temporary dataset file for TraiGent"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for example in examples:
                json.dump({
                    "input": example["input"], 
                    "output": example["output"]
                }, f)
                f.write("\\n")
            return f.name

class ExampleSelector:
    """Handle few-shot example selection strategies"""
    
    def __init__(self, dataset: List[Dict]):
        self.dataset = dataset
    
    def select_examples(self, k: int, strategy: str, query_example: Optional[Dict] = None) -> List[Dict]:
        """Select k examples using specified strategy"""
        
        if k <= 0:
            return []
        
        if strategy == "random":
            return random.sample(self.dataset, min(k, len(self.dataset)))
        
        elif strategy == "diverse":
            # Select from different categories
            categories = list(set(ex['output'] for ex in self.dataset))
            selected = []
            for i, category in enumerate(categories):
                if i >= k:
                    break
                cat_examples = [ex for ex in self.dataset if ex['output'] == category]
                if cat_examples:
                    selected.append(random.choice(cat_examples))
            
            # Fill remaining with random
            remaining = k - len(selected)
            if remaining > 0:
                pool = [ex for ex in self.dataset if ex not in selected]
                selected.extend(random.sample(pool, min(remaining, len(pool))))
            
            return selected
        
        elif strategy == "similar":
            # For now, use random (would need embeddings for true similarity)
            return random.sample(self.dataset, min(k, len(self.dataset)))
        
        elif strategy == "difficulty_progression":
            # Select examples in order of difficulty
            difficulties = ['easy', 'medium', 'hard', 'expert']
            selected = []
            for difficulty in difficulties:
                if len(selected) >= k:
                    break
                examples = [ex for ex in self.dataset if ex.get('difficulty') == difficulty]
                if examples:
                    selected.append(random.choice(examples))
            return selected[:k]
        
        else:
            return random.sample(self.dataset, min(k, len(self.dataset)))

class PromptBuilder:
    """Build dynamic prompts based on parameters"""
    
    def __init__(self):
        self.system_roles = {
            "classifier": "You are a helpful assistant that classifies customer support queries.",
            "expert": "You are an expert customer support specialist with years of experience.",
            "technical": "You are a technical support expert who understands complex system issues.",
            "concise": "You are an efficient assistant that provides brief, accurate classifications."
        }
        
        self.output_formats = {
            "single_word": "Respond with only the category name: technical, billing, or general",
            "json": "Respond with JSON: {\"category\": \"technical|billing|general\", \"confidence\": 0.0-1.0}",
            "explanation": "First explain your reasoning, then provide the category on a new line."
        }
        
        self.styles = {
            "concise": "Be brief and direct.",
            "detailed": "Provide thorough explanations.",
            "technical": "Use technical language when appropriate.",
            "friendly": "Use a warm, helpful tone."
        }
    
    def build_system_message(self, role: str, output_format: str, style: str) -> str:
        """Build system message from components"""
        base_role = self.system_roles.get(role, self.system_roles["classifier"])
        format_instruction = self.output_formats.get(output_format, self.output_formats["single_word"])
        style_instruction = self.styles.get(style, "")
        
        system_msg = f"{base_role}\\n\\n{format_instruction}"
        if style_instruction:
            system_msg += f"\\n\\n{style_instruction}"
        
        return system_msg
    
    def format_few_shot_examples(self, examples: List[Dict]) -> List[Dict]:
        """Format examples as conversation messages"""
        messages = []
        for example in examples:
            messages.append({"role": "user", "content": example["input"]["text"]})
            messages.append({"role": "assistant", "content": example["output"]})
        return messages
    
    def build_messages(self, 
                      text: str,
                      system_role: str = "classifier",
                      output_format: str = "single_word", 
                      style: str = "concise",
                      few_shot_examples: List[Dict] = None,
                      chain_of_thought: bool = False,
                      context: str = "") -> List[Dict]:
        """Build complete message array for LLM"""
        
        messages = []
        
        # System message
        system_content = self.build_system_message(system_role, output_format, style)
        if context:
            system_content += f"\\n\\nContext: {context}"
        if chain_of_thought:
            system_content += "\\n\\nThink step by step before providing your answer."
        
        messages.append({"role": "system", "content": system_content})
        
        # Few-shot examples
        if few_shot_examples:
            messages.extend(self.format_few_shot_examples(few_shot_examples))
        
        # User query
        messages.append({"role": "user", "content": text})
        
        return messages

class ParameterRegistry:
    """Registry of available parameters with their configurations"""
    
    def __init__(self):
        self.parameters = {
            # Core LLM Parameters
            "model": ParameterConfig(
                name="model",
                param_type="categorical",
                values=["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o", "gpt-4"],
                description="LLM model to use"
            ),
            "temperature": ParameterConfig(
                name="temperature",
                param_type="continuous", 
                values=[0.0, 0.3, 0.5, 0.7, 1.0],
                description="Sampling temperature (0.0 = deterministic, 1.0 = random)"
            ),
            "max_tokens": ParameterConfig(
                name="max_tokens",
                param_type="discrete",
                values=[10, 20, 50, 100, 200],
                description="Maximum tokens in response"
            ),
            "top_p": ParameterConfig(
                name="top_p", 
                param_type="continuous",
                values=[0.1, 0.5, 0.9, 1.0],
                description="Nucleus sampling threshold"
            ),
            
            # Few-shot Learning
            "few_shot_k": ParameterConfig(
                name="few_shot_k",
                param_type="discrete",
                values=[0, 1, 3, 5, 8],
                description="Number of few-shot examples"
            ),
            "few_shot_strategy": ParameterConfig(
                name="few_shot_strategy",
                param_type="categorical",
                values=["random", "diverse", "similar", "difficulty_progression"],
                description="Strategy for selecting few-shot examples"
            ),
            
            # Prompt Engineering  
            "system_role": ParameterConfig(
                name="system_role",
                param_type="categorical",
                values=["classifier", "expert", "technical", "concise"],
                description="System role/persona"
            ),
            "output_format": ParameterConfig(
                name="output_format", 
                param_type="categorical",
                values=["single_word", "json", "explanation"],
                description="Response format"
            ),
            "response_style": ParameterConfig(
                name="response_style",
                param_type="categorical", 
                values=["concise", "detailed", "technical", "friendly"],
                description="Response style/tone"
            ),
            "chain_of_thought": ParameterConfig(
                name="chain_of_thought",
                param_type="boolean",
                values=[True, False],
                description="Enable chain-of-thought reasoning"
            ),
            
            # Context/Retrieval
            "retrieval_k": ParameterConfig(
                name="retrieval_k",
                param_type="discrete",
                values=[0, 3, 5, 10],
                description="Number of retrieved context examples"
            ),
            "context_size": ParameterConfig(
                name="context_size",
                param_type="categorical",
                values=["small", "medium", "large"],
                description="Amount of additional context"
            )
        }
    
    def get_parameter(self, name: str) -> Optional[ParameterConfig]:
        """Get parameter configuration by name"""
        return self.parameters.get(name)
    
    def get_categories(self) -> Dict[str, List[str]]:
        """Get parameters grouped by category"""
        return {
            "Core LLM": ["model", "temperature", "max_tokens", "top_p"],
            "Few-Shot Learning": ["few_shot_k", "few_shot_strategy"], 
            "Prompt Engineering": ["system_role", "output_format", "response_style", "chain_of_thought"],
            "Context/Retrieval": ["retrieval_k", "context_size"]
        }

class TraiGentBenchmarkCLI:
    """Main CLI application"""
    
    def __init__(self):
        self.parameter_registry = ParameterRegistry()
        self.dataset_loader = None
        self.config = None
        self.experiment_id = str(uuid.uuid4())[:8]
        
    def print_banner(self):
        """Print application banner"""
        print(BANNER)
        
    def select_configuration_mode(self) -> str:
        """Select configuration mode"""
        print("\\n📋 Configuration Mode:")
        print("1. Quick Start (Presets)")
        print("2. Guided Configuration") 
        print("3. Advanced Configuration")
        print("4. Load Configuration File")
        
        while True:
            try:
                choice = input("\\nChoice (1-4): ").strip()
                if choice in ["1", "2", "3", "4"]:
                    return ["preset", "guided", "advanced", "load"][int(choice) - 1]
                print("Please enter 1, 2, 3, or 4")
            except (ValueError, KeyboardInterrupt):
                print("\\nExiting...")
                sys.exit(0)
    
    def configure_dataset(self) -> Dict[str, Any]:
        """Configure dataset parameters"""
        print("\\n📊 Dataset Configuration")
        print("=" * 50)
        
        # Load dataset info
        self.dataset_loader = DatasetLoader("support_classification_dataset.json")
        total_available = len(self.dataset_loader.dataset['examples'])
        
        print(f"Total examples available: {total_available}")
        
        # Get number of examples
        while True:
            try:
                num_examples = input(f"Number of examples to use (1-{total_available}) [25]: ").strip()
                if not num_examples:
                    num_examples = 25
                else:
                    num_examples = int(num_examples)
                
                if 1 <= num_examples <= total_available:
                    break
                print(f"Please enter a number between 1 and {total_available}")
            except ValueError:
                print("Please enter a valid number")
        
        # Get sampling strategy
        print("\\nSampling strategy:")
        print("1. Stratified (balanced across difficulty levels)")
        print("2. Random sampling")
        print("3. Sequential (first N examples)")
        
        while True:
            try:
                strategy_choice = input("Strategy (1-3) [1]: ").strip()
                if not strategy_choice:
                    strategy_choice = "1"
                
                if strategy_choice == "1":
                    strategy = "stratified"
                    # Configure difficulty distribution
                    print("\\nDifficulty distribution:")
                    per_level = num_examples // 4
                    remaining = num_examples % 4
                    
                    easy = int(input(f"Easy examples [{per_level}]: ") or per_level)
                    medium = int(input(f"Medium examples [{per_level}]: ") or per_level)
                    hard = int(input(f"Hard examples [{per_level}]: ") or per_level)
                    expert = int(input(f"Expert examples [{per_level + remaining}]: ") or (per_level + remaining))
                    
                    difficulty_dist = {
                        "easy": easy,
                        "medium": medium, 
                        "hard": hard,
                        "expert": expert
                    }
                    break
                elif strategy_choice == "2":
                    strategy = "random"
                    difficulty_dist = None
                    break
                elif strategy_choice == "3":
                    strategy = "sequential"
                    difficulty_dist = None
                    break
                else:
                    print("Please enter 1, 2, or 3")
            except ValueError:
                print("Please enter valid numbers")
        
        return {
            "total_examples": num_examples,
            "sampling_strategy": strategy,
            "difficulty_distribution": difficulty_dist
        }
    
    def configure_parameters(self) -> Dict[str, ParameterConfig]:
        """Configure parameter space"""
        print("\\n🔧 Parameter Space Configuration")
        print("=" * 50)
        
        categories = self.parameter_registry.get_categories()
        selected_params = {}
        
        for category, param_names in categories.items():
            print(f"\\n{category}:")
            include = input(f"Include {category} parameters? (y/n) [y]: ").strip().lower()
            
            if include not in ['n', 'no']:
                for param_name in param_names:
                    param = self.parameter_registry.get_parameter(param_name)
                    print(f"\\n  {param.name}: {param.description}")
                    print(f"  Available values: {param.values}")
                    
                    # Ask if user wants to include this parameter
                    include_param = input(f"  Include {param.name}? (y/n) [y]: ").strip().lower()
                    if include_param in ['n', 'no']:
                        continue
                    
                    # Ask for custom values
                    custom = input(f"  Use custom values? (y/n) [n]: ").strip().lower()
                    if custom in ['y', 'yes']:
                        if param.param_type == "categorical":
                            values_str = input(f"  Enter values (comma-separated): ").strip()
                            values = [v.strip() for v in values_str.split(',') if v.strip()]
                        elif param.param_type == "boolean":
                            values = [True, False]
                        else:
                            values_str = input(f"  Enter values (comma-separated): ").strip()
                            try:
                                values = [float(v.strip()) for v in values_str.split(',') if v.strip()]
                            except ValueError:
                                print("  Invalid values, using defaults")
                                values = param.values
                    else:
                        # Ask how many values to use
                        max_values = len(param.values)
                        num_values = input(f"  How many values to use (1-{max_values}) [{min(3, max_values)}]: ").strip()
                        if not num_values:
                            num_values = min(3, max_values)
                        else:
                            num_values = int(num_values)
                        
                        if param.param_type == "boolean":
                            values = param.values
                        else:
                            values = param.values[:num_values]
                    
                    # Create modified parameter config
                    selected_params[param_name] = ParameterConfig(
                        name=param.name,
                        param_type=param.param_type,
                        values=values,
                        enabled=True,
                        description=param.description
                    )
        
        # Calculate total configurations
        total_configs = 1
        for param in selected_params.values():
            total_configs *= len(param.values)
        
        print(f"\\n📈 Total parameter combinations: {total_configs}")
        
        if total_configs > 100:
            print("⚠️  Warning: Large number of configurations!")
            strategy = input("Optimization strategy (grid/random/bayesian) [random]: ").strip()
            if not strategy:
                strategy = "random"
            
            if strategy == "random":
                max_trials = input(f"Maximum trials [50]: ").strip()
                max_trials = int(max_trials) if max_trials else 50
            else:
                max_trials = total_configs
        else:
            strategy = "grid"
            max_trials = total_configs
        
        print(f"\\nStrategy: {strategy}, Max trials: {max_trials}")
        
        return selected_params, strategy, max_trials
    
    def configure_execution(self) -> Dict[str, Any]:
        """Configure execution parameters"""
        print("\\n⚙️  Execution Configuration")
        print("=" * 50)
        
        # Execution mode
        print("Execution modes:")
        print("1. Local (no backend required)")
        print("2. Standard (hybrid with backend)")
        print("3. Cloud (full cloud execution)")
        
        mode_choice = input("Mode (1-3) [1]: ").strip()
        if mode_choice == "2":
            mode = "standard"
        elif mode_choice == "3":
            mode = "cloud"
        else:
            mode = "local"
        
        # Mock mode
        mock_mode = input("Use mock mode (no API costs)? (y/n) [n]: ").strip().lower()
        mock_mode = mock_mode in ['y', 'yes']
        
        # Early stopping
        early_stopping = input("Enable early stopping? (y/n) [n]: ").strip().lower()
        early_stopping = early_stopping in ['y', 'yes']
        
        return {
            "mode": mode,
            "mock_mode": mock_mode,
            "early_stopping": early_stopping
        }
    
    def estimate_costs(self, config: Dict) -> Dict[str, Any]:
        """Estimate execution costs"""
        print("\\n💰 Cost Estimation")
        print("=" * 50)
        
        total_configs = 1
        for param in config['parameters'].values():
            total_configs *= len(param.values)
        
        max_trials = config['execution'].get('max_trials', total_configs)
        num_examples = config['dataset']['total_examples']
        total_calls = max_trials * num_examples
        
        # Rough cost estimation (very approximate)
        if config['execution']['mock_mode']:
            estimated_cost = 0.0
        else:
            # Assume average of $0.001 per call (varies by model)
            estimated_cost = total_calls * 0.001
        
        print(f"Total API calls: {total_calls}")
        print(f"Estimated cost: ${estimated_cost:.2f}")
        print(f"Estimated time: {total_calls * 0.5 / 60:.1f} minutes")
        
        return {
            "total_calls": total_calls,
            "estimated_cost": estimated_cost,
            "estimated_time_minutes": total_calls * 0.5 / 60
        }
    
    def guided_configuration(self) -> ExperimentConfig:
        """Guided configuration wizard"""
        print("\\n🧙 Guided Configuration Wizard")
        
        # Experiment name
        name = input("\\nExperiment name [benchmark_experiment]: ").strip()
        if not name:
            name = f"benchmark_experiment_{self.experiment_id}"
        
        # Configure each section
        dataset_config = self.configure_dataset()
        parameters, strategy, max_trials = self.configure_parameters()
        execution_config = self.configure_execution()
        execution_config.update({"algorithm": strategy, "max_trials": max_trials})
        
        # Output configuration
        output_config = {
            "save_results": True,
            "export_formats": ["json", "csv"],
            "create_visualizations": True
        }
        
        config = ExperimentConfig(
            name=name,
            dataset=dataset_config,
            parameters=parameters,
            execution=execution_config,
            output=output_config
        )
        
        # Show summary and get confirmation
        self.show_config_summary(config)
        
        return config
    
    def show_config_summary(self, config: ExperimentConfig):
        """Show configuration summary"""
        print("\\n📋 Configuration Summary")
        print("=" * 50)
        print(f"Experiment: {config.name}")
        print(f"Examples: {config.dataset['total_examples']}")
        print(f"Parameters: {len([p for p in config.parameters.values() if p.enabled])}")
        print(f"Execution mode: {config.execution['mode']}")
        print(f"Mock mode: {config.execution['mock_mode']}")
        
        # Estimate costs
        costs = self.estimate_costs({
            'parameters': config.parameters,
            'dataset': config.dataset,
            'execution': config.execution
        })
        
        confirm = input("\\nProceed with this configuration? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("Configuration cancelled.")
            sys.exit(0)
    
    def save_configuration(self, config: ExperimentConfig):
        """Save configuration to file"""
        config_dir = Path("benchmark_configs")
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / f"{config.name}.yaml"
        
        # Convert to serializable format
        config_dict = {
            "name": config.name,
            "dataset": config.dataset,
            "parameters": {
                name: {
                    "param_type": param.param_type,
                    "values": param.values,
                    "enabled": param.enabled,
                    "description": param.description
                }
                for name, param in config.parameters.items()
            },
            "execution": config.execution,
            "output": config.output
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
        
        print(f"\\n💾 Configuration saved to: {config_file}")
    
    def execute_benchmark(self, config: ExperimentConfig):
        """Execute the benchmark using TraiGent's parameter injection"""
        print("\\n🚀 Executing Benchmark...")
        print("=" * 50)
        
        # Sample dataset based on configuration
        examples = self.dataset_loader.sample_examples(
            total=config.dataset['total_examples'],
            strategy=config.dataset['sampling_strategy'],
            difficulty_dist=config.dataset.get('difficulty_distribution')
        )
        
        print(f"✅ Sampled {len(examples)} examples")
        
        # Create dataset file for TraiGent
        dataset_file = self.dataset_loader.create_dataset_file(examples)
        print(f"✅ Created dataset file: {dataset_file}")
        
        # Extract only enabled parameters for configuration_space
        config_space = {}
        for name, param in config.parameters.items():
            if param.enabled:
                config_space[name] = param.values
        
        print(f"✅ Configuration space: {len(config_space)} parameters")
        for name, values in config_space.items():
            print(f"   • {name}: {values}")
        
        # Generate the optimized function dynamically using TraiGent's parameter injection
        optimized_function = self.create_optimized_function(
            dataset_file=dataset_file,
            config_space=config_space,
            config=config
        )
        
        print(f"\\n🔄 Starting optimization with TraiGent...")
        print(f"   Algorithm: {config.execution['algorithm']}")
        print(f"   Max trials: {config.execution['max_trials']}")
        print(f"   Mock mode: {config.execution['mock_mode']}")
        
        return optimized_function, dataset_file
    
    def create_optimized_function(self, dataset_file: str, config_space: Dict, config: ExperimentConfig):
        """Create TraiGent optimized function with parameter injection"""
        
        # Import required modules for the generated function
        import traigent
        import openai
        from traigent.utils.callbacks import StatisticsCallback
        
        # Set up mock mode if needed
        if config.execution['mock_mode']:
            setup_mock_mode()
        
        # Initialize prompt builder and example selector
        prompt_builder = PromptBuilder()
        example_selector = ExampleSelector(self.dataset_loader.dataset['examples'])
        
        # Create the optimized function using TraiGent's parameter injection
        @traigent.optimize(
            eval_dataset=dataset_file,
            objectives=["accuracy"],
            configuration_space=config_space,
            max_trials=config.execution.get('max_trials', 10),
            algorithm=config.execution.get('algorithm', 'grid')
        )
        def classify_with_dynamic_params(
            text: str,
            model: str = "gpt-3.5-turbo",
            temperature: float = 0.3,
            max_tokens: int = 10,
            top_p: float = 1.0,
            few_shot_k: int = 0,
            few_shot_strategy: str = "random",
            system_role: str = "classifier",
            output_format: str = "single_word",
            response_style: str = "concise",
            chain_of_thought: bool = False,
            retrieval_k: int = 0,
            context_size: str = "small"
        ) -> str:
            """
            Dynamically configured classification function.
            TraiGent automatically injects optimized parameters.
            """
            
            # Get few-shot examples if requested
            few_shot_examples = []
            if few_shot_k > 0:
                few_shot_examples = example_selector.select_examples(
                    k=few_shot_k,
                    strategy=few_shot_strategy
                )
            
            # Build context if requested
            context = ""
            if context_size != "small":
                context_levels = {
                    "medium": "You are classifying customer support queries for a tech company.",
                    "large": "You are classifying customer support queries for a tech company. Consider the technical complexity, billing implications, and general nature of each query when making classifications."
                }
                context = context_levels.get(context_size, "")
            
            # Build messages using prompt builder
            messages = prompt_builder.build_messages(
                text=text,
                system_role=system_role,
                output_format=output_format,
                style=response_style,
                few_shot_examples=few_shot_examples,
                chain_of_thought=chain_of_thought,
                context=context
            )
            
            # Create OpenAI API call with TraiGent parameter injection
            response = openai.chat.completions.create(
                model=model,  # TraiGent will inject optimized value
                temperature=temperature,  # TraiGent will inject optimized value
                max_tokens=max_tokens,  # TraiGent will inject optimized value
                top_p=top_p,  # TraiGent will inject optimized value
                messages=messages
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("No content in response")
            
            return content.strip().lower()
        
        return classify_with_dynamic_params
    
    def run(self):
        """Main application entry point"""
        try:
            self.print_banner()
            
            # Select configuration mode
            mode = self.select_configuration_mode()
            
            if mode == "guided":
                self.config = self.guided_configuration()
                
                # Save configuration
                save = input("\\nSave this configuration? (y/n) [y]: ").strip().lower()
                if save not in ['n', 'no']:
                    self.save_configuration(self.config)
                
                # Ask if user wants to run the benchmark
                run_now = input("\\nRun benchmark now? (y/n) [y]: ").strip().lower()
                if run_now not in ['n', 'no']:
                    optimized_function, dataset_file = self.execute_benchmark(self.config)
                    
                    print("\\n🎯 Ready to run optimization!")
                    print("Run the following to execute:")
                    print("```python")
                    print("import asyncio")
                    print("results = await optimized_function.optimize()")
                    print("print(f'Best config: {results.best_config}')")
                    print("print(f'Best score: {results.best_score:.1%}')")
                    print("```")
                    
                    # Clean up temporary file
                    try:
                        os.unlink(dataset_file)
                    except:
                        pass
                else:
                    print("\\n✅ Configuration saved! Use saved config to run benchmark later.")
                
            else:
                print(f"\\n{mode.title()} mode not yet implemented.")
                print("Use guided mode (option 2) for now.")
                
        except KeyboardInterrupt:
            print("\\n\\nExiting...")
            sys.exit(0)
        except Exception as e:
            print(f"\\nError: {e}")
            sys.exit(1)

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="TraiGent Advanced Benchmark CLI Tool")
    parser.add_argument("--config", help="Load configuration from file")
    parser.add_argument("--preset", help="Use preset configuration")
    parser.add_argument("--dry-run", action="store_true", help="Show configuration without running")
    
    args = parser.parse_args()
    
    cli = TraiGentBenchmarkCLI()
    cli.run()

if __name__ == "__main__":
    main()