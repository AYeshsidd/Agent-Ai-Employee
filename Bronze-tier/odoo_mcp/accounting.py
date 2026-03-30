#!/usr/bin/env python3
"""Odoo Accounting Operations - Invoices, Payments, Expenses"""
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from odoo_mcp.connector import get_odoo_connector
from bronze_logger import BronzeLogger


class OdooAccounting:
    """
    Odoo Accounting Operations
    
    Provides high-level accounting operations:
    - Customer Invoices
    - Vendor Bills
    - Payments
    - Expenses
    - Journal Entries
    """
    
    def __init__(self):
        self.logger = BronzeLogger.get_logger("OdooAccounting")
        self.odoo = get_odoo_connector()
    
    # ==================== CUSTOMER INVOICES ====================
    
    def create_customer_invoice(self, partner_id: int, invoice_lines: List[Dict], 
                                invoice_date: str = None, due_date: str = None,
                                payment_term_id: int = None) -> Dict[str, Any]:
        """
        Create a customer invoice
        
        Args:
            partner_id: Customer ID
            invoice_lines: List of line items with product_id, quantity, price
            invoice_date: Invoice date (YYYY-MM-DD)
            due_date: Due date (YYYY-MM-DD)
            payment_term_id: Payment term ID
            
        Returns:
            Invoice data including ID
        """
        try:
            BronzeLogger.log_skill_execution(
                self.logger, "OdooAccounting", "create_customer_invoice",
                "IN_PROGRESS", f"Creating invoice for partner {partner_id}"
            )
            
            # Prepare invoice lines
            lines = []
            for line in invoice_lines:
                lines.append((0, 0, {
                    'product_id': line.get('product_id'),
                    'name': line.get('name', 'Service'),
                    'quantity': line.get('quantity', 1),
                    'price_unit': line.get('price_unit', 0),
                    'account_id': line.get('account_id')
                }))
            
            invoice_data = {
                'move_type': 'out_invoice',
                'partner_id': partner_id,
                'invoice_line_ids': lines,
                'invoice_date': invoice_date or datetime.now().strftime('%Y-%m-%d'),
            }
            
            if due_date:
                invoice_data['invoice_date_due'] = due_date
            
            if payment_term_id:
                invoice_data['invoice_payment_term_id'] = payment_term_id
            
            invoice_id = self.odoo.create('account.move', invoice_data)
            
            BronzeLogger.log_skill_execution(
                self.logger, "OdooAccounting", "create_customer_invoice",
                "SUCCESS", f"Invoice created: {invoice_id}"
            )
            
            return {
                'status': 'success',
                'invoice_id': invoice_id,
                'message': f'Customer invoice {invoice_id} created'
            }
            
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "OdooAccounting", "create_customer_invoice",
                "FAILED", str(e)
            )
            return {
                'status': 'failed',
                'message': str(e)
            }
    
    def get_invoice(self, invoice_id: int) -> Dict:
        """Get invoice details"""
        try:
            invoices = self.odoo.read('account.move', [invoice_id], 
                                     ['name', 'partner_id', 'amount_total', 
                                      'amount_due', 'state', 'invoice_date'])
            if invoices:
                return {
                    'status': 'success',
                    'invoice': invoices[0]
                }
            return {
                'status': 'failed',
                'message': 'Invoice not found'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': str(e)
            }
    
    def list_invoices(self, partner_id: int = None, state: str = None, limit: int = 10) -> List[Dict]:
        """List invoices with optional filters"""
        try:
            domain = []
            if partner_id:
                domain.append(('partner_id', '=', partner_id))
            if state:
                domain.append(('state', '=', state))
            
            invoices = self.odoo.search_read('account.move', domain, 
                                            ['name', 'partner_id', 'amount_total', 
                                             'amount_due', 'state', 'invoice_date'],
                                            limit=limit)
            return {
                'status': 'success',
                'invoices': invoices
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': str(e)
            }
    
    def validate_invoice(self, invoice_id: int) -> Dict:
        """Post/validate an invoice"""
        try:
            self.odoo.execute('account.move', 'action_post', [invoice_id])
            return {
                'status': 'success',
                'message': f'Invoice {invoice_id} validated'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': str(e)
            }
    
    # ==================== VENDOR BILLS ====================
    
    def create_vendor_bill(self, partner_id: int, bill_lines: List[Dict],
                          bill_date: str = None, due_date: str = None) -> Dict[str, Any]:
        """Create a vendor bill"""
        try:
            lines = []
            for line in bill_lines:
                lines.append((0, 0, {
                    'product_id': line.get('product_id'),
                    'name': line.get('name', 'Expense'),
                    'quantity': line.get('quantity', 1),
                    'price_unit': line.get('price_unit', 0),
                    'account_id': line.get('account_id')
                }))
            
            bill_data = {
                'move_type': 'in_invoice',
                'partner_id': partner_id,
                'invoice_line_ids': lines,
                'invoice_date': bill_date or datetime.now().strftime('%Y-%m-%d'),
            }
            
            if due_date:
                bill_data['invoice_date_due'] = due_date
            
            bill_id = self.odoo.create('account.move', bill_data)
            
            return {
                'status': 'success',
                'bill_id': bill_id,
                'message': f'Vendor bill {bill_id} created'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': str(e)
            }
    
    # ==================== PAYMENTS ====================
    
    def register_payment(self, invoice_id: int, amount: float, 
                        payment_date: str = None, payment_method: str = 'manual') -> Dict:
        """Register payment for an invoice"""
        try:
            payment_data = {
                'amount': amount,
                'payment_date': payment_date or datetime.now().strftime('%Y-%m-%d'),
                'payment_method_line_id': payment_method,
            }
            
            # Create payment wizard
            wizard_id = self.odoo.execute('account.move', 'action_register_payment', [invoice_id])
            
            return {
                'status': 'success',
                'message': f'Payment of {amount} registered for invoice {invoice_id}'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': str(e)
            }
    
    def get_payments(self, limit: int = 10) -> List[Dict]:
        """List recent payments"""
        try:
            payments = self.odoo.search_read('account.payment', [],
                                           ['name', 'amount', 'payment_date', 'state'],
                                           limit=limit)
            return {
                'status': 'success',
                'payments': payments
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': str(e)
            }
    
    # ==================== EXPENSES ====================
    
    def create_expense(self, product_id: int, amount: float, description: str,
                      date: str = None, employee_id: int = None) -> Dict:
        """Create an expense report"""
        try:
            expense_data = {
                'product_id': product_id,
                'total_amount': amount,
                'name': description,
                'date': date or datetime.now().strftime('%Y-%m-%d'),
            }
            
            if employee_id:
                expense_data['employee_id'] = employee_id
            
            expense_id = self.odoo.create('hr.expense', expense_data)
            
            return {
                'status': 'success',
                'expense_id': expense_id,
                'message': f'Expense {expense_id} created'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': str(e)
            }
    
    def list_expenses(self, employee_id: int = None, state: str = None, limit: int = 10) -> Dict:
        """List expenses with filters"""
        try:
            domain = []
            if employee_id:
                domain.append(('employee_id', '=', employee_id))
            if state:
                domain.append(('state', '=', state))
            
            expenses = self.odoo.search_read('hr.expense', domain,
                                           ['name', 'total_amount', 'date', 'state'],
                                           limit=limit)
            return {
                'status': 'success',
                'expenses': expenses
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': str(e)
            }
    
    def submit_expense(self, expense_id: int) -> Dict:
        """Submit expense for approval"""
        try:
            self.odoo.execute('hr.expense', 'action_submit', [[expense_id]])
            return {
                'status': 'success',
                'message': f'Expense {expense_id} submitted for approval'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': str(e)
            }
    
    # ==================== PARTNERS (CUSTOMERS/VENDORS) ====================
    
    def create_partner(self, name: str, email: str = None, phone: str = None,
                      is_customer: bool = True, is_vendor: bool = False) -> Dict:
        """Create a new partner (customer/vendor)"""
        try:
            partner_data = {
                'name': name,
            }
            
            if email:
                partner_data['email'] = email
            if phone:
                partner_data['phone'] = phone
            
            # Set customer/vendor flags
            if is_customer:
                partner_data['customer_rank'] = 1
            if is_vendor:
                partner_data['supplier_rank'] = 1
            
            partner_id = self.odoo.create('res.partner', partner_data)
            
            return {
                'status': 'success',
                'partner_id': partner_id,
                'message': f'Partner {name} created with ID {partner_id}'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': str(e)
            }
    
    def search_partner(self, name: str = None, email: str = None) -> Dict:
        """Search for partners"""
        try:
            domain = []
            if name:
                domain.append(('name', 'ilike', name))
            if email:
                domain.append(('email', '=', email))
            
            partners = self.odoo.search_read('res.partner', domain,
                                           ['name', 'email', 'phone'],
                                           limit=10)
            return {
                'status': 'success',
                'partners': partners
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': str(e)
            }
    
    # ==================== REPORTS ====================
    
    def get_account_summary(self) -> Dict:
        """Get basic accounting summary"""
        try:
            # Get total receivables
            receivables = self.odoo.search_read('account.move', 
                                               [('move_type', '=', 'out_invoice'), 
                                                ('state', '=', 'posted')],
                                               ['amount_total', 'amount_due'])
            
            # Get total payables
            payables = self.odoo.search_read('account.move',
                                            [('move_type', '=', 'in_invoice'),
                                             ('state', '=', 'posted')],
                                            ['amount_total', 'amount_due'])
            
            total_receivable = sum(inv.get('amount_due', 0) for inv in receivables)
            total_payable = sum(bill.get('amount_due', 0) for bill in payables)
            
            return {
                'status': 'success',
                'summary': {
                    'total_receivables': total_receivable,
                    'total_payables': total_payable,
                    'customer_invoices': len(receivables),
                    'vendor_bills': len(payables)
                }
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': str(e)
            }
