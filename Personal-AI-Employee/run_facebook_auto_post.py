#!/usr/bin/env python3
"""Run Facebook Auto-Post - Post from Vault tasks to Facebook"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from vault_manager import VaultManager
from skills.facebook_auto_post_skill import FacebookAutoPostSkill


def list_facebook_tasks() -> list:
    """List all tasks in Vault that might contain Facebook posts"""
    vault = VaultManager()
    
    # Check Needs_Action folder for tasks
    needs_action = vault.vault_root / "Needs_Action"
    if not needs_action.exists():
        return []
    
    tasks = [f for f in needs_action.glob("*.md") if not f.name.endswith("_PLAN.md")]
    return tasks


def post_from_task(task_path: Path):
    """Post to Facebook from a specific task"""
    skill = FacebookAutoPostSkill()
    
    print(f"\n[INFO] Processing: {task_path.name}")
    
    success = skill.post_from_vault_task(task_path)
    
    if success:
        print(f"[OK] Posted to Facebook: {task_path.name}")
        return True
    else:
        print(f"[FAILED] Could not post: {task_path.name}")
        return False


def auto_post_all():
    """Auto-post all eligible tasks to Facebook"""
    tasks = list_facebook_tasks()
    
    if not tasks:
        print("\n[INFO] No tasks found in Needs_Action/")
        return
    
    print(f"\n[INFO] Found {len(tasks)} task(s) in Needs_Action/")
    print("[INFO] Checking for Facebook post content...\n")
    
    skill = FacebookAutoPostSkill()
    success_count = 0
    skip_count = 0
    
    for task in tasks:
        print(f"Processing: {task.name}")
        
        # Read task to check for Facebook content
        vault = VaultManager()
        content = vault.read_task(task) if vault else ""
        
        if content and ("## Facebook Post" in content or "## Description" in content):
            if skill.post_from_vault_task(task):
                success_count += 1
        else:
            print(f"  [SKIP] No Facebook post content found")
            skip_count += 1
    
    print(f"\n[RESULT] Posted: {success_count}, Skipped: {skip_count}")


def interactive_mode():
    """Interactive mode to select and post tasks"""
    print("\n" + "=" * 70)
    print("  FACEBOOK AUTO-POST - INTERACTIVE MODE")
    print("=" * 70)
    
    tasks = list_facebook_tasks()
    
    if not tasks:
        print("\n[INFO] No tasks found in Needs_Action/")
        return
    
    print(f"\n[INFO] Found {len(tasks)} task(s):\n")
    
    vault = VaultManager()
    for i, task in enumerate(tasks, 1):
        # Check if task has Facebook content
        content = vault.read_task(task) if vault.read_task(task) else ""
        has_facebook = "## Facebook Post" in content or "## Description" in content
        marker = "[FACEBOOK]" if has_facebook else "[NO CONTENT]"
        print(f"{i}. {marker} {task.stem}")
    
    print(f"\n{len(tasks) + 1}. Post ALL tasks with Facebook content")
    
    # Select task
    choice = input(f"\nEnter choice (1-{len(tasks) + 1}): ").strip()
    
    try:
        task_idx = int(choice) - 1
        
        if task_idx == len(tasks):
            # Post all
            auto_post_all()
        elif 0 <= task_idx < len(tasks):
            # Post specific task
            post_from_task(tasks[task_idx])
        else:
            print("[ERROR] Invalid choice")
    except ValueError:
        print("[ERROR] Invalid input")


def main():
    print("\n" + "=" * 70)
    print("  FACEBOOK AUTO-POST")
    print("=" * 70)
    
    # Initialize vault
    VaultManager.initialize()
    
    print("\nSelect mode:")
    print("1. Interactive mode (select task)")
    print("2. Auto-post all tasks with Facebook content")
    
    choice = input("\nEnter choice (1-2): ").strip()
    
    if choice == "1":
        interactive_mode()
    elif choice == "2":
        auto_post_all()
    else:
        print("[ERROR] Invalid choice")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
