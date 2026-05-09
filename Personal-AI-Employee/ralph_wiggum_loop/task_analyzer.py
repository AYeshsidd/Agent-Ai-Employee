#!/usr/bin/env python3
"""
Task Analyzer - Detects task types and extracts metadata

Analyzes task content to determine:
- Task type (Social, Accounting, Email, etc.)
- Required actions
- Priority and complexity
- Required parameters for execution
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from ralph_wiggum_loop.core import TaskType, TaskAction, get_loop_logger
from config import Config


class TaskAnalyzer:
    """Analyzes tasks and determines type and required actions"""
    
    def __init__(self):
        self.logger = get_loop_logger()
        
        # Keywords for task type detection
        self.type_keywords = {
            TaskType.SOCIAL_TWITTER: ['twitter', 'tweet', 'post to twitter', 'x.com'],
            TaskType.SOCIAL_FACEBOOK: ['facebook', 'fb', 'post to facebook', 'meta'],
            TaskType.SOCIAL_LINKEDIN: ['linkedin', 'post to linkedin', 'professional'],
            TaskType.ACCOUNTING_INVOICE: ['invoice', 'create invoice', 'bill', 'billing'],
            TaskType.ACCOUNTING_PAYMENT: ['payment', 'register payment', 'payment received'],
            TaskType.ACCOUNTING_EXPENSE: ['expense', 'create expense', 'reimbursement'],
            TaskType.EMAIL_SEND: ['email', 'send email', 'mail'],
            TaskType.VAULT_MOVE: ['move to', 'archive', 'complete task'],
        }
        
        # Action keywords
        self.action_keywords = {
            TaskAction.POST_TWITTER: ['post', 'tweet', 'publish'],
            TaskAction.POST_FACEBOOK: ['post', 'share', 'publish'],
            TaskAction.POST_LINKEDIN: ['post', 'share', 'publish'],
            TaskAction.CREATE_INVOICE: ['create', 'generate', 'send invoice'],
            TaskAction.REGISTER_PAYMENT: ['payment', 'paid', 'received'],
            TaskAction.CREATE_EXPENSE: ['expense', 'reimburse', 'cost'],
            TaskAction.SEND_EMAIL: ['email', 'send', 'mail'],
            TaskAction.MOVE_TO_DONE: ['done', 'complete', 'finish', 'archive'],
        }
    
    def analyze_task(self, task_path: Path) -> Dict[str, Any]:
        """
        Analyze a task file and extract all relevant information
        
        Args:
            task_path: Path to task markdown file
            
        Returns:
            Dictionary with task analysis results
        """
        task_id = task_path.stem
        
        self.logger.log_step(task_id, "ANALYZE_START", "STARTED", 
                            {"file": str(task_path)})
        
        try:
            # Read task content
            content = task_path.read_text(encoding='utf-8')
            
            # Extract metadata
            metadata = self._extract_metadata(content, task_path)
            
            # Detect task type
            task_type = self._detect_task_type(content, metadata)
            
            # Determine required actions
            actions = self._determine_actions(content, task_type)
            
            # Extract parameters for actions
            parameters = self._extract_parameters(content, task_type, metadata)
            
            # Calculate priority
            priority = self._calculate_priority(content, metadata)
            
            result = {
                "task_id": task_id,
                "task_path": str(task_path),
                "task_type": task_type.value,
                "actions": [a.value for a in actions],
                "parameters": parameters,
                "priority": priority,
                "metadata": metadata,
                "content_preview": content[:200]
            }
            
            self.logger.log_step(task_id, "ANALYZE_COMPLETE", "SUCCESS", result)
            return result
            
        except Exception as e:
            self.logger.log_step(task_id, "ANALYZE_COMPLETE", "ERROR", 
                               error=str(e))
            return {
                "task_id": task_id,
                "task_type": TaskType.UNKNOWN.value,
                "actions": [],
                "error": str(e)
            }
    
    def _extract_metadata(self, content: str, task_path: Path) -> Dict:
        """Extract metadata from task content"""
        metadata = {
            "filename": task_path.name,
            "source_folder": task_path.parent.name
        }
        
        # Extract bold metadata fields
        patterns = {
            "priority": r'\*\*Priority\*\*:\s*(.+?)(?:\n|$)',
            "status": r'\*\*Status\*\*:\s*(.+?)(?:\n|$)',
            "from": r'\*\*From\*\*:\s*(.+?)(?:\n|$)',
            "partner_id": r'\*\*Partner ID\*\*:\s*(\d+)',
            "amount": r'\*\*Amount\*\*:\s*[\$]?([\d,]+\.?\d*)',
            "invoice_id": r'\*\*Invoice ID\*\*:\s*(\d+)',
            "description": r'\*\*Description\*\*:\s*(.+?)(?:\n|$)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                metadata[key] = match.group(1).strip()
        
        # Extract hashtags
        tags = re.findall(r'#(\w+)', content)
        if tags:
            metadata['tags'] = tags
        
        return metadata
    
    def _detect_task_type(self, content: str, metadata: Dict) -> TaskType:
        """Detect task type from content"""
        content_lower = content.lower()
        
        scores = {}
        for task_type, keywords in self.type_keywords.items():
            score = sum(1 for kw in keywords if kw.lower() in content_lower)
            if score > 0:
                scores[task_type] = score
        
        # If email keyword found and no strong invoice indicators, prioritize email
        if 'email' in content_lower or 'send email' in content_lower:
            # Check for strong invoice indicators
            strong_invoice_indicators = ['partner id', 'invoice amount', 'bill to', 'billing address']
            has_strong_invoice = any(indicator in content_lower for indicator in strong_invoice_indicators)
            
            if not has_strong_invoice:
                # This is an email task, not invoice
                return TaskType.EMAIL_SEND
        
        if scores:
            # Return highest scoring type
            return max(scores, key=scores.get)
        
        # Check for Odoo operations
        if 'odoo' in content_lower:
            if 'invoice' in content_lower:
                return TaskType.ACCOUNTING_INVOICE
            elif 'payment' in content_lower:
                return TaskType.ACCOUNTING_PAYMENT
            elif 'expense' in content_lower:
                return TaskType.ACCOUNTING_EXPENSE
        
        return TaskType.GENERAL
    
    def _determine_actions(self, content: str, task_type: TaskType) -> List[TaskAction]:
        """Determine required actions based on task type and content"""
        actions = []
        content_lower = content.lower()
        
        # For email tasks, ONLY use email actions
        if task_type == TaskType.EMAIL_SEND:
            return [TaskAction.SEND_EMAIL, TaskAction.MOVE_TO_DONE]
        
        # Map task types to default actions for other types
        type_actions = {
            TaskType.SOCIAL_TWITTER: [TaskAction.POST_TWITTER, TaskAction.MOVE_TO_DONE],
            TaskType.SOCIAL_FACEBOOK: [TaskAction.POST_FACEBOOK, TaskAction.MOVE_TO_DONE],
            TaskType.SOCIAL_LINKEDIN: [TaskAction.POST_LINKEDIN, TaskAction.MOVE_TO_DONE],
            TaskType.ACCOUNTING_INVOICE: [TaskAction.CREATE_INVOICE, TaskAction.MOVE_TO_DONE],
            TaskType.ACCOUNTING_PAYMENT: [TaskAction.REGISTER_PAYMENT, TaskAction.MOVE_TO_DONE],
            TaskType.ACCOUNTING_EXPENSE: [TaskAction.CREATE_EXPENSE, TaskAction.MOVE_TO_DONE],
            TaskType.VAULT_MOVE: [TaskAction.MOVE_TO_DONE],
        }
        
        # Get default actions for type
        if task_type in type_actions:
            actions = type_actions[task_type].copy()
        
        # Check for explicit action requests
        for action, keywords in self.action_keywords.items():
            for kw in keywords:
                if kw.lower() in content_lower:
                    if action not in actions:
                        actions.insert(0, action)
                    break
        
        return actions
    
    def _extract_parameters(self, content: str, task_type: TaskType, 
                          metadata: Dict) -> Dict:
        """Extract parameters needed for actions"""
        params = {}
        
        # Common parameters
        if 'description' in metadata:
            params['description'] = metadata['description']
        
        # Social media parameters
        if task_type in [TaskType.SOCIAL_TWITTER, TaskType.SOCIAL_FACEBOOK, 
                        TaskType.SOCIAL_LINKEDIN]:
            # Extract post content from relevant section
            post_content = self._extract_section_content(
                content, 
                ['twitter post', 'facebook post', 'linkedin post', 'tweet', 'post']
            )
            if post_content:
                params['content'] = post_content
            elif 'description' in metadata:
                params['content'] = metadata['description']
        
        # Accounting parameters
        if task_type in [TaskType.ACCOUNTING_INVOICE, TaskType.ACCOUNTING_PAYMENT,
                        TaskType.ACCOUNTING_EXPENSE]:
            if 'partner_id' in metadata:
                try:
                    params['partner_id'] = int(metadata['partner_id'])
                except:
                    pass
            if 'amount' in metadata:
                try:
                    params['amount'] = float(metadata['amount'].replace(',', ''))
                except:
                    pass
            if 'invoice_id' in metadata:
                try:
                    params['invoice_id'] = int(metadata['invoice_id'])
                except:
                    pass
        
        # Email parameters - improved extraction
        if task_type == TaskType.EMAIL_SEND:
            # Try multiple patterns for recipient email
            email_patterns = [
                r'\*\*To\*\*:\s*(\S+@\S+)',
                r'To:\s*(\S+@\S+)',
                r'recipient_email:\s*(\S+@\S+)',
                r'\*\*Recipient\*\*:\s*(\S+@\S+)',
                r'recipient:\s*(\S+@\S+)',
            ]
            
            for pattern in email_patterns:
                email_match = re.search(pattern, content, re.IGNORECASE)
                if email_match:
                    params['to'] = email_match.group(1)
                    break
            
            # Try multiple patterns for subject
            subject_patterns = [
                r'\*\*Subject\*\*:\s*(.+?)(?:\n|$)',
                r'Subject:\s*(.+?)(?:\n|$)',
            ]
            
            for pattern in subject_patterns:
                subject_match = re.search(pattern, content, re.IGNORECASE)
                if subject_match:
                    params['subject'] = subject_match.group(1).strip().strip('"\'')
                    break
            
            # Try multiple patterns for body/message
            body_patterns = [
                r'\*\*Message\*\*:\s*(.+?)(?:\n|$)',
                r'\*\*Body\*\*:\s*(.+?)(?:\n|$)',
                r'Body:\s*(.+?)(?:\n|$)',
                r'Message:\s*(.+?)(?:\n|$)',
            ]
            
            for pattern in body_patterns:
                body_match = re.search(pattern, content, re.IGNORECASE)
                if body_match:
                    params['body'] = body_match.group(1).strip().strip('"\'')
                    break
            
            # Fallback to description
            if 'body' not in params and 'description' in metadata:
                params['body'] = metadata['description']
        
        return params
    
    def _extract_section_content(self, content: str, section_names: List[str]) -> str:
        """Extract content from a section"""
        lines = content.split('\n')
        
        in_section = False
        section_lines = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if entering a section
            for section in section_names:
                if section in line_lower and (line.startswith('##') or line.startswith('#')):
                    in_section = True
                    continue
            
            # Check if leaving section
            if in_section and line.startswith('##'):
                break
            
            # Collect lines
            if in_section and line.strip():
                section_lines.append(line.strip())
        
        return ' '.join(section_lines) if section_lines else ''
    
    def _calculate_priority(self, content: str, metadata: Dict) -> int:
        """Calculate task priority (1-5)"""
        priority = 3  # Default medium
        
        # Check explicit priority
        if 'priority' in metadata:
            priority_str = metadata['priority'].lower()
            if 'urgent' in priority_str or 'critical' in priority_str:
                priority = 5
            elif 'high' in priority_str:
                priority = 4
            elif 'low' in priority_str:
                priority = 2
        
        # Check for urgency keywords
        content_lower = content.lower()
        urgency_keywords = ['urgent', 'asap', 'immediately', 'critical', 'emergency']
        if any(kw in content_lower for kw in urgency_keywords):
            priority = max(priority, 5)
        
        return priority
