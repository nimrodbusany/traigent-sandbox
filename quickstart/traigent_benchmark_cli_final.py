#!/usr/bin/env python3
"""
TraiGent Advanced Benchmark CLI Tool - FINAL VERSION
This version includes:
1. Auth header fixes for backend communication
2. max_trials fixes to prevent None values
3. Proper mock mode activation to avoid real API calls
4. Fix for SessionCreationRequest connector error
"""

import os
import sys
import json
import asyncio

# Set environment first
os.environ["TRAIGENT_API_KEY"] = "sk_n_8mXqLXt-eIpWeBpcOfoE8gfq44f1TMGYats_rQ-P4"
os.environ["TRAIGENT_BACKEND_URL"] = "http://localhost:5000"
os.environ["TRAIGENT_EXECUTION_MODE"] = "local"
os.environ["TRAIGENT_MOCK_MODE"] = "true"

# Add paths for shared utilities
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/Traigent')
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/quickstart')
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/quickstart/shared_utils')

# Import and setup mock mode BEFORE anything else
from mock_llm import setup_mock_mode
setup_mock_mode()

# Import mock OpenAI patch
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/quickstart/old_scripts')
try:
    from mock_openai_patch import setup_mock_environment
    setup_mock_environment()
except ImportError:
    print("⚠️ Mock OpenAI patch not available, using environment variables only")

# Apply auth and max_trials fixes BEFORE importing traigent
import aiohttp

original_session_init = aiohttp.ClientSession.__init__

def patched_session_init(self, *args, **kwargs):
    """Patch ClientSession to include TraiGent API key and fix max_trials"""
    original_session_init(self, *args, **kwargs)
    original_request = self._request
    
    async def request_with_auth(method, url, **kwargs):
        backend_url = os.environ.get("TRAIGENT_BACKEND_URL", "http://localhost:5000")
        if backend_url in str(url) or "traigent" in str(url).lower():
            api_key = os.environ.get("TRAIGENT_API_KEY")
            if api_key:
                if 'headers' not in kwargs:
                    kwargs['headers'] = {}
                if 'Authorization' not in kwargs['headers']:
                    kwargs['headers']['Authorization'] = f"Bearer {api_key}"
        
        # Fix max_trials in JSON payload
        if 'json' in kwargs and kwargs['json']:
            data = kwargs['json']
            
            # Fix in optimization_config (most important location)
            if 'optimization_config' in data and isinstance(data['optimization_config'], dict):
                if 'max_trials' not in data['optimization_config'] or data['optimization_config'].get('max_trials') is None:
                    data['optimization_config']['max_trials'] = 50
            
            # Fix at root level  
            if 'max_trials' in data and data['max_trials'] is None:
                data['max_trials'] = 50
            
            # Fix in session_config if present
            if 'session_config' in data and isinstance(data['session_config'], dict):
                if 'max_trials' in data['session_config'] and data['session_config']['max_trials'] is None:
                    data['session_config']['max_trials'] = 50
        
        return await original_request(method, url, **kwargs)
    
    self._request = request_with_auth

aiohttp.ClientSession.__init__ = patched_session_init

# Fix SessionCreationRequest connector issue
from traigent.cloud import models

original_session_creation_init = models.SessionCreationRequest.__init__

def patched_session_creation_init(self, *args, **kwargs):
    """Fix SessionCreationRequest to handle unexpected keyword arguments"""
    # Remove any unexpected kwargs that cause errors
    unexpected_keys = ['connector']
    for key in unexpected_keys:
        if key in kwargs:
            kwargs.pop(key)
    
    # Ensure max_trials is never None
    if 'max_trials' not in kwargs or kwargs.get('max_trials') is None:
        kwargs['max_trials'] = 50
    
    original_session_creation_init(self, *args, **kwargs)

models.SessionCreationRequest.__init__ = patched_session_creation_init

print("✅ Applied comprehensive fixes:")
print("   - Authorization headers will be added")
print("   - max_trials will ALWAYS be set (never None)")
print("   - Mock mode activated (no real API calls)")
print("   - SessionCreationRequest connector fix applied")
print()

# Now run the original CLI with all fixes applied
from traigent_benchmark_cli import main

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 TraiGent Benchmark CLI - FINAL FIXED VERSION")
    print("=" * 60)
    print("✅ All known issues fixed:")
    print("   • Auth headers ✅")
    print("   • max_trials ✅")
    print("   • Mock mode ✅")
    print("   • Connector error ✅")
    print("=" * 60)
    print()
    main()