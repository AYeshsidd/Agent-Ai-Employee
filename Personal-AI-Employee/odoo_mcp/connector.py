#!/usr/bin/env python3
"""Odoo Connector - JSON-RPC API Client for Odoo Community Edition"""
import requests
import json
from typing import Any, Dict, List, Optional
from pathlib import Path
import sys

# Ensure project root is in sys.path
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from config import Config
from bronze_logger import BronzeLogger


class OdooConnector:
    """
    Odoo JSON-RPC API Connector
    
    Connects to self-hosted Odoo Community Edition via JSON-RPC API
    Supports: Authentication, CRUD operations, model queries
    """
    
    def __init__(self):
        self.logger = BronzeLogger.get_logger("OdooConnector")
        self.config_file = Config.BASE_DIR / "credentials" / "odoo_config.json"
        self.session = requests.Session()
        self.authenticated = False
        self.uid = None  # User ID
        self.db = None
        self.url = None
        self._load_config()
    
    def _load_config(self):
        """Load Odoo configuration from secure file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.url = config.get('url', 'http://localhost:8069')
                self.db = config.get('database', 'odoo')
                self.username = config.get('username', 'admin')
                self.password = config.get('password', '')
                BronzeLogger.log_skill_execution(
                    self.logger, "OdooConnector", "_load_config",
                    "SUCCESS", f"Loaded config for {self.url}"
                )
            except Exception as e:
                BronzeLogger.log_skill_execution(
                    self.logger, "OdooConnector", "_load_config",
                    "FAILED", str(e)
                )
                raise
        else:
            raise FileNotFoundError(
                f"Odoo config not found at {self.config_file}. "
                "Please run odoo_setup.py first."
            )
    
    def authenticate(self) -> bool:
        """
        Authenticate with Odoo using JSON-RPC (Odoo 19+)
        
        Returns:
            True if authentication successful
        """
        try:
            BronzeLogger.log_skill_execution(
                self.logger, "OdooConnector", "authenticate",
                "IN_PROGRESS", f"Authenticating to {self.url}"
            )
            
            # Odoo 19+ authentication format
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "db": self.db,
                    "login": self.username,
                    "password": self.password,
                    "context": {}
                },
                "id": 1
            }
            
            response = self.session.post(
                f"{self.url}/web/session/authenticate",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            result = response.json()
            
            if result.get('result', {}).get('uid'):
                self.uid = result['result']['uid']
                self.authenticated = True
                BronzeLogger.log_skill_execution(
                    self.logger, "OdooConnector", "authenticate",
                    "SUCCESS", f"Authenticated as UID: {self.uid}"
                )
                return True
            else:
                BronzeLogger.log_skill_execution(
                    self.logger, "OdooConnector", "authenticate",
                    "FAILED", "Authentication failed - invalid credentials"
                )
                return False
                
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "OdooConnector", "authenticate",
                "FAILED", str(e)
            )
            return False
    
    def execute(self, model: str, method: str, args: List = None, kwargs: Dict = None) -> Any:
        """
        Execute a method on an Odoo model
        
        Args:
            model: Odoo model name (e.g., 'account.move', 'res.partner')
            method: Method to call (e.g., 'create', 'read', 'search')
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Result from Odoo
        """
        if not self.authenticated:
            if not self.authenticate():
                raise Exception("Not authenticated with Odoo")
        
        try:
            # Use session-based call (no need to re-authenticate)
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "model": model,
                    "method": method,
                    "args": args or [],
                    "kwargs": kwargs or {}
                },
                "id": 3
            }
            
            response = self.session.post(
                f"{self.url}/web/dataset/call_kw",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            # Check if response is valid JSON
            try:
                result = response.json()
            except:
                raise Exception(f"Invalid response from Odoo: {response.text[:200]}")
            
            if 'error' in result:
                error_msg = result['error'].get('data', {}).get('message', str(result['error']))
                raise Exception(f"Odoo API Error: {error_msg}")
            
            return result.get('result')
            
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "OdooConnector", "execute",
                "FAILED", f"{model}.{method}: {str(e)}"
            )
            raise
    
    def search(self, model: str, domain: List = None, limit: int = 80) -> List[int]:
        """Search for records"""
        return self.execute(model, 'search', [domain or []], {'limit': limit})
    
    def search_read(self, model: str, domain: List = None, fields: List = None, limit: int = 80) -> List[Dict]:
        """Search and read records"""
        return self.execute(model, 'search_read', [domain or []], {
            'fields': fields,
            'limit': limit
        })
    
    def read(self, model: str, ids: List[int], fields: List = None) -> List[Dict]:
        """Read specific records by ID"""
        return self.execute(model, 'read', [ids], {'fields': fields})
    
    def create(self, model: str, values: Dict) -> int:
        """Create a new record"""
        return self.execute(model, 'create', [values])
    
    def write(self, model: str, ids: List[int], values: Dict) -> bool:
        """Update existing records"""
        return self.execute(model, 'write', [ids, values])
    
    def unlink(self, model: str, ids: List[int]) -> bool:
        """Delete records"""
        return self.execute(model, 'unlink', [ids])
    
    def get_model_fields(self, model: str) -> Dict:
        """Get fields definition for a model"""
        return self.execute(model, 'fields_get', [], {})
    
    def check_access(self, model: str, operation: str = 'read') -> bool:
        """Check access rights for a model"""
        try:
            return self.execute(model, 'check_access_rights', [operation])
        except:
            return False


# Singleton instance
_connector_instance: Optional[OdooConnector] = None


def get_odoo_connector() -> OdooConnector:
    """Get or create Odoo connector singleton"""
    global _connector_instance
    if _connector_instance is None:
        _connector_instance = OdooConnector()
    return _connector_instance
