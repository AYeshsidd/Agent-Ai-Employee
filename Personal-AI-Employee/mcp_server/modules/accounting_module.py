#!/usr/bin/env python3
"""Accounting MCP Module - Handles accounting and financial operations"""
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mcp_server.modules.base_module import MCPModule
from config import Config


class AccountingModule(MCPModule):
    """
    Accounting and financial operations module.
    
    Provides tools for:
    - Invoice generation (future)
    - Expense tracking (future)
    - Financial reporting (future)
    - Payment reminders (future)
    """

    def __init__(self):
        self.accounting_dir = Config.VAULT_ROOT / "Accounting"
        self.invoices_dir = self.accounting_dir / "Invoices"
        self.expenses_dir = self.accounting_dir / "Expenses"
        self.reports_dir = self.accounting_dir / "Reports"
        
        # Ensure directories exist
        self._initialize_directories()
        
        super().__init__("Accounting")

    def _initialize_directories(self):
        """Create accounting directory structure"""
        self.accounting_dir.mkdir(exist_ok=True)
        self.invoices_dir.mkdir(exist_ok=True)
        self.expenses_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

    def _register_tools(self):
        """Register accounting tools"""
        self._tools = {
            "create_invoice": {
                "handler": self._create_invoice,
                "schema": {
                    "name": "create_invoice",
                    "description": "Create a new invoice",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "client_name": {
                                "type": "string",
                                "description": "Client name"
                            },
                            "client_email": {
                                "type": "string",
                                "description": "Client email"
                            },
                            "amount": {
                                "type": "number",
                                "description": "Invoice amount"
                            },
                            "description": {
                                "type": "string",
                                "description": "Invoice description"
                            },
                            "due_date": {
                                "type": "string",
                                "description": "Due date (YYYY-MM-DD)"
                            }
                        },
                        "required": ["client_name", "amount", "description"]
                    }
                }
            },
            "track_expense": {
                "handler": self._track_expense,
                "schema": {
                    "name": "track_expense",
                    "description": "Record a business expense",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Expense category"
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
                        "required": ["category", "amount", "description"]
                    }
                }
            },
            "generate_financial_report": {
                "handler": self._generate_financial_report,
                "schema": {
                    "name": "generate_financial_report",
                    "description": "Generate a financial summary report",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "period": {
                                "type": "string",
                                "description": "Report period (weekly, monthly, quarterly, yearly)"
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Start date (YYYY-MM-DD)"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date (YYYY-MM-DD)"
                            }
                        },
                        "required": ["period"]
                    }
                }
            },
            "send_payment_reminder": {
                "handler": self._send_payment_reminder,
                "schema": {
                    "name": "send_payment_reminder",
                    "description": "Send a payment reminder email",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "invoice_id": {
                                "type": "string",
                                "description": "Invoice identifier"
                            },
                            "client_email": {
                                "type": "string",
                                "description": "Client email"
                            },
                            "message": {
                                "type": "string",
                                "description": "Custom reminder message"
                            }
                        },
                        "required": ["invoice_id", "client_email"]
                    }
                }
            }
        }

    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute accounting tool"""
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
                "message": f"Accounting tool execution failed: {str(e)}"
            }

    def _create_invoice(self, params: Dict[str, Any]) -> Dict[str, str]:
        """Create invoice"""
        client_name = params.get("client_name", "")
        client_email = params.get("client_email", "")
        amount = params.get("amount", 0)
        description = params.get("description", "")
        due_date = params.get("due_date", "")

        if not due_date:
            # Default to 30 days
            from datetime import timedelta
            due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        invoice_id = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        invoice_data = {
            "invoice_id": invoice_id,
            "client_name": client_name,
            "client_email": client_email,
            "amount": amount,
            "description": description,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "due_date": due_date,
            "status": "pending"
        }

        # Save invoice
        invoice_file = self.invoices_dir / f"{invoice_id}.json"
        with open(invoice_file, 'w', encoding='utf-8') as f:
            json.dump(invoice_data, f, indent=2)

        return {
            "status": "success",
            "message": f"Invoice {invoice_id} created for {client_name}",
            "invoice_id": invoice_id
        }

    def _track_expense(self, params: Dict[str, Any]) -> Dict[str, str]:
        """Track expense"""
        category = params.get("category", "")
        amount = params.get("amount", 0)
        description = params.get("description", "")
        date = params.get("date", datetime.now().strftime("%Y-%m-%d"))

        expense_id = f"EXP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        expense_data = {
            "expense_id": expense_id,
            "category": category,
            "amount": amount,
            "description": description,
            "date": date,
            "recorded_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save expense
        expense_file = self.expenses_dir / f"{expense_id}.json"
        with open(expense_file, 'w', encoding='utf-8') as f:
            json.dump(expense_data, f, indent=2)

        return {
            "status": "success",
            "message": f"Expense {expense_id} recorded: ${amount} in {category}",
            "expense_id": expense_id
        }

    def _generate_financial_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate financial report"""
        period = params.get("period", "monthly")
        start_date = params.get("start_date")
        end_date = params.get("end_date")

        # Load all invoices and expenses
        invoices = self._load_all_invoices()
        expenses = self._load_all_expenses()

        # Calculate totals
        total_revenue = sum(inv.get("amount", 0) for inv in invoices)
        total_expenses = sum(exp.get("amount", 0) for exp in expenses)
        net_income = total_revenue - total_expenses

        # Generate report
        report_id = f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        report_data = {
            "report_id": report_id,
            "period": period,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_revenue": total_revenue,
                "total_expenses": total_expenses,
                "net_income": net_income,
                "invoice_count": len(invoices),
                "expense_count": len(expenses)
            },
            "invoices": invoices,
            "expenses": expenses
        }

        # Save report
        report_file = self.reports_dir / f"{report_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

        return {
            "status": "success",
            "message": f"Financial report generated: {report_id}",
            "report_id": report_id,
            "summary": report_data["summary"]
        }

    def _send_payment_reminder(self, params: Dict[str, Any]) -> Dict[str, str]:
        """Send payment reminder"""
        invoice_id = params.get("invoice_id", "")
        client_email = params.get("client_email", "")
        message = params.get("message", "")

        # Load invoice
        invoice_file = self.invoices_dir / f"{invoice_id}.json"
        if not invoice_file.exists():
            return {
                "status": "failed",
                "message": f"Invoice {invoice_id} not found"
            }

        with open(invoice_file, 'r', encoding='utf-8') as f:
            invoice = json.load(f)

        # Placeholder - would integrate with EmailModule
        return {
            "status": "success",
            "message": f"Payment reminder queued for invoice {invoice_id} to {client_email}"
        }

    def _load_all_invoices(self) -> List[Dict[str, Any]]:
        """Load all invoices from disk"""
        invoices = []
        for invoice_file in self.invoices_dir.glob("*.json"):
            try:
                with open(invoice_file, 'r', encoding='utf-8') as f:
                    invoices.append(json.load(f))
            except Exception:
                continue
        return invoices

    def _load_all_expenses(self) -> List[Dict[str, Any]]:
        """Load all expenses from disk"""
        expenses = []
        for expense_file in self.expenses_dir.glob("*.json"):
            try:
                with open(expense_file, 'r', encoding='utf-8') as f:
                    expenses.append(json.load(f))
            except Exception:
                continue
        return expenses

    def cleanup(self):
        """Cleanup accounting module resources"""
        super().cleanup()
