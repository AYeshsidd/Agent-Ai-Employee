#!/usr/bin/env python3
"""Plan to Approval Integration - Bridge between Plan Generator and Approval System"""
import sys
from pathlib import Path
import re

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from vault_manager import VaultManager
from approval_system import ApprovalManager


class PlanApprovalIntegration:
    """Reads plans and creates approval requests for actions requiring approval"""

    def __init__(self):
        self.vault = VaultManager()
        self.approval_manager = ApprovalManager()

    def parse_plan_for_actions(self, plan_path: Path) -> list:
        """
        Parse a plan file and extract actions that require approval

        Returns:
            List of action dictionaries with type, parameters, and metadata
        """
        if not plan_path.exists():
            return []

        content = plan_path.read_text(encoding='utf-8')
        actions = []

        # Extract task title
        title_match = re.search(r'^# Plan for: (.+)$', content, re.MULTILINE)
        task_title = title_match.group(1) if title_match else "Unknown Task"

        # Extract source
        source_match = re.search(r'^## Source\n(.+)$', content, re.MULTILINE)
        source = source_match.group(1).strip() if source_match else "Unknown"

        # Look for email-related action items
        email_pattern = r'- \[ \] .*(?:send|email|notify|contact).*email.*'
        email_matches = re.findall(email_pattern, content, re.IGNORECASE)

        for match in email_matches:
            # Extract email details from action item
            action_text = match.replace('- [ ]', '').strip()

            # Try to extract recipient - look for any email address in the text
            recipient_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', action_text)
            recipient = recipient_match.group(1) if recipient_match else None

            if recipient:
                actions.append({
                    'type': 'send_email',
                    'parameters': {
                        'to': recipient,
                        'subject': f"Regarding: {task_title}",
                        'body': f"Action from plan: {action_text}\n\nThis email requires your review and approval."
                    },
                    'metadata': {
                        'plan_file': plan_path.name,
                        'task_file': plan_path.stem.replace('_PLAN', '') + '.md',
                        'action_item': action_text,
                        'source': source
                    }
                })

        # Look for notification-related action items
        notif_pattern = r'- \[ \] .*(?:notify|alert|send notification|inform).*'
        notif_matches = re.findall(notif_pattern, content, re.IGNORECASE)

        for match in notif_matches:
            if 'email' not in match.lower():  # Skip if it's an email action
                action_text = match.replace('- [ ]', '').strip()

                actions.append({
                    'type': 'send_notification',
                    'parameters': {
                        'title': f"Action Required: {task_title}",
                        'message': action_text
                    },
                    'metadata': {
                        'plan_file': plan_path.name,
                        'task_file': plan_path.stem.replace('_PLAN', '') + '.md',
                        'action_item': action_text,
                        'source': source
                    }
                })

        return actions

    def request_approvals_for_plan(self, plan_path: Path) -> list:
        """
        Request approvals for all actions in a plan

        Returns:
            List of action IDs
        """
        actions = self.parse_plan_for_actions(plan_path)

        if not actions:
            print(f"[INFO] No actions requiring approval found in {plan_path.name}")
            return []

        action_ids = []

        print(f"\n[INFO] Found {len(actions)} action(s) requiring approval in {plan_path.name}")

        for i, action in enumerate(actions, 1):
            print(f"\n[{i}] Requesting approval for: {action['metadata']['action_item'][:60]}...")

            action_id = self.approval_manager.request_approval(
                action_type=action['type'],
                parameters=action['parameters'],
                source='plan',
                metadata=action['metadata']
            )

            action_ids.append(action_id)
            print(f"    Action ID: {action_id}")

        return action_ids

    def process_inbox_plans(self) -> dict:
        """
        Process all plan files in Inbox and request approvals

        Returns:
            Dictionary with statistics
        """
        inbox_path = self.vault.vault_root / "Inbox"

        if not inbox_path.exists():
            return {'plans_processed': 0, 'approvals_requested': 0}

        # Find all plan files
        plan_files = list(inbox_path.glob("*_PLAN.md"))

        if not plan_files:
            print("[INFO] No plan files found in Inbox")
            return {'plans_processed': 0, 'approvals_requested': 0}

        print(f"\n[INFO] Found {len(plan_files)} plan file(s) in Inbox")

        total_approvals = 0

        for plan_file in plan_files:
            print(f"\n{'=' * 70}")
            print(f"Processing: {plan_file.name}")
            print('=' * 70)

            action_ids = self.request_approvals_for_plan(plan_file)
            total_approvals += len(action_ids)

        return {
            'plans_processed': len(plan_files),
            'approvals_requested': total_approvals
        }

    def process_specific_plan(self, plan_name: str) -> list:
        """
        Process a specific plan file by name

        Args:
            plan_name: Name of the plan file (with or without .md extension)

        Returns:
            List of action IDs
        """
        if not plan_name.endswith('.md'):
            plan_name += '.md'

        inbox_path = self.vault.vault_root / "Inbox"
        plan_path = inbox_path / plan_name

        if not plan_path.exists():
            print(f"[ERROR] Plan file not found: {plan_path}")
            return []

        print(f"\n{'=' * 70}")
        print(f"Processing: {plan_name}")
        print('=' * 70)

        return self.request_approvals_for_plan(plan_path)


def main():
    print("\n" + "=" * 70)
    print("  PLAN TO APPROVAL INTEGRATION")
    print("=" * 70)

    integration = PlanApprovalIntegration()

    print("\nOptions:")
    print("1. Process all plans in Inbox")
    print("2. Process specific plan")
    print("3. Process Bitcoin email plan")

    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        stats = integration.process_inbox_plans()
        print("\n" + "=" * 70)
        print("  SUMMARY")
        print("=" * 70)
        print(f"Plans processed: {stats['plans_processed']}")
        print(f"Approvals requested: {stats['approvals_requested']}")

    elif choice == "2":
        plan_name = input("\nEnter plan filename (e.g., Task_PLAN.md): ").strip()
        action_ids = integration.process_specific_plan(plan_name)
        print(f"\n[RESULT] Requested {len(action_ids)} approval(s)")

    elif choice == "3":
        # Specifically for Bitcoin email plan
        action_ids = integration.process_specific_plan("Bitcoin_email_task_PLAN.md")
        print(f"\n[RESULT] Requested {len(action_ids)} approval(s)")

        if action_ids:
            print("\n[NEXT STEP] Review approvals:")
            print("  python run_approval_dashboard.py list")

    else:
        print("[ERROR] Invalid choice")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
