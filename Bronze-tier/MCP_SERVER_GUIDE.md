# MCP Server - Silver Tier Part 4

## Overview
The MCP (Model Context Protocol) Server provides a clean, modular interface for external actions. It exposes structured tools that can be called via JSON requests, enabling integration with AI agents and external systems.

## Architecture

```
mcp_server/
├── server.py              # Main MCP Server
├── actions/
│   ├── send_email.py      # Gmail email sending action
│   └── send_notification.py  # Console/log notification action
└── __init__.py
```

## Available Tools

### 1. send_email
Send emails via Gmail API using existing credentials.

**Parameters:**
```json
{
  "to": "recipient@example.com",
  "subject": "Email subject",
  "body": "Email body content"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Email sent successfully (ID: 18d4f...)"
}
```

**Requirements:**
- Gmail credentials in `credentials/gmail_credentials.json`
- Gmail API enabled with `gmail.send` scope
- OAuth token will be created/refreshed automatically

### 2. send_notification
Send notifications to console and log file.

**Parameters:**
```json
{
  "title": "Notification Title",
  "message": "Notification message content"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Notification sent: Notification Title"
}
```

**Output:**
- Formatted notification printed to console
- Logged to `logs/notifications.log`

## Usage

### Option 1: Direct Python API

```python
from mcp_server import get_server

# Get server instance
server = get_server()

# List available tools
tools = server.list_tools()
for tool in tools:
    print(f"Tool: {tool['name']}")
    print(f"Description: {tool['description']}")

# Call a tool
result = server.call_tool("send_notification", {
    "title": "Task Complete",
    "message": "Your task has been completed successfully"
})

print(result)
# Output: {"status": "success", "message": "Notification sent: Task Complete"}
```

### Option 2: JSON Request/Response

```python
from mcp_server import get_server
import json

server = get_server()

# Create JSON request
request = json.dumps({
    "tool": "send_email",
    "parameters": {
        "to": "user@example.com",
        "subject": "Hello from MCP Server",
        "body": "This is a test email"
    }
})

# Handle request
response = server.handle_json_request(request)
print(response)
```

### Option 3: Dictionary Request

```python
from mcp_server import get_server

server = get_server()

# Handle dictionary request
result = server.handle_request({
    "tool": "send_notification",
    "parameters": {
        "title": "Alert",
        "message": "System alert message"
    }
})

print(result)
```

## Testing

Run the comprehensive test suite:

```bash
cd Bronze-tier
python test_mcp_server.py
```

**Test Coverage:**
- Server initialization
- Tool registration and listing
- Send notification (valid and invalid inputs)
- Send email (validation logic)
- JSON request handling (valid and invalid JSON)
- Unknown tool handling
- Error handling and graceful failures

## Error Handling

The MCP Server handles errors gracefully:

**Missing Required Fields:**
```json
{
  "status": "failed",
  "message": "Missing 'to' field"
}
```

**Unknown Tool:**
```json
{
  "status": "failed",
  "message": "Unknown tool: invalid_tool"
}
```

**Invalid JSON:**
```json
{
  "status": "failed",
  "message": "Invalid JSON: Expecting property name..."
}
```

**Action Execution Error:**
```json
{
  "status": "failed",
  "message": "Gmail authentication failed"
}
```

## Integration with Existing System

The MCP Server integrates seamlessly with the existing Bronze/Silver Tier architecture:

1. **No modifications to existing code** - All MCP code is in separate `mcp_server/` directory
2. **Uses existing credentials** - Reuses Gmail credentials from watchers
3. **Uses existing logging** - Integrates with BronzeLogger
4. **Uses existing config** - Leverages Config class for paths

## Gmail Setup for send_email

To use the `send_email` action:

1. **Use existing Gmail credentials** from watchers (already set up)
2. **Update OAuth scopes** in Google Cloud Console:
   - Add `https://www.googleapis.com/auth/gmail.send` scope
   - Or use `https://www.googleapis.com/auth/gmail.modify` (broader scope)
3. **Delete old token** if needed:
   ```bash
   rm credentials/gmail_token.json
   ```
4. **Re-authenticate** - The action will prompt for OAuth consent

## Logging

All MCP Server operations are logged to `logs/bronze_tier.log`:

```
2026-02-25 03:50:15 - MCPServer - INFO - [SKILL] MCPServer | Operation: __init__ | Status: SUCCESS | Details: MCP Server initialized
2026-02-25 03:50:15 - MCPServer - INFO - [SKILL] MCPServer | Operation: call_tool | Status: IN_PROGRESS | Details: Calling tool: send_notification
2026-02-25 03:50:15 - MCPServer - INFO - [SKILL] MCPServer | Operation: call_tool | Status: SUCCESS | Details: send_notification: Notification sent: Test Notification
```

Notifications are also logged to `logs/notifications.log`:

```
[2026-02-25 03:50:15] Test Notification: This is a test notification from MCP Server test suite
[2026-02-25 03:50:23] JSON Test: Testing JSON request handling
```

## Tool Schema Format

Each tool exposes a JSON schema describing its interface:

```json
{
  "name": "send_email",
  "description": "Send an email via Gmail",
  "parameters": {
    "type": "object",
    "properties": {
      "to": {
        "type": "string",
        "description": "Recipient email address"
      },
      "subject": {
        "type": "string",
        "description": "Email subject"
      },
      "body": {
        "type": "string",
        "description": "Email body content"
      }
    },
    "required": ["to", "subject", "body"]
  }
}
```

## Adding New Actions

To add a new action:

1. **Create action file** in `mcp_server/actions/`:
   ```python
   class MyNewAction:
       def execute(self, params: Dict[str, str]) -> Dict[str, str]:
           # Validate params
           # Execute action
           # Return result
           return {"status": "success", "message": "Action completed"}
   ```

2. **Register in server.py**:
   ```python
   self.actions["my_new_action"] = {
       "handler": MyNewAction(),
       "schema": {
           "name": "my_new_action",
           "description": "Description of action",
           "parameters": { ... }
       }
   }
   ```

3. **Test the action** - Add tests to `test_mcp_server.py`

## Security Considerations

- **Input validation** - All parameters are validated before execution
- **Error isolation** - Exceptions are caught and returned as error responses
- **Credential security** - Uses existing OAuth flow, no hardcoded credentials
- **Graceful failures** - Server never crashes, always returns structured response

## Performance

- **Singleton pattern** - Server instance is reused across calls
- **Lazy authentication** - Gmail auth only happens when needed
- **Minimal overhead** - Direct function calls, no network overhead

## Future Enhancements

Potential additions for Gold Tier:
- WebSocket support for real-time communication
- Async action execution for long-running tasks
- Action queuing and scheduling
- More actions (SMS, Slack, Discord, etc.)
- Authentication and authorization layer
- Rate limiting and throttling

## Troubleshooting

**Issue: Gmail authentication fails**
- Solution: Update OAuth scopes in Google Cloud Console
- Delete `credentials/gmail_token.json` and re-authenticate

**Issue: Notification not appearing**
- Solution: Check `logs/notifications.log` for logged notifications
- Verify console output is not being suppressed

**Issue: Unknown tool error**
- Solution: Check tool name spelling (case-sensitive)
- Use `server.list_tools()` to see available tools

## Summary

The MCP Server provides:
✅ Clean, modular architecture
✅ Two working actions (email, notification)
✅ Robust error handling
✅ JSON request/response interface
✅ Comprehensive test coverage (6/6 tests passing)
✅ Full integration with existing system
✅ No modifications to Bronze/Silver Tier code
✅ Production-ready implementation
