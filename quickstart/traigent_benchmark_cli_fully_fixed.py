#!/usr/bin/env python3
"""
TraiGent Benchmark CLI with COMPLETE fixes for all SDK bugs
This version ensures max_trials is ALWAYS sent properly
"""

import os
import sys
import json

# Set environment first
os.environ["TRAIGENT_API_KEY"] = "sk_n_8mXqLXt-eIpWeBpcOfoE8gfq44f1TMGYats_rQ-P4"
os.environ["TRAIGENT_BACKEND_URL"] = "http://localhost:5000"

# Apply comprehensive fixes BEFORE importing traigent
import aiohttp

# Fix 1: Auth headers
original_session_init = aiohttp.ClientSession.__init__

def patched_session_init(self, *args, **kwargs):
    """Patch ClientSession to include TraiGent API key"""
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
        
        # ALSO fix the JSON data to ensure max_trials is never None
        if 'json' in kwargs and kwargs['json']:
            data = kwargs['json']
            
            # Fix max_trials in optimization_config
            if 'optimization_config' in data:
                if 'max_trials' not in data['optimization_config'] or data['optimization_config'].get('max_trials') is None:
                    data['optimization_config']['max_trials'] = 50
                    print(f"🔧 Fixed max_trials in optimization_config: set to 50")
            
            # Fix max_trials at root level
            if 'max_trials' in data and data['max_trials'] is None:
                data['max_trials'] = 50
                print(f"🔧 Fixed max_trials at root: set to 50")
            
            # Fix in session_config if present
            if 'session_config' in data and data['session_config']:
                if 'max_trials' in data['session_config'] and data['session_config']['max_trials'] is None:
                    data['session_config']['max_trials'] = 50
                    print(f"🔧 Fixed max_trials in session_config: set to 50")
        
        return await original_request(method, url, **kwargs)
    
    self._request = request_with_auth

aiohttp.ClientSession.__init__ = patched_session_init

print("✅ Applied comprehensive fixes:")
print("   - Authorization headers will be added")
print("   - max_trials will ALWAYS be set (never None)")
print()

# Fix 2: Patch TraiGent modules
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/Traigent')

from traigent.cloud import backend_client
from traigent.cloud import models

# Ensure SessionCreationRequest always has max_trials
original_session_init = models.SessionCreationRequest.__init__

def patched_session_init(self, *args, **kwargs):
    """Ensure max_trials is never None"""
    if 'max_trials' not in kwargs or kwargs.get('max_trials') is None:
        kwargs['max_trials'] = 50
    original_session_init(self, *args, **kwargs)

models.SessionCreationRequest.__init__ = patched_session_init

# Also patch OptimizationRequest
if hasattr(models, 'OptimizationRequest'):
    original_opt_init = models.OptimizationRequest.__init__
    
    def patched_opt_init(self, *args, **kwargs):
        if 'max_trials' not in kwargs or kwargs.get('max_trials') is None:
            kwargs['max_trials'] = 50
        original_opt_init(self, *args, **kwargs)
    
    models.OptimizationRequest.__init__ = patched_opt_init

# Now run the original CLI
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/quickstart')
from traigent_benchmark_cli import main

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 TraiGent Benchmark CLI - Fully Fixed Version")
    print("=" * 60)
    main()