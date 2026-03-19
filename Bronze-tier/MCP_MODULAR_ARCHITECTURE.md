# MCP Modular Architecture Guide

## Overview

The MCP (Model Context Protocol) Server has been refactored with a **modular architecture** that:
- Maintains 100% backward compatibility with existing Silver Tier code
- Enables easy addition of new MCP servers/domains
- Follows single responsibility principle
- Provides clear interfaces between components

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         MCPServer                                │
│                    (server.py - Main Entry)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐    ┌──────────────────────────────┐   │
│  │  Legacy Actions     │    │   Module Registry            │   │
│  │  (Backward Compat)  │    │   (Dynamic Module Loading)   │   │
│  │                     │    │                              │   │
│  │  • send_email       │    │  ┌────────────────────────┐  │   │
│  │  • send_notification│    │  │ EmailModule            │  │   │
│  │                     │    │  │ - send_email           │  │   │
│  └─────────────────────┘    │  │ - send_bulk_email      │  │   │
│                              │  └────────────────────────┘  │   │
│                              │                              │   │
│                              │  ┌────────────────────────┐  │   │
│                              │  │ SocialModule           │  │   │
│                              │  │ - send_notification    │  │   │
│                              │  │ - post_to_linkedin     │  │   │
│                              │  │ - schedule_linkedin_post│ │   │
│                              │  └────────────────────────┘  │   │
│                              │                              │   │
│                              │  ┌────────────────────────┐  │   │
│                              │  │ AccountingModule       │  │   │
│                              │  │ - create_invoice       │  │   │
│                              │  │ - track_expense        │  │   │
│                              │  │ - generate_financial_report││   │
│                              │  │ - send_payment_reminder │  │   │
│                              │  └────────────────────────┘  │   │
│                              └──────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
Bronze-tier/mcp_server/
├── __init__.py                 # Package exports (updated for modular)
├── server.py                   # Main MCPServer class (refactored)
│
├── actions/                    # Legacy actions (unchanged)
│   ├── __init__.py
│   ├── send_email.py           # Original implementation
│   └── send_notification.py    # Original implementation
│
└── modules/                    # NEW: Modular architecture
    ├── __init__.py
    ├── base_module.py          # Abstract base class for all modules
    ├── registry.py             # Module registry and loader
    ├── email_module.py         # Email domain module
    ├── social_module.py        # Social media domain module
    └── accounting_module.py    # Accounting domain module (stub)
```

## Key Components

### 1. MCPModule (Base Class)

**File:** `modules/base_module.py`

Abstract base class that all MCP modules must inherit from.

```python
from mcp_server.modules.base_module import MCPModule

class MyCustomModule(MCPModule):
    def __init__(self):
        super().__init__("MyCustom")
    
    def _register_tools(self):
        self._tools = {
            "my_tool": {
                "handler": self._my_tool,
                "schema": {...}
            }
        }
    
    def execute(self, tool_name, parameters):
        # Tool execution logic
        pass
```

**Key Methods:**
- `_register_tools()` - Define tools provided by module
- `execute(tool_name, parameters)` - Execute a tool
- `get_tools()` - Get tool schemas
- `validate_parameters()` - Validate input parameters
- `cleanup()` - Resource cleanup

### 2. MCPModuleRegistry

**File:** `modules/registry.py`

Central registry for loading, managing, and routing to modules.

```python
from mcp_server.modules import get_registry

registry = get_registry()

# Register module class
registry.register_module_class("custom", MyCustomModule)

# Load module
registry.load_module("custom")

# Execute tool (auto-routes to correct module)
registry.execute_tool("my_tool", {...})

# List all tools
registry.list_tools()
```

### 3. Domain Modules

#### Email Module (`modules/email_module.py`)
- **Purpose:** All email-related operations
- **Tools:**
  - `send_email` - Send single email
  - `send_bulk_email` - Send to multiple recipients

#### Social Module (`modules/social_module.py`)
- **Purpose:** Social media operations
- **Tools:**
  - `send_notification` - Console/log notifications
  - `post_to_linkedin` - Post to LinkedIn
  - `schedule_linkedin_post` - Schedule future posts (stub)

#### Accounting Module (`modules/accounting_module.py`)
- **Purpose:** Financial operations (stub for future)
- **Tools:**
  - `create_invoice` - Generate invoices
  - `track_expense` - Record expenses
  - `generate_financial_report` - Financial summaries
  - `send_payment_reminder` - Payment reminders

## Usage

### Backward Compatible (Existing Code)

All existing Silver Tier code continues to work without modification:

```python
from mcp_server import get_server

server = get_server()

# Send notification
server.call_tool("send_notification", {
    "title": "Task Complete",
    "message": "Your task has been completed"
})

# Send email
server.call_tool("send_email", {
    "to": "user@example.com",
    "subject": "Update",
    "body": "Task completed successfully"
})

# List tools
tools = server.list_tools()
```

### New Modular API

Access modules directly for advanced usage:

```python
from mcp_server import get_server

