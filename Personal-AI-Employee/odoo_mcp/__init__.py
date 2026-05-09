"""Odoo MCP Integration Package"""
from odoo_mcp.connector import OdooConnector, get_odoo_connector
from odoo_mcp.accounting import OdooAccounting
from odoo_mcp.odoo_module import OdooModule

__all__ = [
    'OdooConnector',
    'get_odoo_connector',
    'OdooAccounting',
    'OdooModule'
]
