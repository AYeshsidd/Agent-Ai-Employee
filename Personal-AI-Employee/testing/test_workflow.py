#!/usr/bin/env python3
"""Test script to demonstrate watcher functionality"""
from pathlib import Path
from datetime import datetime
from config import Config
from vault_manager import VaultManager
from watcher import DropsFolderHandler


def test_watcher_workflow():
    """Test complete workflow: Drops -> Inbox -> Needs_Action"""
    print("=" * 60)
    print("Testing Watcher Workflow")
    print("=" * 60)
    print()

    VaultManager.initialize()

    test_file = Config.DROPS / "test_task.txt"
    test_content = """Implement user profile page with avatar upload functionality.

Requirements:
- Display user information (name, email, bio)
- Allow avatar image upload
- Add form validation
- Save changes to database

Priority: High
"""

    print("Step 1: Creating test file in Drops folder...")
    test_file.write_text(test_content, encoding='utf-8')
    print(f"  Created: {test_file.name}")
    print()

    print("Step 2: Simulating watcher processing...")
    handler = DropsFolderHandler()
    handler._create_task_from_file(test_file)
    print()

    print("Step 3: Checking Inbox for created task...")
    inbox_files = list(Config.INBOX.glob("*.md"))
    if inbox_files:
        print(f"  Found {len(inbox_files)} task(s) in Inbox")
        for f in inbox_files:
            print(f"    - {f.name}")
    else:
        print("  No tasks found in Inbox")
    print()

    print("Step 4: Processing Inbox with main.py...")
    from main import process_inbox
    process_inbox()
    print()

    print("Step 5: Checking Needs_Action folder...")
    needs_action_files = list(Config.NEEDS_ACTION.glob("*.md"))
    print(f"  Total tasks in Needs_Action: {len(needs_action_files)}")
    print()

    print("=" * 60)
    print("Workflow Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_watcher_workflow()
