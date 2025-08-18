# TraiGent SDK Bug Report: max_trials Serialization Issue

## Bug Description
The TraiGent SDK is sending `None` for `max_trials` in the session creation request to the backend, causing a TypeError when the backend tries to compare the value.

## Error from Backend Logs
```
TypeError: '>=' not supported between instances of 'int' and 'NoneType'
File "/app/src/services/traigent/session_service.py", line 1084, in _should_continue_optimization
    if completed_count >= max_trials:
```

## Root Cause
In `/Traigent/traigent/cloud/backend_client.py`, line 1008:

```python
"optimization_config": {
    "algorithm": "grid",  # Default algorithm
    "max_trials": session_request.max_trials,  # ⚠️ This can be None!
    "optimization_goal": (
        session_request.objectives[0]
        if session_request.objectives
        else "maximize"
    ),
},
```

When `session_request.max_trials` is `None`, it's sent as `null` in the JSON payload, which the backend doesn't handle properly.

## Why This Happens
1. The `SessionCreationRequest` dataclass has a default value:
   ```python
   max_trials: int = 50  # Default value
   ```

2. BUT if the request is created with `max_trials=None` explicitly or through improper initialization, the None value overrides the default.

3. The SDK doesn't validate or provide a fallback when serializing the request to the backend.

## Impact
- Backend crashes with HTTP 500 error
- Optimization session cannot be created
- Users see "Internal server error" without understanding the cause

## The Fix

### Option 1: Add validation in `_create_traigent_session_via_api`
```python
# In backend_client.py, line 1008
"max_trials": session_request.max_trials or 50,  # Use default if None
```

### Option 2: Validate in SessionCreationRequest creation
```python
# Ensure max_trials is never None when creating the request
if max_trials is None:
    max_trials = 50  # Use default
```

### Option 3: Backend should handle None values
The backend should also be defensive and handle None values:
```python
# Backend side
max_trials = session_data.get("optimization_config", {}).get("max_trials") or 50
```

## Temporary Workaround
Until the SDK is fixed, users should:
1. Always explicitly pass `max_trials` parameter
2. Never pass `None` for max_trials
3. Use the default value of 50 if unsure

## Verification Steps
1. Create an optimization with no max_trials specified
2. Check that the session creation request includes `max_trials: 50` (or another number)
3. Verify the backend accepts the request without errors

## Related Issues
This is likely related to the broader issue of incomplete parameter validation in the SDK's cloud client integration.

## Affected Files
- `/Traigent/traigent/cloud/backend_client.py` (line 1008)
- `/Traigent/traigent/cloud/models.py` (SessionCreationRequest)
- `/Traigent/traigent/cloud/client.py` (session creation methods)

## Severity
**HIGH** - This prevents basic optimization functionality from working when using the backend integration.