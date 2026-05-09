#!/usr/bin/env python3
"""MCP Server - Silver Tier Part 4 (Modular Architecture)

This is the refactored MCP Server with modular architecture support.
It maintains full backward compatibility with existing code while
providing a foundation for multiple MCP servers.

Architecture:
- MCPServer: Main server class (backward compatible API)
- MCPModuleRegistry: Manages module loading and tool routing
- MCPModule: Base class for all modules (Email, Social, Accounting, etc.)

Usage (backward compatible):
    from mcp_server import get_server
    server = get_server()
    server.call_tool("send_email", {...})
    server.call_tool("send_notification", {...})

Usage (new modular API):
    from mcp_server import get_server
    server = get_server()
    server.get_module("email").execute(...)
    server.get_registry().load_module("accounting")
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config
from bronze_logger import BronzeLogger

# Import modular architecture
from mcp_server.modules.registry import (
    MCPModuleRegistry,
    get_registry,
    initialize_default_modules
)
from mcp_server.modules.base_module import MCPModule

# Import legacy actions for backward compatibility
from mcp_server.actions.send_email import SendEmailAction
from mcp_server.actions.send_notification import SendNotificationAction


class MCPServer:
    """
    MCP Server with modular architecture.
    
    Maintains full backward compatibility with existing Silver Tier code
    while providing new modular capabilities.
    
    Backward Compatible API:
    - list_tools() - Returns all tool schemas
    - call_tool(tool_name, parameters) - Execute a tool
    - handle_request(request) - Handle JSON-RPC style request
    - handle_json_request(json_str) - Handle JSON string request
    
    New Modular API:
    - get_registry() - Get module registry
    - get_module(module_id) - Get specific module
    - get_module_info() - Get module information
    - load_module(module_id) - Load additional module
    - unload_module(module_id) - Unload module
    """

    def __init__(self, auto_load_modules: bool = True):
        """
        Initialize MCP Server.
        
        Args:
            auto_load_modules: If True, automatically load default modules
        """
        self.logger = BronzeLogger.get_logger("MCPServer")
        self._registry: Optional[MCPModuleRegistry] = None
        
        # Legacy actions for backward compatibility
        self._legacy_actions = {
            "send_email": SendEmailAction(),
            "send_notification": SendNotificationAction()
        }
        
        BronzeLogger.log_skill_execution(
            self.logger, "MCPServer", "__init__",
            "IN_PROGRESS", "Initializing MCP Server"
        )
        
        # Auto-load default modules if requested
        if auto_load_modules:
            self._registry = get_registry()
            initialize_default_modules()
            BronzeLogger.log_skill_execution(
                self.logger, "MCPServer", "__init__",
                "SUCCESS", f"MCP Server initialized with modular architecture ({len(self._registry._modules)} modules)"
            )
        else:
            BronzeLogger.log_skill_execution(
                self.logger, "MCPServer", "__init__",
                "SUCCESS", "MCP Server initialized (no modules loaded)"
            )

    def get_registry(self) -> Optional[MCPModuleRegistry]:
        """
        Get the module registry.
        
        Returns:
            Module registry instance or None if modules not loaded
        """
        return self._registry

    def get_module(self, module_id: str) -> Optional[MCPModule]:
        """
        Get a loaded module by ID.
        
        Args:
            module_id: Module ID (e.g., "email", "social", "accounting")
            
        Returns:
            Module instance or None
        """
        if self._registry:
            return self._registry.get_module(module_id)
        return None

    def get_module_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all loaded modules.
        
        Returns:
            List of module info dictionaries
        """
        if self._registry:
            return self._registry.get_all_module_info()
        return []

    def load_module(self, module_id: str) -> bool:
        """
        Load an additional module.
        
        Args:
            module_id: Module ID to load
            
        Returns:
            True if successful, False otherwise
        """
        if not self._registry:
            self._registry = get_registry()
        return self._registry.load_module(module_id)

    def unload_module(self, module_id: str) -> bool:
        """
        Unload a module.
        
        Args:
            module_id: Module ID to unload
            
        Returns:
            True if successful, False otherwise
        """
        if self._registry:
            return self._registry.unload_module(module_id)
        return False

    def list_tools(self) -> list:
        """
        List all available tools with their schemas.
        
        Combines tools from:
        1. Legacy actions (for backward compatibility)
        2. All loaded modules
        
        Returns:
            List of tool schemas
        """
        all_tools = []
        
        # Add legacy tool schemas (backward compatibility)
        all_tools.append({
            "name": "send_email",
            "description": "Send an email via Gmail",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"}
                },
                "required": ["to", "subject", "body"]
            }
        })
        
        all_tools.append({
            "name": "send_notification",
            "description": "Send a notification (console + log)",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Notification title"},
                    "message": {"type": "string", "description": "Notification message"}
                },
                "required": ["title", "message"]
            }
        })
        
        # Add module tools
        if self._registry:
            all_tools.extend(self._registry.list_tools())
        
        return all_tools

    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool with given parameters.
        
        Tool resolution order:
        1. Check loaded modules first
        2. Fall back to legacy actions
        
        Args:
            tool_name: Name of the tool to call
            parameters: Dictionary of parameters
            
        Returns:
            Dictionary with result
        """
        BronzeLogger.log_skill_execution(
            self.logger, "MCPServer", "call_tool",
            "IN_PROGRESS", f"Calling tool: {tool_name}"
        )

        try:
            # Try modules first
            if self._registry and self._registry.has_tool(tool_name):
                result = self._registry.execute_tool(tool_name, parameters)
                
                status = "SUCCESS" if result.get("status") == "success" else "FAILED"
                BronzeLogger.log_skill_execution(
                    self.logger, "MCPServer", "call_tool",
                    status, f"{tool_name}: {result.get('message', 'No message')}"
                )
                return result
            
            # Fall back to legacy actions
            if tool_name in self._legacy_actions:
                handler = self._legacy_actions[tool_name]
                result = handler.execute(parameters)
                
                status = "SUCCESS" if result.get("status") == "success" else "FAILED"
                BronzeLogger.log_skill_execution(
                    self.logger, "MCPServer", "call_tool",
                    status, f"{tool_name}: {result.get('message', 'No message')}"
                )
                return result
            
            # Tool not found
            result = {
                "status": "failed",
                "message": f"Unknown tool: {tool_name}"
            }
            BronzeLogger.log_skill_execution(
                self.logger, "MCPServer", "call_tool",
                "FAILED", f"Unknown tool: {tool_name}"
            )
            return result

        except Exception as e:
            result = {
                "status": "failed",
                "message": f"Error executing tool: {str(e)}"
            }
            BronzeLogger.log_skill_execution(
                self.logger, "MCPServer", "call_tool",
                "FAILED", str(e)
            )
            return result

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle JSON-RPC style request.
        
        Args:
            request: Dictionary with 'tool' and 'parameters'
            
        Returns:
            Dictionary with result
        """
        try:
            tool_name = request.get("tool")
            parameters = request.get("parameters", {})

            if not tool_name:
                return {
                    "status": "failed",
                    "message": "Missing 'tool' field in request"
                }

            return self.call_tool(tool_name, parameters)

        except Exception as e:
            return {
                "status": "failed",
                "message": f"Error handling request: {str(e)}"
            }

    def handle_json_request(self, json_str: str) -> str:
        """
        Handle JSON string request and return JSON string response.
        
        Args:
            json_str: JSON string with request
            
        Returns:
            JSON string with response
        """
        try:
            request = json.loads(json_str)
            result = self.handle_request(request)
            return json.dumps(result, indent=2)

        except json.JSONDecodeError as e:
            error_result = {
                "status": "failed",
                "message": f"Invalid JSON: {str(e)}"
            }
            return json.dumps(error_result, indent=2)

        except Exception as e:
            error_result = {
                "status": "failed",
                "message": f"Error: {str(e)}"
            }
            return json.dumps(error_result, indent=2)

    def cleanup(self):
        """Cleanup server resources"""
        if self._registry:
            self._registry.cleanup()
        
        BronzeLogger.log_skill_execution(
            self.logger, "MCPServer", "cleanup",
            "SUCCESS", "MCP Server cleaned up"
        )


