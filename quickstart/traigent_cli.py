#!/usr/bin/env python3
"""
TraiGent Generalized CLI Tool - Optimize any agent with intelligent parameter search.

This CLI tool provides a flexible interface for running TraiGent optimization on
various agent functions with configurable parameters and datasets.
"""

import argparse
import asyncio
import json
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import importlib.util

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Also add Traigent directory specifically
sys.path.insert(0, str(Path(__file__).parent.parent / "Traigent"))

# Load environment variables
from load_env import load_demo_env_once
load_demo_env_once()

try:
    import traigent
    from traigent.utils.callbacks import (
        DetailedProgressCallback,
        SimpleProgressCallback
    )
except ImportError:
    print("❌ TraiGent not found. Please install it first:")
    print("   pip install -e ../Traigent")
    sys.exit(1)


@dataclass
class AgentInfo:
    """Information about a loaded agent."""
    name: str
    path: Path
    config: Dict[str, Any]
    dataset: Dict[str, Any]
    module: Any


class AgentLoader:
    """Handles loading and management of agent modules."""
    
    def __init__(self, agents_dir: Path = None):
        """Initialize the agent loader.
        
        Args:
            agents_dir: Directory containing agent subdirectories
        """
        self.agents_dir = agents_dir or Path(__file__).parent / "agents"
        self.agents: Dict[str, AgentInfo] = {}
        self._discover_agents()
    
    def _discover_agents(self):
        """Discover all available agents in the agents directory."""
        if not self.agents_dir.exists():
            print(f"⚠️  Agents directory not found: {self.agents_dir}")
            return
        
        for agent_dir in self.agents_dir.iterdir():
            if agent_dir.is_dir() and not agent_dir.name.startswith('_'):
                # Check for required files
                agent_py = agent_dir / "agent.py"
                config_json = agent_dir / "config.json"
                dataset_json = agent_dir / "dataset.json"
                
                if all(f.exists() for f in [agent_py, config_json, dataset_json]):
                    try:
                        # Load config
                        with open(config_json) as f:
                            config = json.load(f)
                        
                        # Load dataset
                        with open(dataset_json) as f:
                            dataset = json.load(f)
                        
                        # Create agent info (module loaded on demand)
                        agent_info = AgentInfo(
                            name=agent_dir.name,
                            path=agent_dir,
                            config=config,
                            dataset=dataset,
                            module=None  # Loaded on demand
                        )
                        
                        self.agents[agent_dir.name] = agent_info
                    except Exception as e:
                        print(f"⚠️  Failed to load agent {agent_dir.name}: {e}")
    
    def list_agents(self) -> List[str]:
        """Get list of available agent names."""
        return list(self.agents.keys())
    
    def load_agent(self, name: str) -> AgentInfo:
        """Load a specific agent by name.
        
        Args:
            name: Name of the agent to load
            
        Returns:
            AgentInfo with loaded module
        """
        if name not in self.agents:
            raise ValueError(f"Agent '{name}' not found. Available: {', '.join(self.list_agents())}")
        
        agent_info = self.agents[name]
        
        # Load module if not already loaded
        if agent_info.module is None:
            agent_py = agent_info.path / "agent.py"
            
            # Load the module dynamically
            spec = importlib.util.spec_from_file_location(f"agents.{name}", agent_py)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            agent_info.module = module
        
        return agent_info


