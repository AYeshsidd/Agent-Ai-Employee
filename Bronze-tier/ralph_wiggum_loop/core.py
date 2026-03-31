#!/usr/bin/env python3
"""
Ralph Wiggum Loop - Autonomous Multi-Step Task Execution

This module provides autonomous task execution capabilities:
- Detect tasks from Inbox/Needs_Action
- Analyze task content and metadata
- Decide next steps based on task type
- Execute actions automatically via MCP tools
- Log each step with timestamp, status, errors
- Handle errors with retries and graceful degradation
"""
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json
import time
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config
from bronze_logger import BronzeLogger


class TaskType(Enum):
    """Supported task types"""
    SOCIAL_TWITTER = "social_twitter"
    SOCIAL_FACEBOOK = "social_facebook"
    SOCIAL_LINKEDIN = "social_linkedin"
    ACCOUNTING_INVOICE = "accounting_invoice"
    ACCOUNTING_PAYMENT = "accounting_payment"
    ACCOUNTING_EXPENSE = "accounting_expense"
    EMAIL_SEND = "email_send"
    VAULT_MOVE = "vault_move"
    GENERAL = "general"
    UNKNOWN = "unknown"


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    SKIPPED = "skipped"


class TaskAction(Enum):
    """Available actions"""
    POST_TWITTER = "post_twitter"
    POST_FACEBOOK = "post_facebook"
    POST_LINKEDIN = "post_linkedin"
    CREATE_INVOICE = "create_invoice"
    REGISTER_PAYMENT = "register_payment"
    CREATE_EXPENSE = "create_expense"
    SEND_EMAIL = "send_email"
    MOVE_TO_DONE = "move_to_done"
    MOVE_TO_NEEDS_ACTION = "move_to_needs_action"
    ANALYZE_AND_CATEGORIZE = "analyze_and_categorize"
    WAIT_FOR_APPROVAL = "wait_for_approval"


class RalphWiggumLogger:
    """Comprehensive logging for Ralph Wiggum Loop"""
    
    def __init__(self):
        self.logger = BronzeLogger.get_logger("RalphWiggumLoop")
        self.log_file = Config.LOGS_DIR / "ralph_wiggum_loop.jsonl"
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log_step(self, task_id: str, step_name: str, status: str, 
                 details: Dict = None, error: str = None):
        """Log a single step in task execution"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "step": step_name,
            "status": status,
            "details": details or {},
            "error": error
        }
        
        # Write to JSONL file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Also log via BronzeLogger
        if status == "ERROR":
            self.logger.error(f"[{task_id}] {step_name}: {error}")
        else:
            self.logger.info(f"[{task_id}] {step_name}: {status}")
    
    def log_task_start(self, task_id: str, task_type: str):
        """Log task execution start"""
        self.log_step(task_id, "TASK_START", "STARTED", {"task_type": task_type})
    
    def log_task_complete(self, task_id: str, success: bool, result: Dict = None):
        """Log task execution complete"""
        self.log_step(
            task_id, 
            "TASK_COMPLETE", 
            "SUCCESS" if success else "FAILED",
            result or {},
            None if success else result.get('error') if result else None
        )
    
    def get_task_history(self, task_id: str = None) -> List[Dict]:
        """Get execution history for a task"""
        history = []
        if not self.log_file.exists():
            return history
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if task_id is None or entry.get('task_id') == task_id:
                        history.append(entry)
                except:
                    continue
        
        return history


# Global logger instance
_loop_logger = RalphWiggumLogger()


def get_loop_logger() -> RalphWiggumLogger:
    """Get the global loop logger"""
    return _loop_logger
