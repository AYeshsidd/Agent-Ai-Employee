#!/usr/bin/env python3
"""Base MCP Module - Abstract base class for all MCP modules"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import Config
from bronze_logger import BronzeLogger


class MCPModule(ABC):
    """
    Abstract base class for all MCP modules.
    
    Each module represents a domain-specific capability (Email, Social, Accounting, etc.)
    and follows the single responsibility principle.
    """

    def __init__(self, module_name: str):
        """
        Initialize MCP module.
        
        Args:
            module_name: Human-readable name for the module
        """
        self.module_name = module_name
        self.module_id = self._generate_module_id(module_name)
        self.logger = BronzeLogger.get_logger(f"MCP.{module_name}")
        self._initialized = False
        self._tools: Dict[str, Dict[str, Any]] = {}
        
        BronzeLogger.log_skill_execution(
            self.logger, module_name, "__init__",
            "IN_PROGRESS", f"Initializing {module_name} module"
        )
        
        # Register tools defined by this module
        self._register_tools()
        
        self._initialized = True
        BronzeLogger.log_skill_execution(
            self.logger, module_name, "__init__",
            "SUCCESS", f"{module_name} module initialized with {len(self._tools)} tools"
        )

    def _generate_module_id(self, name: str) -> str:
        """Generate a consistent module ID from name"""
        return name.lower().replace(" ", "_").replace("-", "_")

    @abstractmethod
    def _register_tools(self):
        """
        Register all tools provided by this module.
        
        Subclasses must implement this to define their tools.
        Each tool should be added to self._tools with:
        {
            "tool_name": {
                "handler": <callable>,
                "schema": {
                    "name": "tool_name",
                    "description": "...",
                    "parameters": {...}
                }
            }
        }
        """
        pass

    @abstractmethod
    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool from this module.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            
        Returns:
            Dictionary with 'status' and 'message' keys
        """
        pass

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get all tool schemas provided by this module.
        
        Returns:
            List of tool schemas
        """
        return [tool["schema"] for tool in self._tools.values()]

    def get_tool_names(self) -> List[str]:
        """
        Get list of tool names provided by this module.
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def has_tool(self, tool_name: str) -> bool:
        """
        Check if module provides a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            True if tool exists, False otherwise
        """
        return tool_name in self._tools

    def get_module_info(self) -> Dict[str, Any]:
        """
        Get module metadata.
        
        Returns:
            Dictionary with module information
        """
        return {
            "module_id": self.module_id,
            "module_name": self.module_name,
            "tools": self.get_tool_names(),
            "tool_count": len(self._tools),
            "initialized": self._initialized
        }

    def validate_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate parameters against tool schema.
        
        Args:
            tool_name: Name of the tool
            parameters: Parameters to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if tool_name not in self._tools:
            return False, f"Unknown tool: {tool_name}"

        schema = self._tools[tool_name]["schema"]["parameters"]
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        # Check required parameters
        missing = [param for param in required if param not in parameters]
        if missing:
            return False, f"Missing required parameters: {', '.join(missing)}"

        # Check parameter types (basic validation)
        for param, value in parameters.items():
            if param in properties:
                expected_type = properties[param].get("type")
                if expected_type == "string" and not isinstance(value, str):
                    return False, f"Parameter '{param}' must be a string"
                elif expected_type == "object" and not isinstance(value, dict):
                    return False, f"Parameter '{param}' must be an object"
                elif expected_type == "array" and not isinstance(value, list):
                    return False, f"Parameter '{param}' must be an array"

        return True, ""

    def cleanup(self):
        """
        Cleanup resources when module is being unloaded.
        
        Override in subclasses if cleanup is needed.
        """
        BronzeLogger.log_skill_execution(
            self.logger, self.module_name, "cleanup",
            "SUCCESS", f"{self.module_name} module cleaned up"
        )
        self._initialized = False