class DatasetManager:
    """Manages dataset sampling and preparation."""
    
    def __init__(self, dataset: Dict[str, Any]):
        """Initialize with a dataset dictionary."""
        self.dataset = dataset
        self.examples = dataset.get('examples', [])
        self.metadata = dataset.get('metadata', {})
    
    def sample_examples(self, 
                        total: int = None,
                        strategy: str = 'stratified',
                        difficulty_dist: Dict[str, float] = None) -> List[Dict]:
        """Sample examples from the dataset.
        
        Args:
            total: Number of examples to sample (None for all)
            strategy: Sampling strategy ('stratified', 'random', 'sequential')
            difficulty_dist: Distribution for stratified sampling
            
        Returns:
            List of sampled examples
        """
        if total is None or total >= len(self.examples):
            return self.examples
        
        if strategy == 'sequential':
            return self.examples[:total]
        
        elif strategy == 'random':
            import random
            return random.sample(self.examples, total)
        
        elif strategy == 'stratified':
            # Group by difficulty
            by_difficulty = {}
            for ex in self.examples:
                diff = ex.get('difficulty', 'medium')
                if diff not in by_difficulty:
                    by_difficulty[diff] = []
                by_difficulty[diff].append(ex)
            
            # Sample proportionally
            sampled = []
            remaining = total
            difficulties = list(by_difficulty.keys())
            
            for i, diff in enumerate(difficulties):
                if i == len(difficulties) - 1:
                    # Last group gets remaining
                    count = remaining
                else:
                    # Proportional sampling
                    count = int(total * len(by_difficulty[diff]) / len(self.examples))
                    remaining -= count
                
                available = by_difficulty[diff]
                count = min(count, len(available))
                import random
                sampled.extend(random.sample(available, count))
            
            return sampled
        
        else:
            raise ValueError(f"Unknown sampling strategy: {strategy}")
    
    def create_dataset_file(self, examples: List[Dict]) -> str:
        """Create a temporary dataset file for optimization.
        
        Args:
            examples: List of examples to include
            
        Returns:
            Path to the created dataset file
        """
        # Create temporary file
        fd, path = tempfile.mkstemp(suffix='.jsonl', prefix='traigent_dataset_')
        
        # Write examples in JSONL format
        with os.fdopen(fd, 'w') as f:
            for ex in examples:
                # Convert to optimization format
                opt_example = {
                    'input': ex.get('input', {}),
                    'expected_output': ex.get('output', '')
                }
                f.write(json.dumps(opt_example) + '\n')
        
        return path


