#!/usr/bin/env python3
"""MCP Module Registry - Manages loading and registration of MCP modules"""
from pathlib import Path
from typing import Dict, Any, Optional, List, Type
import sys
import importlib

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mcp_server.modules.base_module import MCPModule
from bronze_logger import BronzeLogger
from config import Config


class MCPModuleRegistry:
    """
    Registry for MCP modules.
    
    Handles:
    - Module discovery and loading
    - Module lifecycle management
    - Tool routing to appropriate modules
    """

    def __init__(self):
        self.logger = BronzeLogger.get_logger("MCP.Registry")
        self._modules: Dict[str, MCPModule] = {}
        self._module_classes: Dict[str, Type[MCPModule]] = {}
        self._tool_index: Dict[str, str] = {}  # tool_name -> module_id
        
        BronzeLogger.log_skill_execution(
            self.logger, "MCPModuleRegistry", "__init__",
            "IN_PROGRESS", "Initializing module registry"
        )

    def register_module_class(self, module_id: str, module_class: Type[MCPModule]):
        """
        Register a module class for later instantiation.
        
        Args:
            module_id: Unique identifier for the module
            module_class: Module class (not instance)
        """
        self._module_classes[module_id] = module_class
        BronzeLogger.log_skill_execution(
            self.logger, "MCPModuleRegistry", "register_module_class",
            "SUCCESS", f"Registered module class: {module_id}"
        )

    def load_module(self, module_id: str, **kwargs) -> bool:
        """
        Load and instantiate a module.
        
        Args:
            module_id: ID of module to load
            **kwargs: Arguments to pass to module constructor
            
        Returns:
            True if successful, False otherwise
        """
        if module_id in self._modules:
            BronzeLogger.log_skill_execution(
                self.logger, "MCPModuleRegistry", "load_module",
                "FAILED", f"Module already loaded: {module_id}"
            )
            return False

        module_class = self._module_classes.get(module_id)
        if not module_class:
            BronzeLogger.log_skill_execution(
                self.logger, "MCPModuleRegistry", "load_module",
                "FAILED", f"Unknown module class: {module_id}"
            )
            return False

        try:
            # Instantiate module
            module = module_class(**kwargs)
            
            # Store module
            self._modules[module_id] = module
            
            # Index tools
            for tool_name in module.get_tool_names():
                self._tool_index[tool_name] = module_id
            
            BronzeLogger.log_skill_execution(
                self.logger, "MCPModuleRegistry", "load_module",
                "SUCCESS", f"Loaded module: {module_id} with {len(module.get_tool_names())} tools"
            )
            return True
            
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "MCPModuleRegistry", "load_module",
                "FAILED", f"Failed to load {module_id}: {str(e)}"
            )
            return False

    def unload_module(self, module_id: str) -> bool:
        """
        Unload a module.
        
        Args:
            module_id: ID of module to unload
            
        Returns:
            True if successful, False otherwise
        """
        if module_id not in self._modules:
            return False

        try:
            module = self._modules[module_id]
            module.cleanup()
            
            # Remove from registry
            del self._modules[module_id]
            
            # Remove from tool index
            tools_to_remove = [tool for tool, mid in self._tool_index.items() if mid == module_id]
            for tool in tools_to_remove:
                del self._tool_index[tool]
            
            BronzeLogger.log_skill_execution(
                self.logger, "MCPModuleRegistry", "unload_module",
                "SUCCESS", f"Unloaded module: {module_id}"
            )
            return True
            
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "MCPModuleRegistry", "unload_module",
                "FAILED", f"Failed to unload {module_id}: {str(e)}"
            )
            return False

    def get_module(self, module_id: str) -> Optional[MCPModule]:
        """
        Get a loaded module by ID.
        
        Args:
            module_id: Module ID
            
        Returns:
            Module instance or None
        """
        return self._modules.get(module_id)

    def get_all_modules(self) -> Dict[str, MCPModule]:
        """
        Get all loaded modules.
        
        Returns:
            Dictionary of module instances
        """
        return self._modules.copy()

    def get_module_info(self, module_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a module.
        
        Args:
            module_id: Module ID
            
        Returns:
            Module info dictionary or None
        """
        module = self._modules.get(module_id)
        if module:
            return module.get_module_info()
        return None

    def get_all_module_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all loaded modules.
        
        Returns:
            List of module info dictionaries
        """
        return [module.get_module_info() for module in self._modules.values()]

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by routing to the appropriate module.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        module_id = self._tool_index.get(tool_name)
        
        if not module_id:
            return {
                "status": "failed",
                "message": f"Unknown tool: {tool_name}"
            }

        module = self._modules.get(module_id)
        if not module:
            return {
                "status": "failed",
                "message": f"Module not loaded: {module_id}"
            }

        return module.execute(tool_name, parameters)

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools from all modules.
        
        Returns:
            List of tool schemas
        """
        all_tools = []
        for module in self._modules.values():
            all_tools.extend(module.get_tools())
        return all_tools

    def has_tool(self, tool_name: str) -> bool:
        """
        Check if a tool is available.
        
        Args:
            tool_name: Tool name
            
        Returns:
            True if tool exists, False otherwise
        """
        return tool_name in self._tool_index

    def cleanup(self):
        """Unload all modules and cleanup"""
        for module_id in list(self._modules.keys()):
            self.unload_module(module_id)
        
        BronzeLogger.log_skill_execution(
            self.logger, "MCPModuleRegistry", "cleanup",
            "SUCCESS", "Registry cleaned up"
        )


# Global registry instance
_registry_instance: Optional[MCPModuleRegistry] = None


def get_registry() -> MCPModuleRegistry:
    """Get or create the global registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = MCPModuleRegistry()
    return _registry_instance


def initialize_default_modules():
    """
    Initialize all default MCP modules.
    
    This loads the standard set of modules (Email, Social, Accounting).
    """
    from mcp_server.modules.email_module import EmailModule
    from mcp_server.modules.social_module import SocialModule
    from mcp_server.modules.accounting_module import AccountingModule
    
    registry = get_registry()
    
    # Register module classes
    registry.register_module_class("email", EmailModule)
    registry.register_module_class("social", SocialModule)
    registry.register_module_class("accounting", AccountingModule)
    
    # Load all modules
    registry.load_module("email")
    registry.load_module("social")
    registry.load_module("accounting")
    
    BronzeLogger.log_skill_execution(
        BronzeLogger.get_logger("MCP"), "initialize_default_modules",
        "SUCCESS", f"Loaded {len(registry._modules)} modules"
    )
