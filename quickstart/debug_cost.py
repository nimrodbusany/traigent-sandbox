#!/usr/bin/env python3
"""Debug script to test tokencost calculation directly."""

import json
from tokencost import calculate_prompt_cost, calculate_completion_cost

# Test direct tokencost calls
model_name = "gpt-3.5-turbo"
test_prompt = [{"role": "user", "content": "Classify this support ticket: My app crashes when I upload files"}]
test_response = "technical"

print("🧪 Testing tokencost directly...")
print(f"Model: {model_name}")
print(f"Prompt: {test_prompt}")
print(f"Response: {test_response}")

try:
    input_cost = calculate_prompt_cost(test_prompt, model_name)
    output_cost = calculate_completion_cost(test_response, model_name)
    total_cost = input_cost + output_cost
    
    print(f"\n💰 Cost Calculation Results:")
    print(f"   Input cost: ${input_cost:.6f}")
    print(f"   Output cost: ${output_cost:.6f}")  
    print(f"   Total cost: ${total_cost:.6f}")
    
    if total_cost > 0:
        print("✅ tokencost is working correctly!")
    else:
        print("❌ tokencost returned 0 cost")
        
except Exception as e:
    print(f"❌ tokencost failed: {e}")
    import traceback
    traceback.print_exc()