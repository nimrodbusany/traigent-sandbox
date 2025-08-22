"""
Flexible prompt template system for LiveBench Math Agent.

This module provides a composable prompt building system that allows
for extensive customization while maintaining LiveBench compatibility.
"""

from typing import Dict, Any, List, Optional


class PromptTemplateSystem:
    """Composable prompt template system with parameterized components."""
    
    def __init__(self):
        """Initialize the prompt template components."""
        
        # System role templates
        self.system_roles = {
            "none": "",  # No system message (LiveBench minimal)
            "minimal": "You are a helpful assistant.",
            "standard": "You are a helpful assistant that can solve mathematical problems.",
            "expert": "You are an expert mathematician with deep knowledge of {domain}.",
            "olympiad": "You are a Mathematical Olympiad champion skilled in competition mathematics.",
            "educator": "You are a mathematics educator who explains concepts clearly.",
            "researcher": "You are a mathematics researcher with expertise in {domain}."
        }
        
        # Reasoning style templates
        self.reasoning_styles = {
            "none": "",
            "basic": "Think step by step.",
            "detailed": "Break down the problem systematically. Show all your reasoning.",
            "analytical": "Analyze the problem structure before solving. Identify key insights.",
            "competition": "Apply competition problem-solving techniques. Look for elegant solutions.",
            "creative": "Consider multiple approaches. Think creatively about the problem.",
            "rigorous": "Provide rigorous mathematical reasoning with clear logical steps."
        }
        
        # Problem approach templates
        self.problem_approaches = {
            "direct": "Solve the problem directly.",
            "decompose": "Break the problem into smaller subproblems.",
            "pattern": "Look for patterns and apply known techniques.",
            "construct": "Build the solution constructively.",
            "contradict": "Consider proof by contradiction if applicable.",
            "induction": "Use mathematical induction where appropriate."
        }
        
        # Answer format templates
        self.answer_formats = {
            "minimal": "Provide only the final answer.",
            "boxed": "Box your final answer: \\boxed{answer}",
            "explained": "Explain your solution, then clearly state the final answer.",
            "step_numbered": "Number each step of your solution.",
            "latex": "Use LaTeX notation for all mathematical expressions.",
            "competition": "Format according to competition standards (AMC: letter, AIME: 3-digit integer)."
        }
        
        # Math notation preferences
        self.notation_styles = {
            "standard": "Use standard mathematical notation.",
            "latex": "Use LaTeX for all mathematical expressions.",
            "plain": "Use plain text notation (e.g., x^2 for x squared).",
            "verbal": "Explain mathematics verbally when possible.",
            "mixed": "Use the most appropriate notation for clarity."
        }
        
        # Verification instructions
        self.verification_styles = {
            "none": "",
            "basic": "Double-check your answer.",
            "thorough": "Verify your answer by substitution or alternative method.",
            "explain": "Explain why your answer is correct.",
            "constraints": "Verify that your answer satisfies all problem constraints."
        }
        
        # Chain of thought variants
        self.cot_styles = {
            "none": "",
            "basic": "Let's think step by step.",
            "detailed": "I'll work through this problem step by step, showing all reasoning.",
            "reflective": "Let me think about this problem and reflect on the best approach.",
            "structured": "I'll solve this using a structured approach: 1) Understand, 2) Plan, 3) Execute, 4) Verify."
        }
    
    def build_prompt(self, 
                    system_role: str = "minimal",
                    reasoning_style: str = "none",
                    problem_approach: str = "direct",
                    answer_format: str = "minimal",
                    notation_style: str = "standard",
                    verification_style: str = "none",
                    cot_style: str = "none",
                    domain: Optional[str] = None,
                    custom_instructions: Optional[str] = None) -> str:
        """
        Build a complete prompt from component parameters.
        
        Args:
            system_role: Type of system role to use
            reasoning_style: How to approach reasoning
            problem_approach: Strategy for solving problems
            answer_format: How to format the answer
            notation_style: Mathematical notation preference
            verification_style: How to verify answers
            cot_style: Chain of thought style
            domain: Specific mathematical domain (for templates with {domain})
            custom_instructions: Additional custom instructions
            
        Returns:
            Complete composed prompt string
        """
        prompt_parts = []
        
        # Add system role
        if system_role in self.system_roles:
            role_text = self.system_roles[system_role]
            if domain and "{domain}" in role_text:
                role_text = role_text.format(domain=domain)
            if role_text:
                prompt_parts.append(role_text)
        
        # Add reasoning style
        if reasoning_style in self.reasoning_styles and self.reasoning_styles[reasoning_style]:
            prompt_parts.append(self.reasoning_styles[reasoning_style])
        
        # Add problem approach
        if problem_approach in self.problem_approaches:
            prompt_parts.append(self.problem_approaches[problem_approach])
        
        # Add notation style
        if notation_style in self.notation_styles:
            prompt_parts.append(self.notation_styles[notation_style])
        
        # Add answer format
        if answer_format in self.answer_formats:
            prompt_parts.append(self.answer_formats[answer_format])
        
        # Add verification
        if verification_style in self.verification_styles and self.verification_styles[verification_style]:
            prompt_parts.append(self.verification_styles[verification_style])
        
        # Add chain of thought
        if cot_style in self.cot_styles and self.cot_styles[cot_style]:
            prompt_parts.append(self.cot_styles[cot_style])
        
        # Add custom instructions
        if custom_instructions:
            prompt_parts.append(custom_instructions)
        
        # Join with appropriate spacing
        return " ".join(filter(None, prompt_parts))
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        Get the schema for all available parameters.
        
        Returns:
            Dictionary describing all parameters and their options
        """
        return {
            "prompt_engineering": {
                "system_role": {
                    "type": "categorical",
                    "values": list(self.system_roles.keys()),
                    "default": "minimal",
                    "description": "System role for the assistant"
                },
                "reasoning_style": {
                    "type": "categorical",
                    "values": list(self.reasoning_styles.keys()),
                    "default": "none",
                    "description": "How the model should reason"
                },
                "problem_approach": {
                    "type": "categorical",
                    "values": list(self.problem_approaches.keys()),
                    "default": "direct",
                    "description": "Strategy for solving problems"
                },
                "answer_format": {
                    "type": "categorical",
                    "values": list(self.answer_formats.keys()),
                    "default": "minimal",
                    "description": "How to format the answer"
                },
                "notation_style": {
                    "type": "categorical",
                    "values": list(self.notation_styles.keys()),
                    "default": "standard",
                    "description": "Mathematical notation preference"
                },
                "verification_style": {
                    "type": "categorical",
                    "values": list(self.verification_styles.keys()),
                    "default": "none",
                    "description": "How to verify answers"
                },
                "cot_style": {
                    "type": "categorical",
                    "values": list(self.cot_styles.keys()),
                    "default": "none",
                    "description": "Chain of thought style"
                }
            },
            "domain_specific": {
                "domain": {
                    "type": "categorical",
                    "values": ["algebra", "geometry", "number_theory", "combinatorics", "calculus", "probability"],
                    "default": None,
                    "description": "Mathematical domain for specialized prompts"
                },
                "custom_instructions": {
                    "type": "text",
                    "default": "",
                    "description": "Additional custom instructions"
                }
            }
        }
    
    def get_preset_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Get preset parameter combinations for common use cases.
        
        Returns:
            Dictionary of preset templates
        """
        return {
            "livebench_minimal": {
                "system_role": "none",
                "reasoning_style": "none",
                "answer_format": "minimal"
            },
            "livebench_standard": {
                "system_role": "minimal",
                "reasoning_style": "basic",
                "answer_format": "minimal"
            },
            "competition_solver": {
                "system_role": "olympiad",
                "reasoning_style": "competition",
                "problem_approach": "pattern",
                "answer_format": "competition",
                "verification_style": "basic"
            },
            "detailed_educator": {
                "system_role": "educator",
                "reasoning_style": "detailed",
                "problem_approach": "decompose",
                "answer_format": "explained",
                "notation_style": "mixed",
                "verification_style": "explain",
                "cot_style": "structured"
            },
            "rigorous_proof": {
                "system_role": "expert",
                "reasoning_style": "rigorous",
                "problem_approach": "construct",
                "answer_format": "step_numbered",
                "notation_style": "latex",
                "verification_style": "thorough"
            }
        }