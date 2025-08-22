"""
LiveBench Math Agent for TraiGent Optimization

This agent interfaces with LiveBench's actual math datasets and evaluation methods.
It downloads problems from LiveBench and uses their evaluation criteria.

LiveBench Math Categories:
- math_competition_problems: AMC, AIME, IMO problems
- amps_hard: Advanced mathematical problem solving
- proof_rearrangement: Mathematical proof tasks
"""

import openai
import json
import os
from typing import List, Dict, Any, Optional
import requests
from pathlib import Path

# Import our flexible prompt template system
import sys
from pathlib import Path
agent_dir = Path(__file__).parent
sys.path.insert(0, str(agent_dir))
from prompt_templates import PromptTemplateSystem


class LiveBenchMathAgent:
    """LiveBench math problem solving agent using actual LiveBench data."""
    
    def __init__(self):
        """Initialize the LiveBench math agent."""
        self.name = "livebench_math"
        self.description = "Solves LiveBench mathematical problems using their datasets and evaluation"
        self.livebench_categories = [
            "math_competition_problems",
            "amps_hard", 
            "proof_rearrangement"
        ]
        # Initialize the flexible prompt template system
        self.prompt_system = PromptTemplateSystem()
        
    def create_function(self, prompt_builder, example_selector):
        """
        Create the optimizable function for TraiGent.
        
        Args:
            prompt_builder: PromptBuilder instance for building messages
            example_selector: ExampleSelector instance for few-shot examples
            
        Returns:
            The function to be optimized by TraiGent
        """
        def solve_livebench_math(
            problem: str,
            task: str = None,
            category: str = None,
            # Core LLM parameters
            model: str = "gpt-4o",
            temperature: float = 0.1,
            max_tokens: int = 1000,
            top_p: float = 0.95,
            # Few-shot parameters
            few_shot_k: int = 0,
            few_shot_strategy: str = "similar",
            # Prompt engineering parameters (new flexible system)
            system_role: str = "minimal",
            reasoning_style: str = "none",
            problem_approach: str = "direct",
            answer_format: str = "minimal",
            notation_style: str = "standard",
            verification_style: str = "none",
            cot_style: str = "none",
            # Domain-specific parameters
            domain: Optional[str] = None,
            custom_instructions: Optional[str] = None,
            # Preset template (overrides individual params if set)
            preset_template: Optional[str] = None
        ) -> str:
            """
            Solve LiveBench math problems with TraiGent optimization.
            Now with flexible prompt engineering parameters!
            """
            
            # Handle preset templates
            if preset_template:
                presets = self.prompt_system.get_preset_templates()
                if preset_template in presets:
                    # Override parameters with preset values
                    preset_params = presets[preset_template]
                    system_role = preset_params.get('system_role', system_role)
                    reasoning_style = preset_params.get('reasoning_style', reasoning_style)
                    problem_approach = preset_params.get('problem_approach', problem_approach)
                    answer_format = preset_params.get('answer_format', answer_format)
                    notation_style = preset_params.get('notation_style', notation_style)
                    verification_style = preset_params.get('verification_style', verification_style)
                    cot_style = preset_params.get('cot_style', cot_style)
            
            # Build the system prompt using our flexible template system
            system_prompt = self.prompt_system.build_prompt(
                system_role=system_role,
                reasoning_style=reasoning_style,
                problem_approach=problem_approach,
                answer_format=answer_format,
                notation_style=notation_style,
                verification_style=verification_style,
                cot_style=cot_style,
                domain=domain,
                custom_instructions=custom_instructions
            )
            
            # Build messages
            messages = []
            
            # Add system message if not empty
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add few-shot examples if requested
            if few_shot_k > 0:
                few_shot_examples = example_selector.select_examples(
                    k=few_shot_k,
                    strategy=few_shot_strategy,
                    query_text=problem
                )
                for example in few_shot_examples:
                    if "turns" in example and example["turns"]:
                        messages.append({"role": "user", "content": example["turns"][0]})
                    elif "question" in example:
                        messages.append({"role": "user", "content": example["question"]})
                    
                    if "ground_truth" in example:
                        messages.append({"role": "assistant", "content": example["ground_truth"]})
            
            # Add the current problem
            messages.append({"role": "user", "content": problem})
            
            # Create OpenAI API call with TraiGent parameter injection
            response = openai.chat.completions.create(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                messages=messages
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("No content in response")
            
            # Format answer according to LiveBench expectations
            return prompt_builder.format_answer_for_livebench(content, answer_format)
        
        return solve_livebench_math
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        Get the complete parameter schema for this agent.
        
        This method is used by the HTML CLI generator and TraiGent
        to discover all available parameters dynamically.
        
        Returns:
            Dictionary describing all parameters and their options
        """
        # Get the prompt engineering schema from our template system
        prompt_schema = self.prompt_system.get_parameter_schema()
        
        # Combine with agent-specific parameters
        return {
            "core_llm": {
                "model": {
                    "type": "categorical",
                    "values": ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o", "gpt-4", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                    "default": "gpt-4o",
                    "description": "LLM model to use"
                },
                "temperature": {
                    "type": "continuous",
                    "values": [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9],
                    "default": 0.1,
                    "description": "Temperature for generation"
                },
                "max_tokens": {
                    "type": "discrete",
                    "values": [500, 1000, 1500, 2000],
                    "default": 1000,
                    "description": "Maximum tokens to generate"
                },
                "top_p": {
                    "type": "continuous",
                    "values": [0.9, 0.95, 1.0],
                    "default": 0.95,
                    "description": "Nucleus sampling threshold"
                }
            },
            "few_shot": {
                "few_shot_k": {
                    "type": "discrete",
                    "values": [0, 1, 2, 3, 5],
                    "default": 0,
                    "description": "Number of examples to include"
                },
                "few_shot_strategy": {
                    "type": "categorical",
                    "values": ["random", "similar", "diverse"],
                    "default": "similar",
                    "description": "Strategy for selecting examples"
                }
            },
            **prompt_schema,  # Include all prompt engineering parameters
            "presets": {
                "preset_template": {
                    "type": "categorical",
                    "values": ["none"] + list(self.prompt_system.get_preset_templates().keys()),
                    "default": "none",
                    "description": "Use a preset parameter combination"
                }
            }
        }


class PromptBuilder:
    """Build prompts specifically for LiveBench math problems."""
    
    def __init__(self):
        # LiveBench uses minimal system prompts - just basic assistant role
        # They rely on the question format itself to guide the model
        self.system_roles = {
            "livebench_default": """A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.""",
            
            "livebench_minimal": "",  # LiveBench often uses no system message at all
            
            "livebench_math": """You are a helpful assistant that can solve mathematical problems. Answer questions directly and precisely."""
        }
        
        self.solution_approaches = {
            "systematic": "Work through the problem step-by-step, showing all work clearly.",
            "pattern_matching": "Look for patterns and apply known competition techniques.",
            "direct": "Apply formulas and theorems directly to reach the solution.",
            "construction": "Build the solution constructively from first principles."
        }
        
        self.answer_formats = {
            "livebench_standard": "Format your answer exactly as LiveBench expects (numerical value, proof steps, or letter choice).",
            "amc_format": "For AMC problems, give only the letter choice (A, B, C, D, or E).",
            "aime_format": "For AIME problems, give an integer between 000 and 999.",
            "proof_format": "Number each step of your proof clearly."
        }
    
    def build_system_message(self, role: str, solution_approach: str, 
                           answer_format: str, show_work: bool) -> str:
        """Build system message for LiveBench math problems."""
        
        # LiveBench uses very minimal system prompts
        base_role = self.system_roles.get(role, self.system_roles["livebench_default"])
        
        # For LiveBench, we keep it simple - they don't add extensive instructions
        # The questions themselves contain the format requirements
        if role == "livebench_minimal":
            return ""  # No system message, like LiveBench often does
        
        return base_role
    
    def build_messages(self, 
                      text: str,
                      system_role: str = "livebench_default",
                      solution_approach: str = "systematic",
                      few_shot_examples: List[Dict] = None,
                      show_work: bool = True,
                      use_chain_of_thought: bool = True,
                      answer_format: str = "livebench_standard") -> List[Dict]:
        """Build messages for LiveBench math problems."""
        
        messages = []
        
        # System message (LiveBench keeps this minimal)
        system_content = self.build_system_message(
            system_role, solution_approach, answer_format, show_work
        )
        
        # Only add system message if not empty
        if system_content:
            messages.append({"role": "system", "content": system_content})
        
        # LiveBench doesn't typically use few-shot examples in the conversation
        # They pass the question directly
        
        # Current problem - this is exactly how LiveBench does it
        messages.append({"role": "user", "content": text})
        
        return messages
    
    def format_answer_for_livebench(self, response: str, answer_format: str) -> str:
        """Format the answer according to LiveBench expectations."""
        
        # Extract different answer formats based on problem type
        if "amc" in answer_format.lower():
            # Look for letter choice
            import re
            match = re.search(r'\b([A-E])\b', response.upper())
            if match:
                return match.group(1)
                
        elif "aime" in answer_format.lower():
            # Look for three-digit number
            import re
            # Find all numbers and look for one that's 3 digits or less
            numbers = re.findall(r'\b\d{1,3}\b', response)
            if numbers:
                # Return the last number found, padded to 3 digits
                return numbers[-1].zfill(3)
                
        elif "proof" in answer_format.lower():
            # Return the full proof
            return response.strip()
            
        # Default: try to extract the final answer
        lines = response.strip().split('\n')
        for line in reversed(lines):
            line = line.strip()
            if line and not line.startswith('#'):
                # Check if it looks like an answer
                if any(phrase in line.lower() for phrase in ['answer:', 'therefore', 'thus', 'so']):
                    # Extract the part after the keyword
                    for phrase in ['answer:', 'therefore', 'thus', 'so']:
                        if phrase in line.lower():
                            parts = line.lower().split(phrase)
                            if len(parts) > 1:
                                return parts[1].strip()
                # Return the line if it looks like a final answer
                if line and len(line) < 100:  # Reasonable answer length
                    return line
        
        return response.strip()


class ExampleSelector:
    """Select examples from LiveBench datasets."""
    
    def __init__(self, dataset: List[Dict]):
        """Initialize with LiveBench dataset format."""
        self.dataset = dataset
    
    def select_examples(self, k: int, strategy: str, query_text: str = None) -> List[Dict]:
        """Select k examples from LiveBench data."""
        
        if k <= 0 or not self.dataset:
            return []
        
        import random
        
        if strategy == "random":
            return random.sample(self.dataset, min(k, len(self.dataset)))
        
        elif strategy == "similar":
            # For LiveBench, we'd ideally use the same task type
            # For now, use random selection
            return random.sample(self.dataset, min(k, len(self.dataset)))
        
        elif strategy == "diverse":
            # Try to get examples from different tasks
            selected = []
            tasks = list(set(ex.get('task', '') for ex in self.dataset))
            
            for i in range(k):
                task = tasks[i % len(tasks)] if tasks else None
                task_examples = [ex for ex in self.dataset if ex.get('task') == task]
                
                if task_examples:
                    available = [ex for ex in task_examples if ex not in selected]
                    if available:
                        selected.append(random.choice(available))
            
            # Fill remaining with random
            while len(selected) < k and len(selected) < len(self.dataset):
                remaining = [ex for ex in self.dataset if ex not in selected]
                if remaining:
                    selected.append(random.choice(remaining))
                else:
                    break
            
            return selected
        
        else:
            return random.sample(self.dataset, min(k, len(self.dataset)))


class LiveBenchDataLoader:
    """Load LiveBench math datasets."""
    
    @staticmethod
    def download_livebench_math():
        """
        Download LiveBench math questions.
        
        Note: In production, this would use the actual LiveBench API or HuggingFace datasets.
        For now, this returns a structure compatible with LiveBench format.
        """
        # This would normally download from:
        # https://huggingface.co/datasets/livebench/livebench
        
        print("Note: To use actual LiveBench data, install and run:")
        print("  git clone https://github.com/livebench/livebench")
        print("  cd livebench && pip install -e .")
        print("  python -m livebench.download_questions")
        
        # Return empty structure for now
        return {
            "math_competition_problems": [],
            "amps_hard": [],
            "proof_rearrangement": []
        }
    
    @staticmethod
    def load_from_file(filepath: str) -> List[Dict]:
        """Load LiveBench format JSONL file."""
        questions = []
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                for line in f:
                    if line.strip():
                        questions.append(json.loads(line))
        return questions