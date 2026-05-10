#!/usr/bin/env python3
"""Odoo Task Integration - Process Needs_Action tasks with Odoo operations"""
import sys
import re
from pathlib import Path

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from vault_manager import VaultManager
from odoo_mcp.odoo_module import OdooModule
from bronze_logger import BronzeLogger
from config import Config


class OdooTaskIntegration:
    """
    Integrates Odoo operations with Needs_Action tasks
    
    Workflow:
    1. Read task from Needs_Action
    2. Parse task for Odoo operation type
    3. Execute Odoo operation via MCP
    4. Log result to task file
    5. Move to Done folder
    """
    
    def __init__(self):
        self.logger = BronzeLogger.get_logger("OdooTaskIntegration")
        self.vault = VaultManager()
        self.odoo = OdooModule()
    
    def process_task(self, task_filename: str) -> dict:
        """
        Process a task from Needs_Action folder
        
        Args:
            task_filename: Name of task file in Needs_Action
            
        Returns:
            Result dictionary
        """
        task_path = Config.NEEDS_ACTION / task_filename
        
        if not task_path.exists():
            return {
                'status': 'failed',
                'message': f'Task not found: {task_filename}'
            }
        
        # Read task content
        content = self.vault.read_task(task_path)
        if not content:
            return {
                'status': 'failed',
                'message': 'Could not read task'
            }
        
        # Determine operation type
        operation = self._detect_operation(content)
        
        if not operation:
            return {
                'status': 'failed',
                'message': 'No Odoo operation detected in task'
            }
        
        # Execute operation
        result = self._execute_operation(operation, content)
        
        # Update task with result
        if result.get('status') == 'success':
            self._update_task(task_path, result)
            self._move_to_done(task_path)
        
        return result
    
    def _detect_operation(self, content: str) -> str:
        """Detect Odoo operation from task content"""
        content_lower = content.lower()
        
        if 'create invoice' in content_lower or 'new invoice' in content_lower:
            return 'create_invoice'
        elif 'validate invoice' in content_lower or 'post invoice' in content_lower:
            return 'validate_invoice'
        elif 'register payment' in content_lower or 'payment received' in content_lower:
            return 'register_payment'
        elif 'create expense' in content_lower or 'new expense' in content_lower:
            return 'create_expense'
        elif 'create customer' in content_lower or 'new partner' in content_lower:
            return 'create_partner'
        elif 'accounting summary' in content_lower or 'financial summary' in content_lower:
            return 'get_summary'
        
        return None
    
    def _execute_operation(self, operation: str, content: str) -> dict:
        """Execute Odoo operation based on task content"""
        
        if operation == 'create_invoice':
            return self._create_invoice_from_task(content)
        elif operation == 'validate_invoice':
            return self._validate_invoice_from_task(content)
        elif operation == 'register_payment':
            return self._register_payment_from_task(content)
        elif operation == 'create_expense':
            return self._create_expense_from_task(content)
        elif operation == 'create_partner':
            return self._create_partner_from_task(content)
        elif operation == 'get_summary':
            return self.odoo.execute('odoo_get_summary', {})
        
        return {'status': 'failed', 'message': 'Unknown operation'}
    
    def _extract_value(self, content: str, key: str) -> str:
        """Extract value from task content"""
        pattern = rf'\*\*{key}\*\*:\s*(.+?)(?:\n|$)'
        match = re.search(pattern, content, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def _create_invoice_from_task(self, content: str) -> dict:
        """Create invoice from task"""
        partner_id = self._extract_value(content, 'Partner ID')
        amount = self._extract_value(content, 'Amount')
        description = self._extract_value(content, 'Description')
        
        if not partner_id or not amount:
            # Try to extract from different format
            if 'partner_id:' in content.lower():
                partner_id = content.lower().split('partner_id:')[1].split('\n')[0].strip()
            if 'amount:' in content.lower():
                amount = content.lower().split('amount:')[1].split('\n')[0].strip()
        
        try:
            partner_id = int(partner_id)
            amount = float(amount)
        except (ValueError, TypeError):
            return {
                'status': 'failed',
                'message': 'Invalid partner_id or amount'
            }
        
        return self.odoo.execute('odoo_create_invoice', {
            'partner_id': partner_id,
            'invoice_lines': [{
                'name': description or 'Service',
                'quantity': 1,
                'price_unit': amount
            }]
        })
    
    def _validate_invoice_from_task(self, content: str) -> dict:
        """Validate invoice from task"""
        invoice_id = self._extract_value(content, 'Invoice ID')
        
        if not invoice_id:
            return {'status': 'failed', 'message': 'Invoice ID not found'}
        
        try:
            invoice_id = int(invoice_id)
        except ValueError:
            return {'status': 'failed', 'message': 'Invalid Invoice ID'}
        
        return self.odoo.execute('odoo_validate_invoice', {
            'invoice_id': invoice_id
        })
    
    def _register_payment_from_task(self, content: str) -> dict:
        """Register payment from task"""
        invoice_id = self._extract_value(content, 'Invoice ID')
        amount = self._extract_value(content, 'Amount')
        
        if not invoice_id or not amount:
            return {'status': 'failed', 'message': 'Missing Invoice ID or Amount'}
        
        try:
            invoice_id = int(invoice_id)
            amount = float(amount)
        except ValueError:
            return {'status': 'failed', 'message': 'Invalid numeric values'}
        
        return self.odoo.execute('odoo_register_payment', {
            'invoice_id': invoice_id,
            'amount': amount
        })
    
    def _create_expense_from_task(self, content: str) -> dict:
        """Create expense from task"""
        product_id = self._extract_value(content, 'Product ID')
        amount = self._extract_value(content, 'Amount')
        description = self._extract_value(content, 'Description')
        
        if not product_id or not amount:
            return {'status': 'failed', 'message': 'Missing Product ID or Amount'}
        
        try:
            product_id = int(product_id)
            amount = float(amount)
        except ValueError:
            return {'status': 'failed', 'message': 'Invalid numeric values'}
        
        return self.odoo.execute('odoo_create_expense', {
            'product_id': product_id,
            'amount': amount,
            'description': description or 'Expense'
        })
    
    def _create_partner_from_task(self, content: str) -> dict:
        """Create partner from task"""
        name = self._extract_value(content, 'Name')
        email = self._extract_value(content, 'Email')
        phone = self._extract_value(content, 'Phone')
        
        if not name:
            return {'status': 'failed', 'message': 'Partner name required'}
        
        return self.odoo.execute('odoo_create_partner', {
            'name': name,
            'email': email,
            'phone': phone,
            'is_customer': True
        })
    
    def _update_task(self, task_path: Path, result: dict):
        """Update task file with Odoo result"""
        try:
            content = task_path.read_text(encoding='utf-8')
            
            # Add result section
            result_section = f"""

## Odoo Operation Result

**Status**: {result.get('status', 'unknown').upper()}
**Executed**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Result**: {result.get('message', 'No message')}

"""
            content += result_section
            task_path.write_text(content, encoding='utf-8')
            
            BronzeLogger.log_skill_execution(
                self.logger, "OdooTaskIntegration", "_update_task",
                "SUCCESS", f"Task updated: {task_path.name}"
            )
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "OdooTaskIntegration", "_update_task",
                "FAILED", str(e)
            )
    
    def _move_to_done(self, task_path: Path):
        """Move task to Done folder"""
        try:
            new_path = self.vault.move_task(task_path, 'done')
            BronzeLogger.log_skill_execution(
                self.logger, "OdooTaskIntegration", "_move_to_done",
                "SUCCESS", f"Moved to Done: {new_path.name if new_path else 'unknown'}"
            )
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "OdooTaskIntegration", "_move_to_done",
                "FAILED", str(e)
            )


def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("  ODOO TASK INTEGRATION")
    print("=" * 70)
    
    integration = OdooTaskIntegration()
    
    # Get task filename
    if len(sys.argv) > 1:
        task_filename = sys.argv[1]
    else:
        task_filename = input("\nEnter task filename from Needs_Action: ").strip()
    
    if not task_filename:
        print("\n[ERROR] No task specified")
        return
    
    print(f"\n[INFO] Processing: {task_filename}")
    result = integration.process_task(task_filename)
    
    print(f"\n[RESULT] {result.get('status', 'unknown').upper()}")
    print(f"         {result.get('message', 'No message')}")
    
    if result.get('status') == 'success':
        print(f"\n[OK] Task processed and moved to Done folder")
    else:
        print(f"\n[WARN] Task not completed - check error above")


if __name__ == "__main__":
    main()
