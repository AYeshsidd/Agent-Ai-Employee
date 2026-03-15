#!/usr/bin/env python3
"""MCP Server - Silver Tier Part 4"""
from pathlib import Path
from typing import Dict, Any, Optional
import json
import sys

# Add Bronze-tier to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config
from bronze_logger import BronzeLogger

# Import actions
from mcp_server.actions.send_email import SendEmailAction
from mcp_server.actions.send_notification import SendNotificationAction


class MCPServer:
    """MCP Server for external actions"""

    def __init__(self):
        self.logger = BronzeLogger.get_logger("MCPServer")
        self.actions = {}
        self._register_actions()

        BronzeLogger.log_skill_execution(
            self.logger, "MCPServer", "__init__",
            "SUCCESS", "MCP Server initialized"
        )

    def _register_actions(self):
        """Register all available actions"""
        self.actions = {
            "send_email": {
                "handler": SendEmailAction(),
                "schema": {
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
            },
            "send_notification": {
                "handler": SendNotificationAction(),
                "schema": {
                    "name": "send_notification",
                    "description": "Send a notification (console + log)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Notification title"
                            },
                            "message": {
                                "type": "string",
                                "description": "Notification message"
                            }
                        },
                        "required": ["title", "message"]
                    }
                }
            }
        }

    def list_tools(self) -> list:
        """
        List all available tools with their schemas

        Returns:
            List of tool schemas
        """
        return [action["schema"] for action in self.actions.values()]

    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool with given parameters

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
            # Validate tool exists
            if tool_name not in self.actions:
                result = {
                    "status": "failed",
                    "message": f"Unknown tool: {tool_name}"
                }
                BronzeLogger.log_skill_execution(
                    self.logger, "MCPServer", "call_tool",
                    "FAILED", f"Unknown tool: {tool_name}"
                )
                return result

            # Get action handler
            handler = self.actions[tool_name]["handler"]

            # Execute action
            result = handler.execute(parameters)

            # Log result
            status = "SUCCESS" if result.get("status") == "success" else "FAILED"
            BronzeLogger.log_skill_execution(
                self.logger, "MCPServer", "call_tool",
                status, f"{tool_name}: {result.get('message', 'No message')}"
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
        Handle JSON-RPC style request

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
        Handle JSON string request and return JSON string response

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


# Singleton instance
_server_instance = None


def get_server() -> MCPServer:
    """Get or create MCP Server singleton instance"""
    global _server_instance
    if _server_instance is None:
        _server_instance = MCPServer()
    return _server_instance


if __name__ == "__main__":
    # Quick test
    server = get_server()

    print("\n" + "=" * 70)
    print("  MCP SERVER - AVAILABLE TOOLS")
    print("=" * 70)

    tools = server.list_tools()
    for tool in tools:
        print(f"\nTool: {tool['name']}")
        print(f"Description: {tool['description']}")
        print(f"Parameters: {json.dumps(tool['parameters'], indent=2)}")

    print("\n" + "=" * 70)
