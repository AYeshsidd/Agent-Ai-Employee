#!/usr/bin/env python3
"""Test Approval System - Silver Tier Part 5"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from approval_system import ApprovalManager, ApprovalDashboard
import time


def test_approval_workflow():
    """Test complete approval workflow"""
    print("\n" + "=" * 70)
    print("  APPROVAL SYSTEM - COMPREHENSIVE TEST")
    print("=" * 70)

    manager = ApprovalManager()
    dashboard = ApprovalDashboard()

    # Test 1: Request approval for notification
    print("\n[TEST 1] Request approval for notification...")
    action_id_1 = manager.request_approval(
        action_type="send_notification",
        parameters={
            "title": "Test Notification",
            "message": "This is a test notification requiring approval"
        },
        source="test_script",
        metadata={"test_id": "001"}
    )
    print(f"[OK] Approval requested: {action_id_1}")

    # Test 2: Request approval for email
    print("\n[TEST 2] Request approval for email...")
    action_id_2 = manager.request_approval(
        action_type="send_email",
        parameters={
            "to": "test@example.com",
            "subject": "Test Email Requiring Approval",
            "body": "This email requires human approval before sending"
        },
        source="test_script",
        metadata={"test_id": "002", "priority": "high"}
    )
    print(f"[OK] Approval requested: {action_id_2}")

    # Test 3: Display pending approvals
    print("\n[TEST 3] Display pending approvals...")
    dashboard.display_pending_approvals()

    # Test 4: Review specific approval
    print("\n[TEST 4] Review specific approval...")
    dashboard.review_approval(action_id_1)

    # Test 5: Approve notification
    print("\n[TEST 5] Approve notification action...")
    result = manager.approve(action_id_1, approved_by="test_user")
    if result.get("status") == "success":
        print("[PASS] Notification approved and executed")
    else:
        print(f"[FAIL] Approval failed: {result.get('message')}")

    # Test 6: Reject email
    print("\n[TEST 6] Reject email action...")
    result = manager.reject(action_id_2, rejected_by="test_user", reason="Test rejection")
    if result.get("status") == "success":
        print("[PASS] Email rejected successfully")
    else:
        print(f"[FAIL] Rejection failed: {result.get('message')}")

    # Test 7: Show statistics
    print("\n[TEST 7] Show statistics...")
    dashboard.show_statistics()

    # Test 8: Request another approval
    print("\n[TEST 8] Request another approval (will remain pending)...")
    action_id_3 = manager.request_approval(
        action_type="send_notification",
        parameters={
            "title": "Pending Notification",
            "message": "This will remain pending for manual review"
        },
        source="test_script"
    )
    print(f"[OK] Approval requested: {action_id_3}")

    # Test 9: Get approval history
    print("\n[TEST 9] Get approval history...")
    history = manager.logger.get_approval_history()
    print(f"[INFO] Found {len(history)} log entries")
    if history:
        print(f"[INFO] Latest entry: {history[-1]['event']}")

    # Test 10: Test error handling
    print("\n[TEST 10] Test error handling (invalid action ID)...")
    result = manager.approve("invalid_id")
    if result.get("status") == "failed":
        print("[PASS] Invalid action ID handled correctly")
    else:
        print("[FAIL] Should have failed with invalid ID")

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    stats = manager.get_statistics()
    print(f"\nTotal actions: {stats['total']}")
    print(f"Pending: {stats['pending']}")
    print(f"Approved: {stats['approved']}")
    print(f"Rejected: {stats['rejected']}")

    print("\n[INFO] Check logs/approvals.log for detailed approval logs")
    print("[INFO] Check logs/pending_approvals.json for pending actions")
    print("\n" + "=" * 70)


def test_plan_integration():
    """Test integration with Plan.md files"""
    print("\n" + "=" * 70)
    print("  PLAN INTEGRATION TEST")
    print("=" * 70)

    manager = ApprovalManager()

    # Simulate requesting approval from a plan
    print("\n[INFO] Simulating approval request from Plan.md...")
    action_id = manager.request_approval(
        action_type="send_email",
        parameters={
            "to": "client@example.com",
            "subject": "Task Completion Update",
            "body": "Your requested task has been completed successfully."
        },
        source="plan",
        metadata={
            "plan_file": "Implement_User_Authentication_Feature_PLAN.md",
            "task_file": "Implement_User_Authentication_Feature.md",
            "action_item": "Send completion email to client"
        }
    )

    print(f"[OK] Approval requested from plan: {action_id}")
    print("[INFO] This action is now pending human approval")
    print("[INFO] Run 'python approval_system/approval_dashboard.py' to review")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\nSelect test mode:")
    print("1. Full workflow test")
    print("2. Plan integration test")
    print("3. Both")

    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        test_approval_workflow()
    elif choice == "2":
        test_plan_integration()
    elif choice == "3":
        test_approval_workflow()
        test_plan_integration()
    else:
        print("[ERROR] Invalid choice")
