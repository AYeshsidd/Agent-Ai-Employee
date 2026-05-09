#!/usr/bin/env python3
"""Email MCP Module - Handles all email-related operations"""
from pathlib import Path
from typing import Dict, Any, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mcp_server.modules.base_module import MCPModule
from mcp_server.actions.send_email import SendEmailAction


class EmailModule(MCPModule):
    """
    Email communication module.
    
    Provides tools for:
    - Sending emails via Gmail
    - Email templates (future)
    - Email drafts (future)
    """

    def __init__(self):
        self.email_action = SendEmailAction()
        super().__init__("Email")

    def _register_tools(self):
        """Register email-related tools"""
        self._tools = {
            "send_email": {
                "handler": self._send_email,
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
                            },
                            "cc": {
                                "type": "string",
                                "description": "CC recipients (comma-separated)"
                            },
                            "bcc": {
                                "type": "string",
                                "description": "BCC recipients (comma-separated)"
                            }
                        },
                        "required": ["to", "subject", "body"]
                    }
                }
            },
            "send_bulk_email": {
                "handler": self._send_bulk_email,
                "schema": {
                    "name": "send_bulk_email",
                    "description": "Send email to multiple recipients (BCC)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipients": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of recipient email addresses"
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
                        "required": ["recipients", "subject", "body"]
                    }
                }
            }
        }

    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email tool"""
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(tool_name, parameters)
        if not is_valid:
            return {
                "status": "failed",
                "message": error_msg
            }

        if tool_name not in self._tools:
            return {
                "status": "failed",
                "message": f"Unknown tool: {tool_name}"
            }

        try:
            handler = self._tools[tool_name]["handler"]
            return handler(parameters)
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Email tool execution failed: {str(e)}"
            }

    def _send_email(self, params: Dict[str, str]) -> Dict[str, str]:
        """Send single email"""
        return self.email_action.execute(params)

    def _send_bulk_email(self, params: Dict[str, Any]) -> Dict[str, str]:
        """Send email to multiple recipients via BCC"""
        recipients = params.get("recipients", [])
        subject = params.get("subject", "")
        body = params.get("body", "")

        if not recipients:
            return {
                "status": "failed",
                "message": "No recipients provided"
            }

        results = []
        success_count = 0

        for recipient in recipients:
            result = self.email_action.execute({
                "to": recipient,
                "subject": subject,
                "body": body
            })
            results.append({"recipient": recipient, "result": result})
            if result.get("status") == "success":
                success_count += 1

        return {
            "status": "success" if success_count > 0 else "failed",
            "message": f"Sent {success_count}/{len(recipients)} emails",
            "details": results
        }

    def cleanup(self):
        """Cleanup email module resources"""
        super().cleanup()
