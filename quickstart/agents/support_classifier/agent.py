"""
Support Classifier Agent for TraiGent Optimization

This agent classifies customer support tickets into categories:
- technical: Technical issues, bugs, errors
- billing: Payment, subscription, charges
- general: General inquiries, business hours
"""

import openai
from typing import List, Dict, Any


class SupportClassifierAgent:
    """Customer support ticket classification agent."""
    
    def __init__(self):
        """Initialize the support classifier agent."""
        self.name = "support_classifier"
        self.description = "Classifies customer support tickets into technical, billing, or general categories"
        
    def create_function(self, prompt_builder, example_selector):
        """
        Create the optimizable function for TraiGent.
        
        Args:
            prompt_builder: PromptBuilder instance for building messages
            example_selector: ExampleSelector instance for few-shot examples
            
        Returns:
            The function to be optimized by TraiGent
        """
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


class PromptBuilder:
    """Build dynamic prompts based on parameters."""
    
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
        """Build system message from components."""
        base_role = self.system_roles.get(role, self.system_roles["classifier"])
        format_instruction = self.output_formats.get(output_format, self.output_formats["single_word"])
        style_instruction = self.styles.get(style, "")
        
        system_msg = f"{base_role}\n\n{format_instruction}"
        if style_instruction:
            system_msg += f"\n\n{style_instruction}"
        
        return system_msg
    
    def format_few_shot_examples(self, examples: List[Dict]) -> List[Dict]:
        """Format examples as conversation messages."""
        messages = []
        for example in examples:
            # Handle both formats
            if isinstance(example["input"], dict) and "text" in example["input"]:
                input_text = example["input"]["text"]
            else:
                input_text = example["input"]
            messages.append({"role": "user", "content": input_text})
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
        """Build complete message array for LLM."""
        
        messages = []
        
        # System message
        system_content = self.build_system_message(system_role, output_format, style)
        if context:
            system_content += f"\n\nContext: {context}"
        if chain_of_thought:
            system_content += "\n\nThink step by step before providing your answer."
        
        messages.append({"role": "system", "content": system_content})
        
        # Few-shot examples
        if few_shot_examples:
            messages.extend(self.format_few_shot_examples(few_shot_examples))
        
        # User query
        messages.append({"role": "user", "content": text})
        
        return messages


class ExampleSelector:
    """Handle few-shot example selection strategies."""
    
    def __init__(self, dataset: List[Dict]):
        self.dataset = dataset
    
    def select_examples(self, k: int, strategy: str, query_example: Dict = None) -> List[Dict]:
        """Select k examples using specified strategy."""
        import random
        
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