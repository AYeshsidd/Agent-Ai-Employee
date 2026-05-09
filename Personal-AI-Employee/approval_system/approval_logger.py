#!/usr/bin/env python3
"""Approval Logger - Silver Tier Part 5"""
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config


class ApprovalLogger:
    """Specialized logger for approval decisions and actions"""

    def __init__(self):
        self.approval_log = Config.LOGS_DIR / "approvals.log"
        self.approval_log.parent.mkdir(exist_ok=True)

    def log_approval_request(self, action_id: str, action_type: str, params: Dict[str, Any]):
        """Log when an approval is requested"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            "timestamp": timestamp,
            "event": "APPROVAL_REQUESTED",
            "action_id": action_id,
            "action_type": action_type,
            "parameters": params
        }
        self._write_log(log_entry)

    def log_approval_decision(self, action_id: str, decision: str, approved_by: str = "human"):
        """Log approval or rejection decision"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            "timestamp": timestamp,
            "event": "APPROVAL_DECISION",
            "action_id": action_id,
            "decision": decision,  # "approved" or "rejected"
            "approved_by": approved_by
        }
        self._write_log(log_entry)

    def log_action_execution(self, action_id: str, action_type: str, result: Dict[str, Any]):
        """Log action execution result"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            "timestamp": timestamp,
            "event": "ACTION_EXECUTED",
            "action_id": action_id,
            "action_type": action_type,
            "result": result
        }
        self._write_log(log_entry)

    def _write_log(self, log_entry: Dict[str, Any]):
        """Write log entry to file"""
        try:
            with open(self.approval_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"[ERROR] Failed to write approval log: {str(e)}")

    def get_approval_history(self, action_id: str = None) -> list:
        """Get approval history, optionally filtered by action_id"""
        if not self.approval_log.exists():
            return []

        history = []
        try:
            with open(self.approval_log, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        if action_id is None or entry.get('action_id') == action_id:
                            history.append(entry)
        except Exception as e:
            print(f"[ERROR] Failed to read approval log: {str(e)}")

        return history


if __name__ == "__main__":
    # Quick test
    logger = ApprovalLogger()
    logger.log_approval_request("test_001", "send_email", {"to": "test@example.com"})
    logger.log_approval_decision("test_001", "approved", "test_user")
    print("Approval Logger initialized and tested")
