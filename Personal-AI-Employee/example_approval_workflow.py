#!/usr/bin/env python3
"""Practical Example - Approval System with Email Sending"""
import sys
from pathlib import Path

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from approval_system import ApprovalManager


def example_email_workflow():
    """
    Practical example: Request approval to send an email,
    then use the dashboard to approve it
    """
    print("\n" + "=" * 70)
    print("  PRACTICAL EXAMPLE: EMAIL APPROVAL WORKFLOW")
    print("=" * 70)

    manager = ApprovalManager()

    # Scenario: You want to send an email but need approval first
    print("\n[SCENARIO] You need to send an important email to a client")
    print("[INFO] This email requires human approval before sending")

    # Get email details from user
    if len(sys.argv) < 2:
        print("\n[ERROR] Usage: python example_approval_workflow.py <recipient_email>")
        print("[EXAMPLE] python example_approval_workflow.py client@example.com")
        return

    recipient = sys.argv[2]

    # Request approval
    print(f"\n[STEP 1] Requesting approval to send email to {recipient}...")

    action_id = manager.request_approval(
        action_type="send_email",
        parameters={
            "to": recipient,
            "subject": "Project Status Update",
            "body": """Dear Client,

I hope this email finds you well.

I wanted to provide you with an update on the project status:

1. Phase 1 (Requirements Analysis) - Completed ✓
2. Phase 2 (Design) - In Progress (80% complete)
3. Phase 3 (Implementation) - Scheduled to start next week

We are on track to meet the deadline. I will send another update next week.

Please let me know if you have any questions or concerns.

Best regards,
Autonomous FTE System
"""
        },
        source="manual",
        metadata={
            "priority": "high",
            "category": "client_communication",
            "requires_review": True
        }
    )

    print(f"[SUCCESS] Approval requested: {action_id}")
    print(f"[INFO] Action ID: {action_id}")

    # Show what to do next
    print("\n" + "=" * 70)
    print("  NEXT STEPS")
    print("=" * 70)
    print("\n1. Review the pending approval:")
    print(f"   python run_approval_dashboard.py list")
    print("\n2. Open the approval dashboard:")
    print(f"   python run_approval_dashboard.py")
    print("\n3. In the dashboard:")
    print(f"   - Select option 3 (Approve action)")
    print(f"   - Enter action ID: {action_id}")
    print(f"   - Review details and confirm")
    print("\n4. The email will be sent automatically after approval")

    print("\n[INFO] Approval request saved to: logs/pending_approvals.json")
    print("[INFO] Approval logs saved to: logs/approvals.log")

    print("\n" + "=" * 70)


def example_notification_workflow():
    """
    Practical example: Request approval for multiple notifications
    """
    print("\n" + "=" * 70)
    print("  PRACTICAL EXAMPLE: BATCH NOTIFICATION APPROVAL")
    print("=" * 70)

    manager = ApprovalManager()

    # Scenario: Multiple notifications need approval
    print("\n[SCENARIO] You have 3 notifications that need approval")

    notifications = [
        {
            "title": "Daily Report Generated",
            "message": "The daily report has been generated and is ready for review."
        },
        {
            "title": "Backup Completed",
            "message": "System backup completed successfully at 2026-02-26 01:00:00"
        },
        {
            "title": "Task Reminder",
            "message": "You have 5 tasks pending in Vault/Needs_Action"
        }
    ]

    action_ids = []

    for i, notif in enumerate(notifications, 1):
        print(f"\n[STEP {i}] Requesting approval for: {notif['title']}")
        action_id = manager.request_approval(
            action_type="send_notification",
            parameters=notif,
            source="automation",
            metadata={"batch_id": "daily_notifications"}
        )
        action_ids.append(action_id)
        print(f"[OK] Action ID: {action_id}")

    print(f"\n[SUCCESS] Requested {len(action_ids)} approvals")

    # Show what to do next
    print("\n" + "=" * 70)
    print("  NEXT STEPS")
    print("=" * 70)
    print("\n1. Review all pending approvals in batch mode:")
    print(f"   python run_approval_dashboard.py batch")
    print("\n2. For each notification, you can:")
    print(f"   - Type 'approve' or 'a' to approve and execute")
    print(f"   - Type 'reject' or 'r' to reject")
    print(f"   - Type 'skip' or 's' to skip for now")

    print("\n" + "=" * 70)


def example_plan_integration():
    """
    Practical example: Request approval from a plan
    """
    print("\n" + "=" * 70)
    print("  PRACTICAL EXAMPLE: PLAN-BASED APPROVAL")
    print("=" * 70)

    manager = ApprovalManager()

    # Scenario: A plan has action items that need approval
    print("\n[SCENARIO] Plan has action items requiring approval")
    print("[INFO] Plan: Implement_User_Authentication_Feature_PLAN.md")

    # Simulate action items from plan
    action_items = [
        {
            "action_type": "send_email",
            "parameters": {
                "to": "team@company.com",
                "subject": "Authentication Feature - Ready for Review",
                "body": "The user authentication feature is complete and ready for code review."
            },
            "action_item": "Notify team when feature is complete"
        },
        {
            "action_type": "send_notification",
            "parameters": {
                "title": "Feature Complete",
                "message": "User authentication feature implementation completed"
            },
            "action_item": "Send completion notification"
        }
    ]

    action_ids = []

    for i, item in enumerate(action_items, 1):
        print(f"\n[STEP {i}] Requesting approval for: {item['action_item']}")
        action_id = manager.request_approval(
            action_type=item["action_type"],
            parameters=item["parameters"],
            source="plan",
            metadata={
                "plan_file": "Implement_User_Authentication_Feature_PLAN.md",
                "task_file": "Implement_User_Authentication_Feature.md",
                "action_item": item["action_item"]
            }
        )
        action_ids.append(action_id)
        print(f"[OK] Action ID: {action_id}")

    print(f"\n[SUCCESS] Requested {len(action_ids)} approvals from plan")

    # Show what to do next
    print("\n" + "=" * 70)
    print("  NEXT STEPS")
    print("=" * 70)
    print("\n1. Review approvals with plan context:")
    print(f"   python run_approval_dashboard.py list")
    print("\n2. Notice the metadata shows:")
    print(f"   - Which plan file triggered the request")
    print(f"   - Which action item from the plan")
    print(f"   - Related task file")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\nSelect example:")
    print("1. Email approval workflow")
    print("2. Batch notification approval")
    print("3. Plan-based approval")

    if len(sys.argv) > 1 and sys.argv[1] in ["1", "2", "3"]:
        choice = sys.argv[1]
    else:
        print("\n[INFO] Usage:")
        print("  python example_approval_workflow.py 1 <email>  # Email workflow")
        print("  python example_approval_workflow.py 2          # Batch notifications")
        print("  python example_approval_workflow.py 3          # Plan integration")
        sys.exit(0)

    if choice == "1":
        example_email_workflow()
    elif choice == "2":
        example_notification_workflow()
    elif choice == "3":
        example_plan_integration()
