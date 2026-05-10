#!/usr/bin/env python3
"""Approval Dashboard - Silver Tier Part 5"""
from pathlib import Path
import sys
import json

# Ensure project root is in sys.path
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from approval_system.approval_manager import ApprovalManager


class ApprovalDashboard:
    """Interactive CLI dashboard for reviewing and approving actions"""

    def __init__(self):
        self.manager = ApprovalManager()

    def display_pending_approvals(self):
        """Display all pending approvals"""
        pending = self.manager.get_pending_approvals()

        if not pending:
            print("\n[INFO] No pending approvals")
            return False

        print("\n" + "=" * 70)
        print("  PENDING APPROVALS")
        print("=" * 70)

        for i, approval in enumerate(pending, 1):
            print(f"\n[{i}] Action ID: {approval['action_id']}")
            print(f"    Type: {approval['action_type']}")
            print(f"    Source: {approval['source']}")
            print(f"    Requested: {approval['requested_at']}")

            # Display parameters
            print(f"    Parameters:")
            for key, value in approval['parameters'].items():
                # Truncate long values
                value_str = str(value)
                if len(value_str) > 60:
                    value_str = value_str[:57] + "..."
                print(f"      - {key}: {value_str}")

            # Display metadata if present
            if approval.get('metadata'):
                print(f"    Metadata:")
                for key, value in approval['metadata'].items():
                    print(f"      - {key}: {value}")

        print("\n" + "=" * 70)
        return True

    def review_approval(self, action_id: str):
        """Review a specific approval in detail"""
        approval = self.manager.get_approval(action_id)

        if not approval:
            print(f"\n[ERROR] Action {action_id} not found")
            return

        print("\n" + "=" * 70)
        print("  APPROVAL DETAILS")
        print("=" * 70)

        print(f"\nAction ID: {approval['action_id']}")
        print(f"Type: {approval['action_type']}")
        print(f"Status: {approval['status']}")
        print(f"Source: {approval['source']}")
        print(f"Requested: {approval['requested_at']}")

        print(f"\nParameters:")
        print(json.dumps(approval['parameters'], indent=2))

        if approval.get('metadata'):
            print(f"\nMetadata:")
            print(json.dumps(approval['metadata'], indent=2))

        print("\n" + "=" * 70)

    def approve_action(self, action_id: str):
        """Approve and execute an action"""
        print(f"\n[INFO] Approving action {action_id}...")
        result = self.manager.approve(action_id)

        if result.get("status") == "success":
            print(f"[SUCCESS] Action approved and executed successfully")
            print(f"[RESULT] {result.get('message')}")
        else:
            print(f"[FAILED] Action execution failed")
            print(f"[ERROR] {result.get('message')}")

        return result

    def reject_action(self, action_id: str, reason: str = ""):
        """Reject an action"""
        print(f"\n[INFO] Rejecting action {action_id}...")
        result = self.manager.reject(action_id, reason=reason)

        if result.get("status") == "success":
            print(f"[SUCCESS] Action rejected")
        else:
            print(f"[FAILED] Rejection failed")
            print(f"[ERROR] {result.get('message')}")

        return result

    def show_statistics(self):
        """Display approval statistics"""
        stats = self.manager.get_statistics()

        print("\n" + "=" * 70)
        print("  APPROVAL STATISTICS")
        print("=" * 70)
        print(f"\nTotal Actions: {stats['total']}")
        print(f"Pending: {stats['pending']}")
        print(f"Approved: {stats['approved']}")
        print(f"Rejected: {stats['rejected']}")
        print(f"Failed: {stats['failed']}")
        print("\n" + "=" * 70)

    def interactive_mode(self):
        """Run interactive approval dashboard"""
        print("\n" + "=" * 70)
        print("  APPROVAL DASHBOARD - INTERACTIVE MODE")
        print("=" * 70)

        while True:
            print("\nOptions:")
            print("1. View pending approvals")
            print("2. Review specific action")
            print("3. Approve action")
            print("4. Reject action")
            print("5. Show statistics")
            print("6. Clear completed actions")
            print("7. Exit")

            choice = input("\nEnter choice (1-7): ").strip()

            if choice == "1":
                self.display_pending_approvals()

            elif choice == "2":
                action_id = input("Enter action ID: ").strip()
                self.review_approval(action_id)

            elif choice == "3":
                if not self.display_pending_approvals():
                    continue
                action_id = input("\nEnter action ID to approve: ").strip()

                # Show details and confirm
                self.review_approval(action_id)
                confirm = input("\nConfirm approval? (yes/no): ").strip().lower()

                if confirm in ['yes', 'y']:
                    self.approve_action(action_id)
                else:
                    print("[CANCELLED] Approval cancelled")

            elif choice == "4":
                if not self.display_pending_approvals():
                    continue
                action_id = input("\nEnter action ID to reject: ").strip()
                reason = input("Enter rejection reason (optional): ").strip()

                # Show details and confirm
                self.review_approval(action_id)
                confirm = input("\nConfirm rejection? (yes/no): ").strip().lower()

                if confirm in ['yes', 'y']:
                    self.reject_action(action_id, reason)
                else:
                    print("[CANCELLED] Rejection cancelled")

            elif choice == "5":
                self.show_statistics()

            elif choice == "6":
                self.manager.clear_completed()
                print("\n[SUCCESS] Completed actions cleared")

            elif choice == "7":
                print("\n[INFO] Exiting approval dashboard")
                break

            else:
                print("\n[ERROR] Invalid choice")

    def batch_approve_mode(self):
        """Review and approve/reject all pending actions one by one"""
        print("\n" + "=" * 70)
        print("  BATCH APPROVAL MODE")
        print("=" * 70)

        pending = self.manager.get_pending_approvals()

        if not pending:
            print("\n[INFO] No pending approvals")
            return

        print(f"\n[INFO] Found {len(pending)} pending approval(s)")

        for i, approval in enumerate(pending, 1):
            print(f"\n[{i}/{len(pending)}] Reviewing action...")
            self.review_approval(approval['action_id'])

            while True:
                decision = input("\nDecision (approve/reject/skip): ").strip().lower()

                if decision in ['approve', 'a']:
                    self.approve_action(approval['action_id'])
                    break
                elif decision in ['reject', 'r']:
                    reason = input("Rejection reason (optional): ").strip()
                    self.reject_action(approval['action_id'], reason)
                    break
                elif decision in ['skip', 's']:
                    print("[INFO] Skipped")
                    break
                else:
                    print("[ERROR] Invalid decision. Use: approve/reject/skip")

        print("\n[INFO] Batch approval completed")


if __name__ == "__main__":
    dashboard = ApprovalDashboard()

    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "batch":
            dashboard.batch_approve_mode()
        elif sys.argv[1] == "list":
            dashboard.display_pending_approvals()
        elif sys.argv[1] == "stats":
            dashboard.show_statistics()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Usage: python approval_dashboard.py [batch|list|stats]")
    else:
        dashboard.interactive_mode()
