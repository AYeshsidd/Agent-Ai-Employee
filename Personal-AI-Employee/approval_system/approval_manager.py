#!/usr/bin/env python3
"""Approval Manager - Silver Tier Part 5"""
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import uuid
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config
from approval_system.approval_logger import ApprovalLogger
from mcp_server import get_server


class ApprovalManager:
    """Manages approval workflow for sensitive actions"""

    def __init__(self):
        self.pending_file = Config.LOGS_DIR / "pending_approvals.json"
        self.logger = ApprovalLogger()
        self.mcp_server = get_server()
        self._load_pending()

    def _load_pending(self):
        """Load pending approvals from file"""
        if self.pending_file.exists():
            try:
                with open(self.pending_file, 'r', encoding='utf-8') as f:
                    self.pending = json.load(f)
            except Exception:
                self.pending = {}
        else:
            self.pending = {}

    def _save_pending(self):
        """Save pending approvals to file"""
        try:
            self.pending_file.parent.mkdir(exist_ok=True)
            with open(self.pending_file, 'w', encoding='utf-8') as f:
                json.dump(self.pending, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save pending approvals: {str(e)}")

    def request_approval(
        self,
        action_type: str,
        parameters: Dict[str, Any],
        source: str = "manual",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Request approval for an action

        Args:
            action_type: Type of action (e.g., "send_email", "send_notification")
            parameters: Action parameters
            source: Source of the request (e.g., "manual", "plan", "automation")
            metadata: Additional metadata (e.g., plan file, task info)

        Returns:
            Action ID for tracking
        """
        action_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        approval_request = {
            "action_id": action_id,
            "action_type": action_type,
            "parameters": parameters,
            "source": source,
            "metadata": metadata or {},
            "status": "pending",
            "requested_at": timestamp
        }

        self.pending[action_id] = approval_request
        self._save_pending()

        # Log the request
        self.logger.log_approval_request(action_id, action_type, parameters)

        return action_id

    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get all pending approval requests"""
        return [
            approval for approval in self.pending.values()
            if approval.get("status") == "pending"
        ]

    def get_approval(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Get specific approval request by ID"""
        return self.pending.get(action_id)

    def approve(self, action_id: str, approved_by: str = "human") -> Dict[str, Any]:
        """
        Approve an action and execute it

        Args:
            action_id: Action ID to approve
            approved_by: Who approved the action

        Returns:
            Execution result
        """
        approval = self.pending.get(action_id)

        if not approval:
            return {
                "status": "failed",
                "message": f"Action {action_id} not found"
            }

        if approval.get("status") != "pending":
            return {
                "status": "failed",
                "message": f"Action {action_id} is not pending (status: {approval.get('status')})"
            }

        # Log approval decision
        self.logger.log_approval_decision(action_id, "approved", approved_by)

        # Execute action via MCP Server
        try:
            result = self.mcp_server.call_tool(
                approval["action_type"],
                approval["parameters"]
            )

            # Log execution
            self.logger.log_action_execution(action_id, approval["action_type"], result)

            # Update status
            approval["status"] = "approved"
            approval["approved_by"] = approved_by
            approval["approved_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            approval["execution_result"] = result

            self._save_pending()

            return result

        except Exception as e:
            error_result = {
                "status": "failed",
                "message": f"Execution error: {str(e)}"
            }

            # Log execution error
            self.logger.log_action_execution(action_id, approval["action_type"], error_result)

            # Update status
            approval["status"] = "failed"
            approval["error"] = str(e)

            self._save_pending()

            return error_result

    def reject(self, action_id: str, rejected_by: str = "human", reason: str = "") -> Dict[str, Any]:
        """
        Reject an action

        Args:
            action_id: Action ID to reject
            rejected_by: Who rejected the action
            reason: Reason for rejection

        Returns:
            Result dictionary
        """
        approval = self.pending.get(action_id)

        if not approval:
            return {
                "status": "failed",
                "message": f"Action {action_id} not found"
            }

        if approval.get("status") != "pending":
            return {
                "status": "failed",
                "message": f"Action {action_id} is not pending (status: {approval.get('status')})"
            }

        # Log rejection decision
        self.logger.log_approval_decision(action_id, "rejected", rejected_by)

        # Update status
        approval["status"] = "rejected"
        approval["rejected_by"] = rejected_by
        approval["rejected_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        approval["rejection_reason"] = reason

        self._save_pending()

        return {
            "status": "success",
            "message": f"Action {action_id} rejected"
        }

    def clear_completed(self):
        """Remove approved/rejected actions from pending list"""
        self.pending = {
            action_id: approval
            for action_id, approval in self.pending.items()
            if approval.get("status") == "pending"
        }
        self._save_pending()

    def get_statistics(self) -> Dict[str, int]:
        """Get approval statistics"""
        stats = {
            "pending": 0,
            "approved": 0,
            "rejected": 0,
            "failed": 0,
            "total": len(self.pending)
        }

        for approval in self.pending.values():
            status = approval.get("status", "unknown")
            if status in stats:
                stats[status] += 1

        return stats


if __name__ == "__main__":
    # Quick test
    manager = ApprovalManager()
    print("Approval Manager initialized")
    print(f"Pending approvals: {len(manager.get_pending_approvals())}")
