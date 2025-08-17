# 🚨 CRITICAL: Fix HTTP 500 Errors in TraiGent Examples

**Priority**: High  
**Impact**: User Experience - New users see ERROR messages  
**Complexity**: Low (Simple parameter addition)  
**Estimated Fix Time**: 5 minutes  

## 🔍 Problem Description

TraiGent SDK examples are causing HTTP 500 errors during optimization due to missing `max_trials` parameter. This creates a poor first impression for new users who see ERROR messages in logs, even though the optimization works.

## 📋 Error Details

**Error Message**:
```
2025-08-17 11:50:33,914 - traigent.cloud.backend_client - ERROR - ❌ Failed to submit trial result: HTTP 500
2025-08-17 11:50:33,914 - traigent.cloud.backend_client - ERROR -    Error message: {
  "error": "Internal server error"
}
```

**Backend Stack Trace**:
```python
# session_service.py:1082
if session_state["completed_count"] >= max_trials:
# TypeError: '>=' not supported between instances of 'int' and 'NoneType'
```

## 🎯 Root Cause Analysis

1. **SDK Examples**: Not passing `max_trials` parameter to `.optimize()` calls
2. **Backend receives**: `max_trials=None` 
3. **Backend crashes**: When comparing `int >= None` in session management logic
4. **User sees**: HTTP 500 errors (but optimization still works via local fallback)

**Evidence**:
```bash
# BEFORE (broken):
2025-08-17 12:17:21,655 - INFO - Starting optimization: max_trials=None
# → Results in HTTP 500 errors

# AFTER (fixed):  
2025-08-17 12:24:35,833 - INFO - Starting optimization: max_trials=10
# → Zero HTTP 500 errors
```

## 🛠️ Solution

**Fix Required**: Add `max_trials` parameter to `.optimize()` calls in examples

### Files to Update

**Primary File**: `examples/quickstart/basic_optimization.py`

**Line ~131**:
```python
# BEFORE (causes HTTP 500):
results = await classify_support_query.optimize()

# AFTER (fixes HTTP 500):
results = await classify_support_query.optimize(max_trials=10)
```

### Additional Files Likely Needing Same Fix

Search for other examples with similar pattern:
```bash
grep -r "\.optimize()" examples/
```

Look for calls missing `max_trials` parameter and add it consistently.

## ✅ Verification Steps

1. **Before Fix**: Run example and confirm HTTP 500 errors in logs
2. **Apply Fix**: Add `max_trials=10` to `.optimize()` call  
3. **After Fix**: Run example and confirm zero HTTP 500 errors
4. **Verify Logs**: Should see `max_trials=10` instead of `max_trials=None`

**Test Command**:
```bash
cd examples
PYTHONPATH=$(pwd) python quickstart/basic_optimization.py 2>&1 | grep -E "(HTTP 500|max_trials)"
```

## 📊 Impact Assessment

**Before Fix**:
- ❌ Users see scary ERROR messages in logs
- ✅ Optimization still works (SDK has graceful fallback)
- ❌ Poor first impression for new users

**After Fix**:
- ✅ Clean logs with no errors
- ✅ Optimization works perfectly  
- ✅ Professional user experience

## 🔧 Implementation Notes

1. **Recommended Value**: `max_trials=10` (reasonable default for examples)
2. **Scope**: All examples that use `.optimize()` without explicit `max_trials`
3. **Backward Compatibility**: This change is additive and safe
4. **Documentation**: Consider mentioning `max_trials` parameter in example comments

## 🎯 Success Criteria

- [ ] Zero HTTP 500 errors in example execution logs
- [ ] Backend logs show `max_trials=10` instead of `max_trials=None`  
- [ ] All examples complete successfully with clean output
- [ ] New user validation script passes without backend errors

---

**Reporter**: Claude Code SDK Validation  
**Date**: 2025-08-17  
**Validation Method**: Fresh environment testing with comprehensive validation script