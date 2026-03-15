# Gmail OAuth Scope Conflict - Issue and Resolution

## Problem Summary

**Issue:** Gmail Watcher stopped working after MCP email sending was tested, failing with:
```
('invalid_scope: Bad Request', {'error': 'invalid_scope', 'error_description': 'Bad Request'})
```

**Root Cause:** OAuth scope conflict between two components sharing the same token file.

---

## Technical Analysis

### The Conflict

Both Gmail Watcher and MCP send_email use the same OAuth token file (`credentials/gmail_token.json`) but were requesting different scopes:

**Before Fix:**

1. **Gmail Watcher** (`gmail_watcher_skill.py`):
   ```python
   SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
   ```
   - Needed to READ emails from inbox
   - Could not send emails

2. **MCP send_email** (`send_email.py`):
   ```python
   SCOPES = ['https://www.googleapis.com/auth/gmail.send']
   ```
   - Needed to SEND emails
   - Could not read emails

### What Happened

1. Gmail Watcher was working initially with `gmail.readonly` scope
2. When testing MCP email sending, we deleted `gmail_token.json`
3. Re-authenticated with only `gmail.send` scope
4. Gmail Watcher broke because the token no longer had `gmail.readonly` scope

### Why It Failed

When Gmail Watcher tried to authenticate:
- It loaded the existing token with `gmail.send` scope
- It requested `gmail.readonly` scope
- Google rejected the request because the scopes didn't match
- Result: `invalid_scope` error

---

## Solution

### Combined Scopes Approach

Updated both components to use the same combined scopes that support both reading and sending:

```python
# Combined scopes for both reading and sending emails
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]
```

### Files Modified

1. **`Bronze-tier/skills/watcher_skills/gmail_watcher_skill.py`** (line 32-36)
   - Changed from single `gmail.readonly` scope
   - To combined scopes array

2. **`Bronze-tier/mcp_server/actions/send_email.py`** (line 28-32)
   - Changed from single `gmail.send` scope
   - To combined scopes array

3. **Deleted and regenerated token**
   - Removed `credentials/gmail_token.json`
   - Re-authenticated with combined scopes
   - New token has both permissions

---

## Verification Results

### Test 1: Gmail Watcher ✅

```bash
python test_gmail_watcher.py
```

**Result:**
- Authentication successful with combined scopes
- Created 10 tasks from 10 unread emails
- All tasks saved to Vault/Inbox
- Gmail Watcher fully functional

**OAuth URL showed both scopes:**
```
scope=https://www.googleapis.com/auth/gmail.readonly+https://www.googleapis.com/auth/gmail.send
```

### Test 2: MCP Email Sending ✅

```bash
python test_send_email.py aaish28siddiqui@gmail.com
```

**Result:**
- Authentication successful (reused existing token)
- Email sent successfully (ID: 19c96dca168b5ff2)
- No re-authentication required
- MCP send_email fully functional

---

## Why This Solution Works

### Single Token, Multiple Permissions

- One OAuth token can have multiple scopes
- Both components now request the same scopes
- Token is valid for both reading and sending
- No conflicts when loading/refreshing token

### Scope Compatibility

- `gmail.readonly` - Read-only access to Gmail
- `gmail.send` - Send emails on behalf of user
- These scopes are compatible and can coexist
- Google allows requesting multiple scopes in one token

### Token Reuse

- First component to authenticate creates token with both scopes
- Second component loads existing token
- Both scopes are available to both components
- No re-authentication needed

---

## Google Cloud Console Configuration

### Required Scopes

Ensure your OAuth consent screen includes both scopes:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project: `digital-fte`
3. Navigate to **APIs & Services** > **OAuth consent screen**
4. Under **Scopes**, ensure both are added:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`

### Testing Mode

If app is in "Testing" mode:
- Add your Gmail address as a test user
- No verification required
- Scopes work immediately

---

## Alternative Solutions Considered

### Option 1: Separate Token Files ❌
**Approach:** Use different token files for each component
- `gmail_token_readonly.json` for watcher
- `gmail_token_send.json` for MCP

**Why Not Used:**
- More complex configuration
- Requires two separate OAuth flows
- User must authenticate twice
- More maintenance overhead

### Option 2: Use gmail.modify Scope ❌
**Approach:** Use broader `gmail.modify` scope for both

**Why Not Used:**
- Overly permissive (can modify/delete emails)
- Violates principle of least privilege
- Security risk if token is compromised
- Not necessary for our use case

### Option 3: Combined Scopes ✅ (Selected)
**Approach:** Both components use same combined scopes

**Why Selected:**
- Minimal permissions needed
- Single authentication flow
- Simple to maintain
- Follows security best practices
- Works for both use cases

---

## Best Practices

### 1. Consistent Scope Definitions

When multiple components share OAuth credentials:
- Define scopes in a central location
- Use the same scope list across all components
- Document why each scope is needed

### 2. Scope Documentation

```python
# Combined scopes for Gmail integration
# - gmail.readonly: Required for Gmail Watcher to read inbox
# - gmail.send: Required for MCP Server to send emails
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]
```

### 3. Token Management

- Store tokens in a consistent location
- Use descriptive filenames
- Document which components use which tokens
- Include token regeneration instructions

### 4. Testing After Scope Changes

When modifying OAuth scopes:
1. Delete existing token
2. Re-authenticate with new scopes
3. Test all components that use the token
4. Verify each component's functionality

---

## Troubleshooting

### Issue: "invalid_scope" Error

**Symptoms:**
```
('invalid_scope: Bad Request', {'error': 'invalid_scope'})
```

**Solution:**
1. Check that all components use the same scopes
2. Delete `credentials/gmail_token.json`
3. Re-authenticate
4. Verify scopes in OAuth URL

### Issue: Token Expired

**Symptoms:**
```
Token has been expired or revoked
```

**Solution:**
1. Token will auto-refresh if refresh_token exists
2. If refresh fails, delete token and re-authenticate
3. Check Google Cloud Console for app status

### Issue: Scope Not Authorized

**Symptoms:**
```
Access blocked: This app hasn't been verified by Google
```

**Solution:**
1. Add your email as test user in Google Cloud Console
2. Or complete Google's app verification process
3. Ensure scopes are added to OAuth consent screen

---

## Current Configuration

### Token Location
```
Bronze-tier/credentials/gmail_token.json
```

### Credentials Location
```
Bronze-tier/credentials/gmail_credentials.json
```

### Scopes in Token
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/gmail.send`

### Components Using Token
1. Gmail Watcher (`skills/watcher_skills/gmail_watcher_skill.py`)
2. MCP send_email (`mcp_server/actions/send_email.py`)

---

## Testing Checklist

After any OAuth scope changes:

- [ ] Delete existing token
- [ ] Test Gmail Watcher authentication
- [ ] Verify Gmail Watcher can read emails
- [ ] Test MCP send_email authentication
- [ ] Verify MCP can send emails
- [ ] Check both components work without re-authentication
- [ ] Verify token contains all required scopes
- [ ] Document any scope changes

---

## Summary

**Problem:** OAuth scope conflict between Gmail Watcher and MCP send_email

**Solution:** Use combined scopes in both components

**Result:** Both systems now work perfectly with a single shared token

**Status:** ✅ RESOLVED

Both Gmail Watcher and MCP email sending are fully functional and can coexist without conflicts.