server = get_server()

# Get specific module
email_module = server.get_module("email")
result = email_module.execute("send_email", {
    "to": "user@example.com",
    "subject": "Hello",
    "body": "Test"
})

# Get module information
module_info = server.get_module_info()
for info in module_info:
    print(f"Module: {info['module_name']}")
    print(f"  Tools: {info['tools']}")

# Load additional module
server.load_module("accounting")

# Unload module
server.unload_module("social")
```

### Creating Custom Modules

1. **Create module class:**

```python
# modules/my_module.py
from mcp_server.modules.base_module import MCPModule

class MyModule(MCPModule):
    def __init__(self):
        super().__init__("My")
    
    def _register_tools(self):
        self._tools = {
            "my_tool": {
                "handler": self._execute_my_tool,
                "schema": {
                    "name": "my_tool",
                    "description": "Does something useful",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "param1": {"type": "string"}
                        },
                        "required": ["param1"]
                    }
                }
            }
        }
    
    def execute(self, tool_name, parameters):
        is_valid, error = self.validate_parameters(tool_name, parameters)
        if not is_valid:
            return {"status": "failed", "message": error}
        
        return self._tools[tool_name]["handler"](parameters)
    
    def _execute_my_tool(self, params):
        # Implementation
        return {"status": "success", "message": "Done"}
```

2. **Register and load:**

```python
from mcp_server import get_server, MCPModuleRegistry

server = get_server()
registry = server.get_registry()

# Register module class
registry.register_module_class("my", MyModule)

# Load module
registry.load_module("my")

# Use tool
result = server.call_tool("my_tool", {"param1": "value"})
```

## Module Interface Specification

### Input/Output Contract

All modules follow this interface:

**Input:**
```python
{
    "tool_name": str,       # Tool to execute
    "parameters": dict      # Tool-specific parameters
}
```

**Output:**
```python
{
    "status": str,          # "success" or "failed"
    "message": str,         # Human-readable result
    "details": dict,        # Optional: Additional data
    "error": str            # Optional: Error details
}
```

### Tool Schema Format

```python
{
    "name": str,            # Tool name
    "description": str,     # What the tool does
    "parameters": {
        "type": "object",
        "properties": {
            "param_name": {
                "type": str,        # "string", "number", "object", "array"
                "description": str,
                "enum": list        # Optional: Allowed values
            }
        },
        "required": list    # Required parameters
    }
}
```

## Migration Guide

### For Existing Code

**No changes required!** All existing code continues to work:

```python
# This still works exactly as before
from mcp_server import get_server
server = get_server()
server.call_tool("send_email", {...})
```

### For New Features

Use the modular API for better organization:

```python
# Instead of adding to monolithic server.py
# Create a new module:

# modules/calendar_module.py
class CalendarModule(MCPModule):
    def _register_tools(self):
        self._tools = {
            "create_event": {...},
            "list_events": {...}
        }
```

## Testing

### Test Modular Architecture

```bash
cd Bronze-tier
python -m mcp_server.server
```

### Test Backward Compatibility

```bash
cd Bronze-tier
python test_mcp_server.py
```

### Test Individual Modules

```python
from mcp_server.modules.email_module import EmailModule

module = EmailModule()
print(module.get_tools())
print(module.execute("send_email", {...}))
```

## Benefits

### 1. Single Responsibility
Each module handles one domain (Email, Social, Accounting)

### 2. Easy Extension
Add new capabilities without modifying existing code

### 3. Clear Interfaces
Well-defined input/output contracts

### 4. Backward Compatible
Zero breaking changes to existing code

### 5. Testable
Modules can be tested in isolation

### 6. Maintainable
Changes to one module don't affect others

## Future Enhancements

### Planned Modules
- **Calendar Module** - Google Calendar integration
- **Storage Module** - Cloud storage operations
- **Analytics Module** - Metrics and reporting
- **Communication Module** - Slack, Discord, SMS

### Planned Features
- Module hot-reloading
- Module configuration files
- Module dependency management
- Module versioning

## Troubleshooting

### Module Not Loading

```python
# Check if module class is registered
registry = get_registry()
print(registry._module_classes)

# Check load result
success = registry.load_module("email")
print(f"Load success: {success}")
```

### Tool Not Found

```python
# Check if tool exists
registry = get_registry()
print(f"Has tool: {registry.has_tool('send_email')}")

# List all available tools
tools = registry.list_tools()
for tool in tools:
    print(tool['name'])
```

### Module Execution Error

```python
# Get detailed error
result = server.call_tool("my_tool", {...})
if result['status'] == 'failed':
    print(f"Error: {result['message']}")
    print(f"Details: {result.get('error')}")
```

## Summary

The modular MCP architecture provides:
- ✅ 100% backward compatibility
- ✅ Clean separation of concerns
- ✅ Easy extension mechanism
- ✅ Clear interfaces
- ✅ Production-ready implementation

All existing Silver Tier functionality is preserved while enabling future growth through modular design.
