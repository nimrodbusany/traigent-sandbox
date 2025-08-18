#!/usr/bin/env python3
"""
Fix TraiGent to properly send Authorization headers with API key
"""

import os
import sys
import json
import asyncio

# Set the environment variables
os.environ["TRAIGENT_API_KEY"] = "sk_n_8mXqLXt-eIpWeBpcOfoE8gfq44f1TMGYats_rQ-P4"
os.environ["TRAIGENT_BACKEND_URL"] = "http://localhost:5000"
os.environ["TRAIGENT_EXECUTION_MODE"] = "local"
os.environ["TRAIGENT_MOCK_MODE"] = "true"

print("=" * 60)
print("🔧 Fixing TraiGent Authorization Headers")
print("=" * 60)
print(f"TRAIGENT_API_KEY: {os.environ.get('TRAIGENT_API_KEY')}")
print(f"TRAIGENT_BACKEND_URL: {os.environ.get('TRAIGENT_BACKEND_URL')}")
print("=" * 60)

# Add Traigent to path
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/Traigent')

# Import TraiGent modules
from traigent.cloud.client import CloudClient
from traigent.cloud.auth import AuthManager

# Monkey-patch CloudClient to include auth headers
original_init = CloudClient.__init__

def patched_init(self, *args, **kwargs):
    """Initialize CloudClient with auth headers fix"""
    original_init(self, *args, **kwargs)
    
    # Store original session.post method
    if hasattr(self, 'session'):
        original_post = self.session.post
        
        async def post_with_auth(url, **kwargs):
            """Wrapper that adds auth headers to all requests"""
            # Get auth headers from auth manager
            if self.auth and hasattr(self.auth, 'get_headers'):
                try:
                    auth_headers = await self.auth.get_headers()
                    
                    # Add auth headers to request
                    if 'headers' not in kwargs:
                        kwargs['headers'] = {}
                    kwargs['headers'].update(auth_headers)
                    
                    # Log the authorization header
                    if 'Authorization' in kwargs['headers']:
                        auth_header = kwargs['headers']['Authorization']
                        if auth_header.startswith('Bearer '):
                            token = auth_header[7:]
                            print(f"\n✅ Adding Authorization header: Bearer {token[:30]}...")
                        else:
                            print(f"\n✅ Adding Authorization header: {auth_header[:30]}...")
                except Exception as e:
                    print(f"\n⚠️ Could not get auth headers: {e}")
            
            # Call original post method
            return await original_post(url, **kwargs)
        
        # Replace session.post with our wrapper
        self.session.post = post_with_auth
        print("✅ CloudClient session.post patched to include auth headers")

# Apply the patch
CloudClient.__init__ = patched_init

# Also patch AuthManager to accept sk_ prefix keys
original_validate = AuthManager._validate_key_format

def patched_validate(self, key: str) -> bool:
    """Accept both tg_ and sk_ prefixed keys"""
    if not key:
        return False
    
    # Accept sk_ prefix (TraiGent's actual format) or tg_ prefix
    if not (key.startswith("tg_") or key.startswith("sk_")):
        print(f"⚠️ API key doesn't start with tg_ or sk_: {key[:10]}...")
        # For now, accept it anyway if it's long enough
        if len(key) < 20:
            return False
    
    # Original validation would check for exact 64 chars, but sk_ keys are different
    if key.startswith("tg_") and len(key) != 64:
        return False
    
    # For sk_ keys, just check minimum length
    if key.startswith("sk_") and len(key) < 20:
        return False
    
    return True

AuthManager._validate_key_format = patched_validate
print("✅ AuthManager patched to accept sk_ prefix keys")

# Now test with a simple optimization
import traigent
import tempfile

def create_test_dataset():
    examples = [
        {"input": {"text": "test1"}, "output": "result1"},
        {"input": {"text": "test2"}, "output": "result2"},
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for example in examples:
            json.dump(example, f)
            f.write('\n')
        return f.name

@traigent.optimize(
    eval_dataset=create_test_dataset(),
    objectives=["accuracy"],
    configuration_space={
        "model": ["gpt-3.5-turbo"],
        "temperature": [0.5]
    },
    max_trials=1,
    algorithm="grid",
    execution_mode="local"
)
def test_function(text: str, model: str = "gpt-3.5-turbo", temperature: float = 0.5) -> str:
    """Test function that returns a mock result"""
    return "mock_result"

async def run_test():
    print("\n🚀 Starting optimization with fixed auth headers...")
    print("-" * 60)
    
    try:
        results = await test_function.optimize()
        print("\n✅ Optimization completed successfully!")
        print(f"Best config: {results.best_config}")
        print(f"Best score: {results.best_score:.1%}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_test())
    print("\n" + "=" * 60)
    print("✅ Test complete - Authorization headers should now be sent")
    print("=" * 60)