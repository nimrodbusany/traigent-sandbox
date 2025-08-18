# TraiGent SDK Bug Report: Missing Authorization Headers

## Bug Description
The TraiGent SDK's `TraiGentCloudClient` class inconsistently includes authentication headers in HTTP requests. Some methods include headers explicitly, while others rely on session defaults that may not be set.

## Root Cause
In `/Traigent/traigent/cloud/client.py`:

1. **Session created with headers** (line 237-240):
```python
self._session = aiohttp.ClientSession(
    headers=await self.auth.get_headers(),
)
```

2. **Some methods explicitly add headers**:
- Line 953: `headers=await self._get_headers()`
- Line 1017: `headers=await self._get_headers()`
- Line 1056: `headers=await self._get_headers()`
- Line 1093: `headers=await self._get_headers()`

3. **BUT many methods DON'T add headers**:
- Line 567: `async with self._session.post(url, json=request_data)`
- Line 608: `async with self._session.post(url, json=request_data)`
- Line 673: `async with self._session.post(url, json=request_data)`
- Line 709: `async with self._session.post(url, json=request_data)`

## Impact
- Authentication fails when the backend enforces API key validation
- Inconsistent behavior depending on which methods are called
- Works only if session default headers are properly set

## Recommended Fix

### Option 1: Add headers to ALL requests
```python
# Change all session.post() calls to include headers
async with self._session.post(
    url, 
    json=request_data,
    headers=await self._get_headers()  # Add this line
) as response:
```

### Option 2: Ensure session always has default headers
Create a helper method that ensures headers are always present:
```python
async def _ensure_session(self):
    """Ensure session exists with current auth headers."""
    if not self._session:
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers=await self.auth.get_headers(),
        )
    return self._session
```

Then use `await self._ensure_session()` before any request.

## Affected Methods
- `create_optimization_session()` - Line 567
- `get_next_trial()` - Line 608  
- `submit_trial_result()` - Line 673
- `finalize_optimization_session()` - Line 709

## Workaround
Until the SDK is fixed, users can:
1. Always use the client as a context manager
2. Apply the monkey-patch we created in `traigent_benchmark_cli_with_auth.py`
3. Ensure TRAIGENT_API_KEY is set before importing traigent

## Verification
The bug can be verified by:
1. Setting TRAIGENT_API_KEY environment variable
2. Running optimization with `execution_mode="local"`
3. Monitoring HTTP requests to see missing Authorization headers
4. Observing authentication failures from the backend