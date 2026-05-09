#!/usr/bin/env python3
"""
Action Executor - Executes actions via MCP tools

Executes actions determined by the task analyzer:
- Social media posts (Twitter, Facebook, LinkedIn)
- Accounting operations (invoices, payments, expenses)
- Email sending
- Vault operations
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from ralph_wiggum_loop.core import TaskAction, TaskStatus, get_loop_logger
from config import Config


class ActionExecutor:
    """Executes actions via MCP tools"""
    
    def __init__(self):
        self.logger = get_loop_logger()
        self._mcp_server = None
        self._vault_manager = None
    
    def _get_mcp_server(self):
        """Lazy load MCP server"""
        if self._mcp_server is None:
            from mcp_server import get_server
            self._mcp_server = get_server()
        return self._mcp_server
    
    def _get_vault_manager(self):
        """Lazy load Vault manager"""
        if self._vault_manager is None:
            from vault_manager import VaultManager
            self._vault_manager = VaultManager()
        return self._vault_manager
    
    def execute(self, task_id: str, action: TaskAction, parameters: Dict) -> Dict[str, Any]:
        """
        Execute a single action
        
        Args:
            task_id: Task identifier
            action: Action to execute
            parameters: Action parameters
            
        Returns:
            Execution result
        """
        self.logger.log_step(task_id, f"EXECUTE_{action.value}", "STARTED", parameters)
        
        try:
            # Route to appropriate handler
            handler = self._get_handler(action)
            if handler:
                result = handler(task_id, parameters)
                self.logger.log_step(task_id, f"EXECUTE_{action.value}", 
                                   "SUCCESS" if result.get('status') == 'success' else "ERROR",
                                   result)
                return result
            else:
                return {
                    'status': 'failed',
                    'message': f'No handler for action: {action.value}'
                }
                
        except Exception as e:
            self.logger.log_step(task_id, f"EXECUTE_{action.value}", "ERROR", error=str(e))
            return {
                'status': 'failed',
                'message': str(e)
            }
    
    def _get_handler(self, action: TaskAction):
        """Get handler method for action"""
        handlers = {
            TaskAction.POST_TWITTER: self._post_twitter,
            TaskAction.POST_FACEBOOK: self._post_facebook,
            TaskAction.POST_LINKEDIN: self._post_linkedin,
            TaskAction.CREATE_INVOICE: self._create_invoice,
            TaskAction.REGISTER_PAYMENT: self._register_payment,
            TaskAction.CREATE_EXPENSE: self._create_expense,
            TaskAction.SEND_EMAIL: self._send_email,
            TaskAction.MOVE_TO_DONE: self._move_to_done,
            TaskAction.MOVE_TO_NEEDS_ACTION: self._move_to_needs_action,
        }
        return handlers.get(action)
    
    def _post_twitter(self, task_id: str, params: Dict) -> Dict:
        """Post to Twitter"""
        try:
            from skills.twitter_auto_post_skill import TwitterAutoPostSkill
            
            skill = TwitterAutoPostSkill()
            content = params.get('content', '')
            
            if not content:
                return {'status': 'failed', 'message': 'No content to post'}
            
            success = skill.post_tweet(content, f"ralph_{task_id}")
            
            if success:
                return {'status': 'success', 'message': 'Posted to Twitter'}
            else:
                return {'status': 'failed', 'message': 'Failed to post to Twitter'}
                
        except Exception as e:
            return {'status': 'failed', 'message': str(e)}
    
    def _post_facebook(self, task_id: str, params: Dict) -> Dict:
        """Post to Facebook"""
        try:
            from skills.facebook_auto_post_skill import FacebookAutoPostSkill
            
            skill = FacebookAutoPostSkill()
            content = params.get('content', '')
            
            if not content:
                return {'status': 'failed', 'message': 'No content to post'}
            
            success = skill.post_to_facebook(content, f"ralph_{task_id}")
            
            if success:
                return {'status': 'success', 'message': 'Posted to Facebook'}
            else:
                return {'status': 'failed', 'message': 'Failed to post to Facebook'}
                
        except Exception as e:
            return {'status': 'failed', 'message': str(e)}
    
    def _post_linkedin(self, task_id: str, params: Dict) -> Dict:
        """Post to LinkedIn"""
        try:
            from skills.linkedin_auto_post_skill import LinkedInAutoPostSkill
            
            skill = LinkedInAutoPostSkill()
            content = params.get('content', '')
            
            if not content:
                return {'status': 'failed', 'message': 'No content to post'}
            
            success = skill.post_to_linkedin(content, f"ralph_{task_id}")
            
            if success:
                return {'status': 'success', 'message': 'Posted to LinkedIn'}
            else:
                return {'status': 'failed', 'message': 'Failed to post to LinkedIn'}
                
        except Exception as e:
            return {'status': 'failed', 'message': str(e)}
    
    def _create_invoice(self, task_id: str, params: Dict) -> Dict:
        """Create invoice in Odoo"""
        try:
            from odoo_mcp.accounting import OdooAccounting
            
            accounting = OdooAccounting()
            
            partner_id = params.get('partner_id')
            amount = params.get('amount', 0)
            description = params.get('description', 'Invoice')
            
            if not partner_id:
                return {'status': 'failed', 'message': 'Missing partner_id'}
            
            result = accounting.create_customer_invoice(
                partner_id=partner_id,
                invoice_lines=[{
                    'name': description,
                    'quantity': 1,
                    'price_unit': amount
                }]
            )
            
            return result
                
        except Exception as e:
            return {'status': 'failed', 'message': str(e)}
    
    def _register_payment(self, task_id: str, params: Dict) -> Dict:
        """Register payment in Odoo"""
        try:
            from odoo_mcp.accounting import OdooAccounting
            
            accounting = OdooAccounting()
            
            invoice_id = params.get('invoice_id')
            amount = params.get('amount', 0)
            
            if not invoice_id:
                return {'status': 'failed', 'message': 'Missing invoice_id'}
            
            result = accounting.register_payment(invoice_id, amount)
            return result
                
        except Exception as e:
            return {'status': 'failed', 'message': str(e)}
    
    def _create_expense(self, task_id: str, params: Dict) -> Dict:
        """Create expense in Odoo"""
        try:
            from odoo_mcp.accounting import OdooAccounting
            
            accounting = OdooAccounting()
            
            # Use default product ID if not specified
            product_id = params.get('product_id', 1)
            amount = params.get('amount', 0)
            description = params.get('description', 'Expense')
            
            result = accounting.create_expense(product_id, amount, description)
            return result
                
        except Exception as e:
            return {'status': 'failed', 'message': str(e)}
    
    def _send_email(self, task_id: str, params: Dict) -> Dict:
        """Send email via MCP"""
        try:
            server = self._get_mcp_server()
            
            to = params.get('to')
            subject = params.get('subject', 'No Subject')
            body = params.get('body', params.get('description', ''))
            
            if not to:
                return {'status': 'failed', 'message': 'Missing recipient email'}
            
            result = server.call_tool('send_email', {
                'to': to,
                'subject': subject,
                'body': body
            })
            
            return result
                
        except Exception as e:
            return {'status': 'failed', 'message': str(e)}
    
    def _move_to_done(self, task_id: str, params: Dict) -> Dict:
        """Move task to Done folder"""
        try:
            vault = self._get_vault_manager()
            
            task_path = params.get('task_path')
            if not task_path:
                task_path = Config.NEEDS_ACTION / f"{task_id}.md"
            
            if not Path(task_path).exists():
                return {'status': 'skipped', 'message': 'Task file not found'}
            
            new_path = vault.move_task(Path(task_path), 'done')
            
            if new_path:
                return {'status': 'success', 'message': f'Moved to Done: {new_path.name}'}
            else:
                return {'status': 'failed', 'message': 'Failed to move task'}
                
        except Exception as e:
            return {'status': 'failed', 'message': str(e)}
    
    def _move_to_needs_action(self, task_id: str, params: Dict) -> Dict:
        """Move task to Needs_Action folder"""
        try:
            vault = self._get_vault_manager()
            
            task_path = params.get('task_path')
            if not task_path:
                task_path = Config.INBOX / f"{task_id}.md"
            
            if not Path(task_path).exists():
                return {'status': 'skipped', 'message': 'Task file not found'}
            
            new_path = vault.move_task(Path(task_path), 'needs_action')
            
            if new_path:
                return {'status': 'success', 'message': f'Moved to Needs_Action: {new_path.name}'}
            else:
                return {'status': 'failed', 'message': 'Failed to move task'}
                
        except Exception as e:
            return {'status': 'failed', 'message': str(e)}
