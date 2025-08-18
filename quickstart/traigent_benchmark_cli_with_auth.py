#!/usr/bin/env python3
"""
TraiGent Advanced Benchmark CLI Tool with Auth Fix and max_trials Fix
This wrapper ensures:
1. The TRAIGENT_API_KEY is sent with all backend requests
2. max_trials is never None (defaults to 50 or calculated from config space)
"""

import os
import sys
import json
import asyncio

# Apply auth fix BEFORE importing traigent
import aiohttp

# Fix 1: Patch aiohttp to include API key in all TraiGent backend requests
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

# Fix 2: Ensure max_trials is never None
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/Traigent')

from traigent.cloud import backend_client
from traigent.cloud import models

# Patch the backend client to ensure max_trials
original_create_session = backend_client.BackendIntegratedClient._create_traigent_session_via_api

async def patched_create_session(self, session_request):
    """Ensure max_trials is never None when sending to backend"""
    if session_request.max_trials is None:
        session_request.max_trials = 50
    return await original_create_session(self, session_request)

backend_client.BackendIntegratedClient._create_traigent_session_via_api = patched_create_session

# Patch SessionCreationRequest
original_session_init = models.SessionCreationRequest.__init__

def patched_session_init(self, *args, **kwargs):
    """Ensure max_trials has a default value"""
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

# Now run the original CLI with the fixes applied
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/quickstart')
from traigent_benchmark_cli import main

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 TraiGent Benchmark CLI with Auth & max_trials Fixes")
    print("=" * 60)
    print("✅ Authorization headers will be automatically added")
    print("✅ max_trials will default to 50 if not specified")
    print("=" * 60)
    print()
    main()