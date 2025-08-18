#!/usr/bin/env python3
"""
TraiGent Benchmark CLI with ALL SDK Bug Fixes Applied
This version fixes both auth headers AND max_trials issues
"""

import os
import sys

# Apply fixes BEFORE importing anything from TraiGent
print("=" * 60)
print("🔧 TraiGent Benchmark CLI with SDK Fixes")
print("=" * 60)

# Fix 1: Auth headers for TraiGent backend
import aiohttp
original_session_init = aiohttp.ClientSession.__init__

def patched_session_init(self, *args, **kwargs):
    """Patch ClientSession to always include TraiGent API key in headers"""
    original_session_init(self, *args, **kwargs)
    original_request = self._request
    
    async def request_with_auth(method, url, **kwargs):
        """Add TraiGent API key to all backend requests"""
        backend_url = os.environ.get("TRAIGENT_BACKEND_URL", "http://localhost:5000")
        if backend_url in str(url) or "traigent" in str(url).lower():
            api_key = os.environ.get("TRAIGENT_API_KEY")
            if api_key:
                if 'headers' not in kwargs:
                    kwargs['headers'] = {}
                if 'Authorization' not in kwargs['headers']:
                    kwargs['headers']['Authorization'] = f"Bearer {api_key}"
        return await original_request(method, url, **kwargs)
    
    self._request = request_with_auth

aiohttp.ClientSession.__init__ = patched_session_init
print("✅ Fix 1: Authorization headers will be added automatically")

# Fix 2: Patch TraiGent to ensure max_trials is never None
# We need to patch this BEFORE importing TraiGent
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/Traigent')

# Import the backend client module
from traigent.cloud import backend_client
from traigent.cloud import models

# Patch SessionCreationRequest to ensure max_trials is never None
original_session_creation_init = models.SessionCreationRequest.__init__

def patched_session_creation_init(self, *args, **kwargs):
    """Ensure max_trials is never None"""
    # If max_trials is None or not provided, set to default
    if 'max_trials' not in kwargs or kwargs.get('max_trials') is None:
        kwargs['max_trials'] = 50
    original_session_creation_init(self, *args, **kwargs)

models.SessionCreationRequest.__init__ = patched_session_creation_init

# Also patch the backend client method that creates sessions
original_create_session = backend_client.BackendIntegratedClient._create_traigent_session_via_api

async def patched_create_session(self, session_request):
    """Ensure max_trials is never None when sending to backend"""
    # Double-check max_trials is not None
    if session_request.max_trials is None:
        session_request.max_trials = 50
    
    # Also patch the data being sent directly
    result = await original_create_session(self, session_request)
    return result

backend_client.BackendIntegratedClient._create_traigent_session_via_api = patched_create_session

print("✅ Fix 2: max_trials will always have a value (default: 50)")

# Fix 3: Also patch the OptimizationRequest to ensure max_trials
from traigent.cloud import service

original_opt_request_init = service.OptimizationRequest.__init__

def patched_opt_request_init(self, *args, **kwargs):
    """Ensure max_trials is never None in OptimizationRequest"""
    if 'max_trials' not in kwargs or kwargs.get('max_trials') is None:
        kwargs['max_trials'] = 50
    original_opt_request_init(self, *args, **kwargs)

if hasattr(service, 'OptimizationRequest'):
    service.OptimizationRequest.__init__ = patched_opt_request_init

# Also patch the models version
if hasattr(models, 'OptimizationRequest'):
    original_models_opt_init = models.OptimizationRequest.__init__
    
    def patched_models_opt_init(self, *args, **kwargs):
        if 'max_trials' not in kwargs or kwargs.get('max_trials') is None:
            kwargs['max_trials'] = 50
        original_models_opt_init(self, *args, **kwargs)
    
    models.OptimizationRequest.__init__ = patched_models_opt_init

print("✅ Fix 3: OptimizationRequest will always have max_trials")

# Now patch the optimize decorator to ensure max_trials
import traigent

original_optimize = traigent.optimize

def patched_optimize(*args, **kwargs):
    """Ensure max_trials is never None in optimize decorator"""
    if 'max_trials' not in kwargs or kwargs.get('max_trials') is None:
        # Calculate based on configuration space if possible
        if 'configuration_space' in kwargs:
            config_space = kwargs['configuration_space']
            total_configs = 1
            for param, values in config_space.items():
                if isinstance(values, list):
                    total_configs *= len(values)
            # Use total configs but cap at 50 for safety
            kwargs['max_trials'] = min(total_configs, 50)
        else:
            kwargs['max_trials'] = 50
    
    return original_optimize(*args, **kwargs)

traigent.optimize = patched_optimize
print("✅ Fix 4: @traigent.optimize will auto-calculate max_trials")

print("=" * 60)
print("✅ All SDK fixes applied successfully!")
print("=" * 60)
print()

# Now import and run the original CLI
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/quickstart')
from traigent_benchmark_cli import main

if __name__ == "__main__":
    # Check if there's piped input
    import select
    
    # If there's piped input, the CLI might not handle it well
    # So we'll just pass through to the main function
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)