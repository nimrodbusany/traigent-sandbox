#!/usr/bin/env python3
"""
Debug TraiGent API key authentication
"""

import os
import sys

# Set the API key
os.environ["TRAIGENT_API_KEY"] = "sk_n_8mXqLXt-eIpWeBpcOfoE8gfq44f1TMGYats_rQ-P4"
os.environ["TRAIGENT_BACKEND_URL"] = "http://localhost:5000"
os.environ["TRAIGENT_EXECUTION_MODE"] = "local"
os.environ["TRAIGENT_MOCK_MODE"] = "true"

print("=" * 60)
print("🔍 DEBUG: TraiGent Authentication Check")
print("=" * 60)
print(f"✅ TRAIGENT_API_KEY: {os.environ.get('TRAIGENT_API_KEY')}")
print(f"✅ TRAIGENT_BACKEND_URL: {os.environ.get('TRAIGENT_BACKEND_URL')}")
print(f"✅ TRAIGENT_EXECUTION_MODE: {os.environ.get('TRAIGENT_EXECUTION_MODE')}")
print(f"✅ TRAIGENT_MOCK_MODE: {os.environ.get('TRAIGENT_MOCK_MODE')}")
print("=" * 60)

# Import TraiGent and check what it's using
sys.path.insert(0, '/home/nimrodbu/projects/traigent-sandbox/Traigent')

try:
    from traigent.cloud.auth import CredentialProvider
    from traigent.cloud.client import CloudClient
    
    print("\n📋 Checking CredentialProvider:")
    provider = CredentialProvider()
    creds = provider.get_credentials()
    
    if creds:
        print(f"  ✅ Found credentials")
        print(f"  📌 API Key: {creds.api_key[:20]}..." if creds.api_key else "  ❌ No API key")
        print(f"  📌 Backend URL: {creds.backend_url}")
        print(f"  📌 Auth Type: {creds.auth_type}")
    else:
        print("  ❌ No credentials found")
    
    print("\n📋 Testing Backend Connection:")
    # Try to create a cloud client
    client = CloudClient(backend_url="http://localhost:5000")
    
    # Check the headers that would be sent
    import aiohttp
    import asyncio
    
    async def test_request():
        """Test a request to the backend"""
        headers = {}
        
        # This is what TraiGent does internally
        if os.environ.get("TRAIGENT_API_KEY"):
            api_key = os.environ.get("TRAIGENT_API_KEY")
            headers["Authorization"] = f"Bearer {api_key}"
            print(f"  ✅ Authorization header will be: Bearer {api_key[:20]}...")
        else:
            print("  ❌ No Authorization header will be sent")
        
        # Try a simple request
        async with aiohttp.ClientSession() as session:
            try:
                url = "http://localhost:5000/api/v1/health"
                print(f"\n  🔗 Testing connection to: {url}")
                print(f"  📤 Headers: {headers}")
                
                async with session.get(url, headers=headers) as response:
                    print(f"  📥 Response status: {response.status}")
                    if response.status == 200:
                        text = await response.text()
                        print(f"  ✅ Backend is healthy: {text[:100]}")
                    else:
                        text = await response.text()
                        print(f"  ❌ Backend error: {text[:200]}")
            except Exception as e:
                print(f"  ❌ Connection error: {e}")
    
    # Run the test
    asyncio.run(test_request())
    
except Exception as e:
    print(f"\n❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("If the backend is running but rejecting the API key,")
print("check that the key is valid and active in the TraiGent system.")
print("=" * 60)