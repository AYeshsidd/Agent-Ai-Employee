"""MCP Server Package - Silver Tier Part 4 (Modular Architecture)

This package provides a modular MCP (Model Context Protocol) Server architecture
that supports multiple domain-specific modules while maintaining backward
compatibility with existing Silver Tier code.

Architecture Overview:
=====================

MCPServer (server.py)
├── Legacy Actions (backward compatible)
│   ├── send_email
│   └── send_notification
├── Module Registry
│   ├── Email Module (email_module.py)
│   ├── Social Module (social_module.py)
│   └── Accounting Module (accounting_module.py)
└── Base Module (base_module.py) - Abstract base class

Usage Examples:
==============

# Backward Compatible (existing code continues to work)
from mcp_server import get_server
server = get_server()
server.call_tool("send_email", {"to": "...", "subject": "...", "body": "..."})

# New Modular API
from mcp_server import get_server
server = get_server()

# Access specific modules
email_module = server.get_module("email")
email_module.execute("send_email", {...})

# Load additional modules
server.load_module("accounting")

# List all available tools
tools = server.list_tools()

# Get module information
module_info = server.get_module_info()
"""

from mcp_server.server import MCPServer, get_server
from mcp_server.modules import (
    MCPModule,
    MCPModuleRegistry,
    get_registry,
    initialize_default_modules
)

# Module classes for direct import
from mcp_server.modules.email_module import EmailModule
from mcp_server.modules.social_module import SocialModule
from mcp_server.modules.accounting_module import AccountingModule

__all__ = [
    # Server
    'MCPServer',
    'get_server',
    
    # Registry
    'MCPModuleRegistry',
    'get_registry',
    'initialize_default_modules',
    
    # Base class
    'MCPModule',
    
    # Module classes
    'EmailModule',
    'SocialModule',
    'AccountingModule'
]