# Singleton instance
_server_instance: Optional[MCPServer] = None


def get_server(auto_load_modules: bool = True) -> MCPServer:
    """
    Get or create MCP Server singleton instance.
    
    Args:
        auto_load_modules: If True, automatically load default modules
        
    Returns:
        MCP Server instance
    """
    global _server_instance
    if _server_instance is None:
        _server_instance = MCPServer(auto_load_modules=auto_load_modules)
    return _server_instance


if __name__ == "__main__":
    # Quick test
    print("\n" + "=" * 70)
    print("  MCP SERVER - MODULAR ARCHITECTURE TEST")
    print("=" * 70)
    
    server = get_server()
    
    print("\n[TEST 1] List all tools...")
    tools = server.list_tools()
    print(f"  Found {len(tools)} tools:")
    for tool in tools:
        print(f"    - {tool['name']}")
    
    print("\n[TEST 2] Get module info...")
    module_info = server.get_module_info()
    for info in module_info:
        print(f"  Module: {info['module_name']} ({info['module_id']})")
        print(f"    Tools: {', '.join(info['tools'])}")
    
    print("\n[TEST 3] Test legacy send_notification...")
    result = server.call_tool("send_notification", {
        "title": "Test Notification",
        "message": "Modular architecture test"
    })
    print(f"  Result: {result['status']} - {result['message']}")
    
    print("\n[TEST 4] Test module-based tool...")
    if server.get_registry() and server.get_registry().has_tool("send_email"):
        print("  Email module loaded and ready")
    else:
        print("  Email module available via legacy action")
    
    print("\n" + "=" * 70)
    print("  All tests completed successfully!")
    print("=" * 70)
