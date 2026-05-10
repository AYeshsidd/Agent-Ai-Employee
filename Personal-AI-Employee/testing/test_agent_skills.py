#!/usr/bin/env python3
"""Test Part 3: Agent Skills Verification"""
import sys
from pathlib import Path

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from vault_manager import VaultManager
from skills import ReadVaultSkill, WriteVaultSkill, TaskAnalyzerSkill, VaultWriterSkill


def test_step(step_num, description):
    """Print test step header"""
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {description}")
    print('='*60)


def print_result(test_name, passed, details=""):
    """Print test result"""
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {test_name}")
    if details:
        print(f"      {details}")


def main():
    print("\n" + "="*60)
    print("  PART 3: AGENT SKILLS VERIFICATION TEST")
    print("="*60)

    # Initialize
    VaultManager.initialize()

    # Step 1: Read tasks from Inbox using ReadVaultSkill
    test_step(1, "Read tasks from Vault/Inbox using ReadVaultSkill")
    try:
        reader = ReadVaultSkill()
        inbox_tasks = reader.read_all_tasks("inbox")

        passed = isinstance(inbox_tasks, list)
        print_result("ReadVaultSkill initialized", passed)
        print_result("Read tasks from Inbox", passed, f"Found {len(inbox_tasks)} task(s)")

        if inbox_tasks:
            print(f"\nInbox tasks:")
            for task in inbox_tasks:
                print(f"  - {task['filename']}")

        step1_pass = passed
    except Exception as e:
        print_result("ReadVaultSkill", False, str(e))
        step1_pass = False

    # Step 2: Create new test task using WriteVaultSkill
    test_step(2, "Create new test task using WriteVaultSkill")
    try:
        writer = WriteVaultSkill()
        test_task_path = writer.create_task(
            title="Test Task for Agent Skills Verification",
            description="This is a test task created to verify WriteVaultSkill functionality. It should be analyzed and moved to Needs_Action.",
            folder="inbox",
            priority="Medium",
            action_items=[
                "Verify task creation",
                "Test task analysis",
                "Confirm task movement"
            ],
            tags=["test", "verification", "agent-skills"]
        )

        passed = test_task_path is not None and test_task_path.exists()
        print_result("WriteVaultSkill initialized", passed)
        print_result("Created test task", passed, f"File: {test_task_path.name if test_task_path else 'None'}")

        step2_pass = passed
        step2_task_path = test_task_path
    except Exception as e:
        print_result("WriteVaultSkill", False, str(e))
        step2_pass = False
        step2_task_path = None

    # Step 3: Analyze task with TaskAnalyzerSkill
    test_step(3, "Analyze task with TaskAnalyzerSkill")
    try:
        if step2_pass and step2_task_path:
            analyzer = TaskAnalyzerSkill()
            task_content = step2_task_path.read_text(encoding='utf-8')

            task_data = analyzer.analyze(task_content, step2_task_path)

            passed = isinstance(task_data, dict)
            print_result("TaskAnalyzerSkill initialized", passed)
            print_result("Analyzed task", passed)

            if passed:
                print(f"\nAnalysis results:")
                print(f"  Title: {task_data.get('title', 'N/A')}")
                print(f"  Priority: {task_data.get('priority', 'N/A')}/5")
                print(f"  Complexity: {task_data.get('complexity', 'N/A')}")
                print(f"  Action Items: {len(task_data.get('action_items', []))}")
                print(f"  Tags: {', '.join(task_data.get('tags', []))}")

            step3_pass = passed
            step3_task_data = task_data
        else:
            print_result("TaskAnalyzerSkill", False, "Skipped - Step 2 failed")
            step3_pass = False
            step3_task_data = None
    except Exception as e:
        print_result("TaskAnalyzerSkill", False, str(e))
        step3_pass = False
        step3_task_data = None

    # Step 4: Write analyzed task to Needs_Action using VaultWriterSkill
    test_step(4, "Write analyzed task to Vault/Needs_Action using VaultWriterSkill")
    try:
        if step3_pass and step3_task_data:
            vault_writer = VaultWriterSkill()
            output_path = vault_writer.write_to_needs_action(step3_task_data)

            passed = output_path is not None and output_path.exists()
            print_result("VaultWriterSkill initialized", passed)
            print_result("Wrote to Needs_Action", passed, f"File: {output_path.name if output_path else 'None'}")

            step4_pass = passed
            step4_output_path = output_path
        else:
            print_result("VaultWriterSkill", False, "Skipped - Step 3 failed")
            step4_pass = False
            step4_output_path = None
    except Exception as e:
        print_result("VaultWriterSkill", False, str(e))
        step4_pass = False
        step4_output_path = None

    # Step 5: Verify folder structure and task placement
    test_step(5, "Verify folder structure and task placement")
    try:
        from config import Config

        folders_exist = all([
            Config.DROPS.exists(),
            Config.INBOX.exists(),
            Config.NEEDS_ACTION.exists(),
            Config.DONE.exists()
        ])
        print_result("Vault folder structure intact", folders_exist)

        if step4_pass and step4_output_path:
            task_in_needs_action = step4_output_path.exists()
            print_result("Task in Needs_Action", task_in_needs_action, f"Path: {step4_output_path}")

            # Verify task content
            if task_in_needs_action:
                content = step4_output_path.read_text(encoding='utf-8')
                has_title = "# Test Task for Agent Skills Verification" in content
                has_status = "**Status**:" in content
                has_priority = "**Priority**:" in content
                has_actions = "## Action Items" in content

                print_result("Task has title", has_title)
                print_result("Task has status", has_status)
                print_result("Task has priority", has_priority)
                print_result("Task has action items", has_actions)

                step5_pass = all([folders_exist, task_in_needs_action, has_title, has_status, has_priority, has_actions])
            else:
                step5_pass = False
        else:
            print_result("Task verification", False, "Skipped - Step 4 failed")
            step5_pass = False
    except Exception as e:
        print_result("Folder structure verification", False, str(e))
        step5_pass = False

    # Step 6: Clean up test task
    test_step(6, "Clean up test task")
    try:
        cleanup_success = True

        # Remove from Inbox if still there
        if step2_pass and step2_task_path and step2_task_path.exists():
            step2_task_path.unlink()
            print(f"  Removed test task from Inbox: {step2_task_path.name}")

        # Remove from Needs_Action
        if step4_pass and step4_output_path and step4_output_path.exists():
            step4_output_path.unlink()
            print(f"  Removed test task from Needs_Action: {step4_output_path.name}")

        print_result("Cleanup completed", cleanup_success)
    except Exception as e:
        print_result("Cleanup", False, str(e))

    # Final Summary
    print("\n" + "="*60)
    print("  FINAL RESULTS")
    print("="*60)

    all_steps = [
        ("Step 1: ReadVaultSkill", step1_pass),
        ("Step 2: WriteVaultSkill", step2_pass),
        ("Step 3: TaskAnalyzerSkill", step3_pass),
        ("Step 4: VaultWriterSkill", step4_pass),
        ("Step 5: Verification", step5_pass)
    ]

    for step_name, passed in all_steps:
        print_result(step_name, passed)

    all_passed = all(passed for _, passed in all_steps)

    print("\n" + "="*60)
    if all_passed:
        print("  ✓ ALL TESTS PASSED")
        print("  Agent Skills are fully functional!")
    else:
        print("  ✗ SOME TESTS FAILED")
        print("  Review errors above for details")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
