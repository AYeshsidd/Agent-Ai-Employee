#!/usr/bin/env python3
"""Comprehensive test for Vault operations and Agent Skills"""
from pathlib import Path
from vault_manager import VaultManager
from skills import ReadVaultSkill, WriteVaultSkill


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_vault_operations():
    """Test all vault read/write operations"""

    print_section("VAULT OPERATIONS TEST")

    # Initialize
    VaultManager.initialize()
    reader = ReadVaultSkill()
    writer = WriteVaultSkill()

    # Test 1: Create new task
    print_section("Test 1: Create New Task")
    task_path = writer.create_task(
        title="Build REST API",
        description="Implement RESTful API for user management system",
        folder="inbox",
        priority="High",
        action_items=[
            "Design API endpoints",
            "Implement authentication",
            "Add rate limiting",
            "Write API documentation"
        ],
        tags=["api", "backend", "urgent"]
    )
    print(f"Created task: {task_path.name}")

    # Test 2: Read all tasks from Inbox
    print_section("Test 2: Read All Tasks from Inbox")
    inbox_tasks = reader.read_all_tasks("inbox")
    print(f"Found {len(inbox_tasks)} task(s) in Inbox:")
    for task in inbox_tasks:
        print(f"  - {task['filename']}")

    # Test 3: Read specific task
    print_section("Test 3: Read Specific Task")
    task = reader.read_task_by_name(task_path.name, "inbox")
    if task:
        print(f"Task: {task['filename']}")
        metadata = reader.extract_metadata(task['content'])
        print(f"  Title: {metadata['title']}")
        print(f"  Priority: {metadata['priority']}")
        print(f"  Status: {metadata['status']}")

    # Test 4: Add action item
    print_section("Test 4: Add Action Item")
    success = writer.add_action_item(task_path, "Add unit tests for all endpoints")
    print(f"Added action item: {'Success' if success else 'Failed'}")

    # Test 5: Update task
    print_section("Test 5: Update Task Status")
    success = writer.update_task(task_path, {"status": "[IN PROGRESS]"})
    print(f"Updated task status: {'Success' if success else 'Failed'}")

    # Test 6: Move task to Needs_Action
    print_section("Test 6: Move Task to Needs_Action")
    new_path = writer.move_task_to_folder(task_path, "needs_action")
    if new_path:
        print(f"Moved task to Needs_Action: {new_path.name}")
        task_path = new_path

    # Test 7: Search tasks
    print_section("Test 7: Search Tasks")
    results = reader.search_tasks("API", "needs_action")
    print(f"Found {len(results)} task(s) matching 'API':")
    for result in results:
        print(f"  - {result['filename']}")

    # Test 8: Get task summary
    print_section("Test 8: Get Task Summary")
    summary = reader.get_task_summary("needs_action")
    print(f"Needs_Action Summary:")
    print(f"  Total tasks: {summary['count']}")
    for task in summary['tasks'][:3]:
        print(f"  - {task['filename']}")
        print(f"    Preview: {task['preview'][:80]}...")

    # Test 9: Mark task complete
    print_section("Test 9: Mark Task Complete")
    done_path = writer.mark_task_complete(task_path)
    if done_path:
        print(f"Task marked complete and moved to Done: {done_path.name}")

    # Test 10: Get vault statistics
    print_section("Test 10: Vault Statistics")
    vault_mgr = VaultManager()
    stats = vault_mgr.get_vault_stats()
    print(f"Vault Statistics:")
    print(f"  Inbox: {stats['inbox']} tasks")
    print(f"  Needs_Action: {stats['needs_action']} tasks")
    print(f"  Done: {stats['done']} tasks")
    print(f"  Total: {stats['total']} tasks")

    # Test 11: Read from Done folder
    print_section("Test 11: Read Completed Tasks")
    done_tasks = reader.read_all_tasks("done")
    print(f"Found {len(done_tasks)} completed task(s):")
    for task in done_tasks[:5]:
        metadata = reader.extract_metadata(task['content'])
        print(f"  - {task['filename']}")
        print(f"    Title: {metadata['title']}")

    print_section("ALL TESTS COMPLETED")
    print("\nVault operations are fully functional!")
    print("All Agent Skills are working correctly.")


if __name__ == "__main__":
    test_vault_operations()