class TraiGentCLI:
    """Main CLI application for TraiGent optimization."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.agent_loader = AgentLoader()
        self.current_agent: Optional[AgentInfo] = None
        self.dataset_manager: Optional[DatasetManager] = None
    
    def create_optimized_function(self, 
                                 agent_info: AgentInfo,
                                 dataset_file: str,
                                 config_space: Dict,
                                 execution_config: Dict) -> Callable:
        """Create the TraiGent optimized function for the agent."""
        
        # Validate max_trials
        max_trials = execution_config.get('max_trials', 10)
        if not isinstance(max_trials, int) or max_trials < 1:
            print(f"⚠️  Invalid max_trials: {max_trials}, using default: 10")
            max_trials = 10
            execution_config['max_trials'] = max_trials
        
        print(f"\n📝 Optimization Configuration:")
        print(f"   Max trials: {max_trials}")
        print(f"   Algorithm: {execution_config.get('algorithm', 'grid')}")
        print(f"   Mode: {execution_config.get('mode', 'local')}")
        
        # Set up mock mode - FORCE override environment variables if needed
        if execution_config.get('mock_mode', False):
            # Force override any .env settings for mock mode
            os.environ["TRAIGENT_MOCK_MODE"] = "true"
            os.environ["TRAIGENT_EXECUTION_MODE"] = "local"
            print("✅ TraiGent mock mode ENABLED - no API costs will be incurred")
            print(f"   Environment: TRAIGENT_MOCK_MODE={os.environ.get('TRAIGENT_MOCK_MODE')}")
            print(f"   Environment: TRAIGENT_EXECUTION_MODE={os.environ.get('TRAIGENT_EXECUTION_MODE')}")
        else:
            print("🔥 Real API mode ENABLED - API costs WILL be incurred")
            print(f"   Environment: TRAIGENT_MOCK_MODE={os.environ.get('TRAIGENT_MOCK_MODE')}")
            print(f"   Environment: TRAIGENT_EXECUTION_MODE={os.environ.get('TRAIGENT_EXECUTION_MODE')}")
            
            # Check if API keys are available
            openai_key = os.environ.get('OPENAI_API_KEY')
            anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
            print(f"   OpenAI API Key: {'✅ Present' if openai_key and openai_key.startswith('sk-') else '❌ Missing'}")
            print(f"   Anthropic API Key: {'✅ Present' if anthropic_key and anthropic_key.startswith('sk-ant') else '❌ Missing'}")
            
            if execution_config.get('mode') != 'local':
                print("🔥 Cloud API mode ENABLED - API costs will be incurred")
        
        # Get agent components
        agent_module = agent_info.module
        
        # Create necessary instances
        if hasattr(agent_module, 'PromptBuilder'):
            prompt_builder = agent_module.PromptBuilder()
        else:
            raise ValueError(f"Agent {agent_info.name} missing PromptBuilder class")
        
        if hasattr(agent_module, 'ExampleSelector'):
            example_selector = agent_module.ExampleSelector(self.dataset_manager.examples)
        else:
            raise ValueError(f"Agent {agent_info.name} missing ExampleSelector class")
        
        # Get the agent class and create function
        agent_class_name = None
        for name in dir(agent_module):
            if 'Agent' in name and name != 'Agent':
                agent_class_name = name
                break
        
        if not agent_class_name:
            raise ValueError(f"No Agent class found in {agent_info.name}")
        
        agent_class = getattr(agent_module, agent_class_name)
        agent_instance = agent_class()
        
        # Get the base function
        base_function = agent_instance.create_function(prompt_builder, example_selector)
        
        # Get objectives from config
        objectives = agent_info.config.get('objectives', ['accuracy'])
        
        # Apply TraiGent optimization decorator with parallel configuration
        parallel_config = {
            'parallel_trials': execution_config.get('parallel_trials'),
            'batch_size': execution_config.get('batch_size'),
            'max_workers': execution_config.get('max_workers'),
            'adaptive_batching': execution_config.get('adaptive_batching', False)
        }
        
        # Log parallel configuration
        if parallel_config['parallel_trials'] and parallel_config['parallel_trials'] > 1:
            print(f"   Parallel trials: {parallel_config['parallel_trials']} (between-trial parallelism)")
        if parallel_config['batch_size'] and parallel_config['batch_size'] > 1:
            print(f"   Batch size: {parallel_config['batch_size']} (within-trial parallelism)")
        if parallel_config['max_workers'] and parallel_config['max_workers'] > 1:
            print(f"   Max workers: {parallel_config['max_workers']} (batch processing)")
        if parallel_config['adaptive_batching']:
            print(f"   Adaptive batching: enabled")
        
        optimized_function = traigent.optimize(
            eval_dataset=dataset_file,
            objectives=objectives,
            configuration_space=config_space,
            max_trials=max_trials,
            algorithm=execution_config.get('algorithm', 'grid'),
            execution_mode=execution_config.get('mode', 'local'),
            **{k: v for k, v in parallel_config.items() if v is not None}
        )(base_function)
        
        return optimized_function
    
    def _create_progress_callback(self, progress_mode: str):
        """Create progress callback based on mode selection."""
        if progress_mode == 'none':
            return None
        elif progress_mode == 'detailed':
            print("🎯 Using detailed progress tracking...")
            return DetailedProgressCallback(show_config_details=True, show_metrics=True)
        else:  # 'simple' mode
            return SimpleProgressCallback(output="print", show_details=True)
    
    def run_optimization(self, args):
        """Run optimization with command-line arguments."""
        
        # Load agent
        print(f"\n📦 Loading agent: {args.agent}")
        self.current_agent = self.agent_loader.load_agent(args.agent)
        self.dataset_manager = DatasetManager(self.current_agent.dataset)
        
        agent_config = self.current_agent.config
        print(f"✅ Agent loaded: {agent_config.get('name', args.agent)}")
        print(f"   {agent_config.get('description', '')}")
        
        # Parse parameter space
        param_space = {}
        
        # Handle models
        if args.models:
            param_space['model'] = args.models
            
        # Handle temperature
        if args.temperature:
            param_space['temperature'] = args.temperature
            
        # Handle max_tokens
        if args.max_tokens:
            param_space['max_tokens'] = args.max_tokens
            
        # Handle top_p
        if args.top_p:
            param_space['top_p'] = args.top_p
            
        # Handle few_shot_k
        if args.few_shot_k:
            param_space['few_shot_k'] = args.few_shot_k
            
        # Handle LiveBench-specific parameters
        livebench_params = {
            'system_role': 'system_role',
            'reasoning_style': 'reasoning_style', 
            'problem_approach': 'problem_approach',
            'answer_format': 'answer_format',
            'notation_style': 'notation_style',
            'verification_style': 'verification_style',
            'cot_style': 'cot_style',
            'preset_template': 'preset_template'
        }
        
        for param_name, arg_name in livebench_params.items():
            if hasattr(args, arg_name) and getattr(args, arg_name) is not None:
                param_space[param_name] = [getattr(args, arg_name)]
            
        # If no parameters specified, use defaults from config
        if not param_space:
            print("\n⚠️  No parameters specified. Using defaults from agent config.")
            default_params = agent_config.get('parameters', {})
            for param_name, param_def in default_params.items():
                if param_def.get('default'):
                    param_space[param_name] = [param_def['default']]
        
        # Calculate total combinations
        total_configs = 1
        for values in param_space.values():
            total_configs *= len(values)
        
        print(f"\n📊 Configuration Summary:")
        print(f"   Total combinations: {total_configs}")
        print(f"   Parameters: {list(param_space.keys())}")
        
        # Determine algorithm and max_trials
        if args.algorithm:
            algorithm = args.algorithm
        elif total_configs <= 20:
            algorithm = 'grid'
        else:
            algorithm = 'random'
        
        if args.max_trials:
            max_trials = args.max_trials
        elif algorithm == 'grid':
            max_trials = min(total_configs, 100)
        else:
            max_trials = min(10, total_configs)
        
        # Sample dataset
        examples = self.dataset_manager.sample_examples(
            total=args.num_examples,
            strategy=args.sampling_strategy
        )
        
        print(f"\n✅ Sampled {len(examples)} examples using {args.sampling_strategy} strategy")
        
        # Create dataset file
        dataset_file = self.dataset_manager.create_dataset_file(examples)
        print(f"✅ Created dataset file: {dataset_file}")
        
        # Prepare execution config
        exec_config = {
            'algorithm': algorithm,
            'max_trials': max_trials,
            'mode': args.execution_mode,
            'mock_mode': args.mock_mode,
            'parallel_trials': args.parallel_trials,
            'batch_size': args.batch_size,
            'max_workers': args.max_workers,
            'adaptive_batching': args.adaptive_batching
        }
        
        # Create optimized function
        optimized_function = self.create_optimized_function(
            self.current_agent, dataset_file, param_space, exec_config
        )
        
        # Get objectives for progress callback
        objectives = self.current_agent.config.get('objectives', ['accuracy'])
        
        # Setup progress callback
        callback = self._create_progress_callback(args.progress)
        
        print(f"\n🔄 Starting optimization...")
        print(f"   Algorithm: {algorithm}")
        print(f"   Max trials: {max_trials}")
        print(f"   Mock mode: {args.mock_mode}")
        
        try:
            # Run optimization with TraiGent's native callback system
            callback_list = [callback] if callback else []
            
            # Use asyncio.run() for proper async handling
            results = asyncio.run(optimized_function.optimize(
                algorithm=algorithm,
                max_trials=max_trials,
                callbacks=callback_list
            ))
            
            # Display results
            print(f"\n✅ Optimization completed!")
            print(f"   Best score: {results.best_score:.4f}")
            print(f"   Best config: {json.dumps(results.best_config, indent=2)}")
            
            # Calculate total cost from trials
            total_cost = 0.0
            total_tokens = 0
            for trial in results.trials:
                # Check for cost in trial's direct attributes
                if hasattr(trial, 'cost') and trial.cost:
                    total_cost += trial.cost
                
                # Check for cost in trial metrics (where it's actually stored)
                if hasattr(trial, 'metrics') and trial.metrics:
                    # Check for cost in metrics dict - this is where the tokencost values are stored
                    if 'cost' in trial.metrics:
                        total_cost += trial.metrics.get('cost', 0.0)
                    if 'total_cost' in trial.metrics:
                        total_cost += trial.metrics.get('total_cost', 0.0)
                    if 'input_cost' in trial.metrics and 'output_cost' in trial.metrics:
                        total_cost += trial.metrics.get('input_cost', 0.0) + trial.metrics.get('output_cost', 0.0)
                    # Check for tokens in metrics
                    if 'total_tokens' in trial.metrics:
                        total_tokens += trial.metrics.get('total_tokens', 0)
                
                # Also check metadata as a fallback
                if hasattr(trial, 'metadata') and trial.metadata:
                    # Check for cost in metadata
                    if 'cost' in trial.metadata:
                        total_cost += trial.metadata.get('cost', 0.0)
                    if 'total_cost' in trial.metadata:
                        total_cost += trial.metadata.get('total_cost', 0.0)
                    # Check for tokens
                    if 'total_tokens' in trial.metadata:
                        total_tokens += trial.metadata.get('total_tokens', 0)
            
            if total_cost > 0:
                print(f"   Total cost: ${total_cost:.6f}")
            if total_tokens > 0:
                print(f"   Total tokens: {total_tokens:,}")
            
            # Debug: Show trial details
            if args.verbose and results.trials:
                print(f"\n🔍 Trial details:")
                for i, trial in enumerate(results.trials):
                    print(f"   Trial {i+1}: score={trial.metrics.get('accuracy', 0.0):.4f}")
                    
                    # Get cost from metrics (where it's actually stored)
                    cost = 0.0
                    tokens = 0
                    
                    if hasattr(trial, 'metrics') and trial.metrics:
                        cost = max(
                            trial.metrics.get('cost', 0.0),
                            trial.metrics.get('total_cost', 0.0),
                            trial.metrics.get('input_cost', 0.0) + trial.metrics.get('output_cost', 0.0)
                        )
                        tokens = trial.metrics.get('total_tokens', 0)
                    
                    # Fallback to metadata
                    if cost == 0.0 and hasattr(trial, 'metadata') and trial.metadata:
                        cost = trial.metadata.get('total_cost', trial.metadata.get('cost', 0.0))
                        if tokens == 0:
                            tokens = trial.metadata.get('total_tokens', 0)
                    
                    if cost > 0:
                        print(f"     Cost: ${cost:.6f}")
                    if tokens > 0:
                        print(f"     Tokens: {tokens:,}")
            
            # Save results if requested
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Prepare detailed results including cost
                detailed_results = {
                    'agent': args.agent,
                    'best_config': results.best_config,
                    'best_score': results.best_score,
                    'trials': len(results.trials),
                    'parameters': param_space,
                    'algorithm': algorithm,
                    'max_trials': max_trials,
                    'total_cost': total_cost,
                    'total_tokens': total_tokens
                }
                
                # Add trial details if verbose
                if args.verbose:
                    detailed_results['trial_details'] = []
                    for i, trial in enumerate(results.trials):
                        trial_info = {
                            'trial_number': i + 1,
                            'config': trial.config,
                            'score': trial.metrics.get('accuracy', 0.0),
                            'metrics': trial.metrics
                        }
                        # Get cost from metrics (where it's actually stored)
                        cost = 0.0
                        tokens = 0
                        
                        if hasattr(trial, 'metrics') and trial.metrics:
                            cost = max(
                                trial.metrics.get('cost', 0.0),
                                trial.metrics.get('total_cost', 0.0),
                                trial.metrics.get('input_cost', 0.0) + trial.metrics.get('output_cost', 0.0)
                            )
                            tokens = trial.metrics.get('total_tokens', 0)
                        
                        # Fallback to metadata
                        if cost == 0.0 and hasattr(trial, 'metadata') and trial.metadata:
                            cost = trial.metadata.get('total_cost', trial.metadata.get('cost', 0.0))
                            if tokens == 0:
                                tokens = trial.metadata.get('total_tokens', 0)
                        
                        trial_info['cost'] = cost
                        trial_info['tokens'] = tokens
                        detailed_results['trial_details'].append(trial_info)
                
                with open(output_path, 'w') as f:
                    json.dump(detailed_results, f, indent=2)
                
                print(f"\n💾 Results saved to: {output_path}")
            
        except Exception as e:
            print(f"\n❌ Optimization failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
        finally:
            # Clean up dataset file
            try:
                os.unlink(dataset_file)
            except:
                pass
        
        return 0


def create_parser():
    """Create the argument parser with comprehensive help."""
    
    parser = argparse.ArgumentParser(
        description='TraiGent CLI - Optimize AI agents with intelligent parameter search',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic optimization with default settings
  %(prog)s --agent support_classifier
  
  # Custom model and temperature selection
  %(prog)s --agent support_classifier --models gpt-3.5-turbo gpt-4 --temperature 0.0 0.5 1.0
  
  # Full configuration with all parameters
  %(prog)s --agent support_classifier \\
    --models gpt-3.5-turbo gpt-4o-mini \\
    --temperature 0.0 0.7 \\
    --max-tokens 50 100 \\
    --num-examples 20 \\
    --algorithm random \\
    --max-trials 15 \\
    --mock-mode
    
  # List available agents
  %(prog)s --list-agents
        """
    )
    
    # Agent selection
    parser.add_argument(
        '--agent',
        type=str,
        help='Name of the agent to optimize (e.g., support_classifier)'
    )
    
    parser.add_argument(
        '--list-agents',
        action='store_true',
        help='List all available agents and exit'
    )
    
    # Parameter space configuration
    parser.add_argument(
        '--models',
        nargs='+',
        default=None,
        help='Models to test (e.g., gpt-3.5-turbo gpt-4o-mini gpt-4)'
    )
    
    parser.add_argument(
        '--temperature',
        nargs='+',
        type=float,
        default=None,
        help='Temperature values to test (e.g., 0.0 0.5 1.0)'
    )
    
    parser.add_argument(
        '--max-tokens',
        nargs='+',
        type=int,
        default=None,
        help='Max token values to test (e.g., 50 100 200)'
    )
    
    parser.add_argument(
        '--top-p',
        nargs='+',
        type=float,
        default=None,
        help='Top-p (nucleus sampling) values to test (e.g., 0.1 0.5 0.9)'
    )
    
    parser.add_argument(
        '--few-shot-k',
        nargs='+',
        type=int,
        default=None,
        help='Number of few-shot examples to test (e.g., 0 3 5)'
    )
    
    # Agent-specific parameters (LiveBench Competition Math)
    parser.add_argument(
        '--system-role',
        choices=['none', 'minimal', 'standard', 'expert', 'olympiad', 'educator', 'researcher'],
        default=None,
        help='System role for the assistant (LiveBench agent)'
    )
    
    parser.add_argument(
        '--reasoning-style',
        choices=['none', 'basic', 'detailed', 'analytical', 'competition', 'creative', 'rigorous'],
        default=None,
        help='How the model should approach reasoning (LiveBench agent)'
    )
    
    parser.add_argument(
        '--problem-approach',
        choices=['direct', 'decompose', 'pattern', 'construct', 'contradict', 'induction'],
        default=None,
        help='Strategy for solving problems (LiveBench agent)'
    )
    
    parser.add_argument(
        '--answer-format',
        choices=['minimal', 'boxed', 'explained', 'step_numbered', 'latex', 'competition'],
        default=None,
        help='How to format the answer (LiveBench agent)'
    )
    
    parser.add_argument(
        '--notation-style',
        choices=['standard', 'latex', 'plain', 'verbal', 'mixed'],
        default=None,
        help='Mathematical notation preference (LiveBench agent)'
    )
    
    parser.add_argument(
        '--verification-style',
        choices=['none', 'basic', 'thorough', 'explain', 'constraints'],
        default=None,
        help='How to verify answers (LiveBench agent)'
    )
    
    parser.add_argument(
        '--cot-style',
        choices=['none', 'basic', 'detailed', 'reflective', 'structured'],
        default=None,
        help='Chain of thought style (LiveBench agent)'
    )
    
    parser.add_argument(
        '--preset-template',
        choices=['none', 'livebench_minimal', 'livebench_standard', 'competition_solver', 'detailed_educator', 'rigorous_proof'],
        default=None,
        help='Use a preset parameter combination (LiveBench agent)'
    )
    
    # Dataset configuration
    parser.add_argument(
        '--num-examples',
        type=int,
        default=10,
        help='Number of examples to use from dataset (default: 10)'
    )
    
    parser.add_argument(
        '--sampling-strategy',
        choices=['stratified', 'random', 'sequential'],
        default='sequential',
        help='Strategy for sampling examples (default: sequential)'
    )
    
    # Optimization configuration
    parser.add_argument(
        '--algorithm',
        choices=['grid', 'random', 'bayesian'],
        default=None,
        help='Optimization algorithm (auto-selected if not specified)'
    )
    
    parser.add_argument(
        '--max-trials',
        type=int,
        default=None,
        help='Maximum number of trials (default: 10 for random, all for grid up to 100)'
    )
    
    # Parallel execution configuration
    parser.add_argument(
        '--parallel-trials',
        type=int,
        default=None,
        help='Number of parallel trials (between-trial parallelism, default: 1 for sequential)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=None,
        help='Batch size for within-trial parallelism (default: 10)'
    )
    
    parser.add_argument(
        '--max-workers',
        type=int,
        default=None,
        help='Maximum number of workers for batch processing (default: 4)'
    )
    
    parser.add_argument(
        '--adaptive-batching',
        action='store_true',
        default=False,
        help='Enable adaptive batch sizing based on performance'
    )
    
    # Execution configuration
    parser.add_argument(
        '--execution-mode',
        choices=['local', 'cloud', 'hybrid'],
        default='local',
        help='Execution mode (default: local)'
    )
    
    parser.add_argument(
        '--mock-mode',
        action='store_true',
        help='Enable mock mode (no API calls, for testing)'
    )
    
    # Output configuration
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Path to save optimization results (JSON format)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--progress',
        type=str,
        choices=['none', 'simple', 'detailed'],
        default='simple',
        help='Progress tracking mode: none (no progress), simple (basic), detailed (comprehensive)'
    )
    
    return parser


def main():
    """Main entry point."""
    
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Create CLI instance
    cli = TraiGentCLI()
    
    # Handle list agents
    if args.list_agents:
        print("\n📦 Available Agents:")
        print("=" * 50)
        for agent_name in cli.agent_loader.list_agents():
            agent_info = cli.agent_loader.agents[agent_name]
            config = agent_info.config
            print(f"\n• {agent_name}")
            print(f"  Name: {config.get('name', agent_name)}")
            print(f"  Description: {config.get('description', 'No description')}")
            print(f"  Version: {config.get('version', 'Unknown')}")
            print(f"  Objectives: {', '.join(config.get('objectives', ['accuracy']))}")
        return 0
    
    # Check if agent is specified
    if not args.agent:
        print("❌ Error: --agent is required (or use --list-agents to see available agents)")
        parser.print_help()
        return 1
    
    # Check if agent exists
    if args.agent not in cli.agent_loader.list_agents():
        print(f"❌ Error: Agent '{args.agent}' not found")
        print(f"Available agents: {', '.join(cli.agent_loader.list_agents())}")
        return 1
    
    # Run optimization
    return cli.run_optimization(args)


if __name__ == "__main__":
    sys.exit(main())