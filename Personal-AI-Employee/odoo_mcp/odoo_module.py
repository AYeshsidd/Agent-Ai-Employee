#!/usr/bin/env python3
"""Odoo MCP Server - Accounting Operations via MCP Protocol"""
from pathlib import Path
from typing import Dict, Any, List
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from mcp_server.modules.base_module import MCPModule
from odoo_mcp.accounting import OdooAccounting
from odoo_mcp.connector import get_odoo_connector
from bronze_logger import BronzeLogger


class OdooModule(MCPModule):
    """
    Odoo Accounting MCP Module
    
    Provides tools for:
    - Customer Invoices (create, read, list, validate)
    - Vendor Bills (create, read, list)
    - Payments (register, list)
    - Expenses (create, submit, list)
    - Partners (create, search)
    - Reports (accounting summary)
    """
    
    def __init__(self):
        self.accounting = OdooAccounting()
        super().__init__("Odoo")
    
    def _register_tools(self):
        """Register Odoo accounting tools"""
        self._tools = {
            # Invoices
            "odoo_create_invoice": {
                "handler": self._create_invoice,
                "schema": {
                    "name": "odoo_create_invoice",
                    "description": "Create a customer invoice in Odoo",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "partner_id": {
                                "type": "number",
                                "description": "Customer ID"
                            },
                            "invoice_lines": {
                                "type": "array",
                                "description": "Line items with product_id, quantity, price_unit, name",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "product_id": {"type": "number"},
                                        "name": {"type": "string"},
                                        "quantity": {"type": "number"},
                                        "price_unit": {"type": "number"}
                                    }
                                }
                            },
                            "invoice_date": {
                                "type": "string",
                                "description": "Invoice date (YYYY-MM-DD)"
                            },
                            "due_date": {
                                "type": "string",
                                "description": "Due date (YYYY-MM-DD)"
                            }
                        },
                        "required": ["partner_id", "invoice_lines"]
                    }
                }
            },
            "odoo_get_invoice": {
                "handler": self._get_invoice,
                "schema": {
                    "name": "odoo_get_invoice",
                    "description": "Get invoice details by ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "invoice_id": {
                                "type": "number",
                                "description": "Invoice ID"
                            }
                        },
                        "required": ["invoice_id"]
                    }
                }
            },
            "odoo_list_invoices": {
                "handler": self._list_invoices,
                "schema": {
                    "name": "odoo_list_invoices",
                    "description": "List invoices with optional filters",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "partner_id": {
                                "type": "number",
                                "description": "Filter by customer ID"
                            },
                            "state": {
                                "type": "string",
                                "description": "Filter by state (draft, posted, cancel)"
                            },
                            "limit": {
                                "type": "number",
                                "description": "Maximum number of results"
                            }
                        }
                    }
                }
            },
            "odoo_validate_invoice": {
                "handler": self._validate_invoice,
                "schema": {
                    "name": "odoo_validate_invoice",
                    "description": "Post/validate a draft invoice",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "invoice_id": {
                                "type": "number",
                                "description": "Invoice ID to validate"
                            }
                        },
                        "required": ["invoice_id"]
                    }
                }
            },
            
            # Payments
            "odoo_register_payment": {
                "handler": self._register_payment,
                "schema": {
                    "name": "odoo_register_payment",
                    "description": "Register payment for an invoice",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "invoice_id": {
                                "type": "number",
                                "description": "Invoice ID"
                            },
                            "amount": {
                                "type": "number",
                                "description": "Payment amount"
                            },
                            "payment_date": {
                                "type": "string",
                                "description": "Payment date (YYYY-MM-DD)"
                            }
                        },
                        "required": ["invoice_id", "amount"]
                    }
                }
            },
            
            # Expenses
            "odoo_create_expense": {
                "handler": self._create_expense,
                "schema": {
                    "name": "odoo_create_expense",
                    "description": "Create an expense report",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {
                                "type": "number",
                                "description": "Expense product ID"
                            },
                            "amount": {
                                "type": "number",
                                "description": "Expense amount"
                            },
                            "description": {
                                "type": "string",
                                "description": "Expense description"
                            },
                            "date": {
                                "type": "string",
                                "description": "Expense date (YYYY-MM-DD)"
                            }
                        },
                        "required": ["product_id", "amount", "description"]
                    }
                }
            },
            "odoo_list_expenses": {
                "handler": self._list_expenses,
                "schema": {
                    "name": "odoo_list_expenses",
                    "description": "List expenses with filters",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "number",
                                "description": "Filter by employee ID"
                            },
                            "state": {
                                "type": "string",
                                "description": "Filter by state"
                            },
                            "limit": {
                                "type": "number",
                                "description": "Maximum results"
                            }
                        }
                    }
                }
            },
            
            # Partners
            "odoo_create_partner": {
                "handler": self._create_partner,
                "schema": {
                    "name": "odoo_create_partner",
                    "description": "Create a new customer/vendor",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Partner name"
                            },
                            "email": {
                                "type": "string",
                                "description": "Email address"
                            },
                            "phone": {
                                "type": "string",
                                "description": "Phone number"
                            },
                            "is_customer": {
                                "type": "boolean",
                                "description": "Mark as customer"
                            },
                            "is_vendor": {
                                "type": "boolean",
                                "description": "Mark as vendor"
                            }
                        },
                        "required": ["name"]
                    }
                }
            },
            "odoo_search_partner": {
                "handler": self._search_partner,
                "schema": {
                    "name": "odoo_search_partner",
                    "description": "Search for partners",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Search by name"
                            },
                            "email": {
                                "type": "string",
                                "description": "Search by email"
                            }
                        }
                    }
                }
            },
            
            # Reports
            "odoo_get_summary": {
                "handler": self._get_summary,
                "schema": {
                    "name": "odoo_get_summary",
                    "description": "Get accounting summary (receivables, payables)",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            
            # Connection
            "odoo_test_connection": {
                "handler": self._test_connection,
                "schema": {
                    "name": "odoo_test_connection",
                    "description": "Test Odoo connection",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        }
    
    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Odoo tool"""
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
                "message": f"Odoo tool execution failed: {str(e)}"
            }
    
    # Invoice handlers
    def _create_invoice(self, params: Dict) -> Dict:
        return self.accounting.create_customer_invoice(
            partner_id=params['partner_id'],
            invoice_lines=params['invoice_lines'],
            invoice_date=params.get('invoice_date'),
            due_date=params.get('due_date')
        )
    
    def _get_invoice(self, params: Dict) -> Dict:
        return self.accounting.get_invoice(params['invoice_id'])
    
    def _list_invoices(self, params: Dict) -> Dict:
        return self.accounting.list_invoices(
            partner_id=params.get('partner_id'),
            state=params.get('state'),
            limit=params.get('limit', 10)
        )
    
    def _validate_invoice(self, params: Dict) -> Dict:
        return self.accounting.validate_invoice(params['invoice_id'])
    
    # Payment handlers
    def _register_payment(self, params: Dict) -> Dict:
        return self.accounting.register_payment(
            invoice_id=params['invoice_id'],
            amount=params['amount'],
            payment_date=params.get('payment_date')
        )
    
    # Expense handlers
    def _create_expense(self, params: Dict) -> Dict:
        return self.accounting.create_expense(
            product_id=params['product_id'],
            amount=params['amount'],
            description=params['description'],
            date=params.get('date')
        )
    
    def _list_expenses(self, params: Dict) -> Dict:
        return self.accounting.list_expenses(
            employee_id=params.get('employee_id'),
            state=params.get('state'),
            limit=params.get('limit', 10)
        )
    
    # Partner handlers
    def _create_partner(self, params: Dict) -> Dict:
        return self.accounting.create_partner(
            name=params['name'],
            email=params.get('email'),
            phone=params.get('phone'),
            is_customer=params.get('is_customer', True),
            is_vendor=params.get('is_vendor', False)
        )
    
    def _search_partner(self, params: Dict) -> Dict:
        return self.accounting.search_partner(
            name=params.get('name'),
            email=params.get('email')
        )
    
    # Report handlers
    def _get_summary(self, params: Dict) -> Dict:
        return self.accounting.get_account_summary()
    
    def _test_connection(self, params: Dict) -> Dict:
        """Test Odoo connection"""
        try:
            odoo = get_odoo_connector()
            if odoo.authenticate():
                return {
                    "status": "success",
                    "message": f"Connected to Odoo (UID: {odoo.uid})"
                }
            else:
                return {
                    "status": "failed",
                    "message": "Authentication failed"
                }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Connection failed: {str(e)}"
            }
    
    def cleanup(self):
        """Cleanup"""
        super().cleanup()
