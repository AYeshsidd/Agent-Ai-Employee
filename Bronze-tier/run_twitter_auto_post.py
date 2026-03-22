#!/usr/bin/env python3
"""Run Twitter Auto-Post - Post from Vault tasks to Twitter"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from vault_manager import VaultManager
from skills.twitter_auto_post_skill import TwitterAutoPostSkill


def list_twitter_tasks() -> list:
    """List all tasks in Vault that might contain Twitter posts"""
    vault = VaultManager()
    
    # Check Needs_Action folder for tasks
    needs_action = vault.vault_root / "Needs_Action"
    if not needs_action.exists():
        return []
    
    tasks = [f for f in needs_action.glob("*.md") if not f.name.endswith("_PLAN.md")]
    return tasks


def post_from_task(task_path: Path):
    """Post to Twitter from a specific task"""
    skill = TwitterAutoPostSkill()
    
    print(f"\n[INFO] Processing: {task_path.name}")
    
    success = skill.post_from_vault_task(task_path)
    
    if success:
        print(f"[OK] Posted to Twitter: {task_path.name}")
        return True
    else:
        print(f"[FAILED] Could not post: {task_path.name}")
        return False


def auto_post_all():
    """Auto-post all eligible tasks to Twitter"""
    tasks = list_twitter_tasks()
    
    if not tasks:
        print("\n[INFO] No tasks found in Needs_Action/")
        return
    
    print(f"\n[INFO] Found {len(tasks)} task(s) in Needs_Action/")
    print("[INFO] Checking for Twitter post content...\n")
    
    skill = TwitterAutoPostSkill()
    success_count = 0
    skip_count = 0
    
    for task in tasks:
        print(f"Processing: {task.name}")
        
        # Read task to check for Twitter content
        content = vault_manager.read_task(task) if (vault_manager := VaultManager()) else ""
        
        if content and ("## Twitter Post" in content or "## Tweet" in content or "## Description" in content):
            if skill.post_from_vault_task(task):
                success_count += 1
        else:
            print(f"  [SKIP] No Twitter post content found")
            skip_count += 1
    
    print(f"\n[RESULT] Posted: {success_count}, Skipped: {skip_count}")


def interactive_mode():
    """Interactive mode to select and post tasks"""
    print("\n" + "=" * 70)
    print("  TWITTER AUTO-POST - INTERACTIVE MODE")
    print("=" * 70)
    
    tasks = list_twitter_tasks()
    
    if not tasks:
        print("\n[INFO] No tasks found in Needs_Action/")
        return
    
    print(f"\n[INFO] Found {len(tasks)} task(s):\n")
    
    for i, task in enumerate(tasks, 1):
        # Check if task has Twitter content
        content = VaultManager().read_task(task) if VaultManager().read_task(task) else ""
        has_twitter = "## Twitter Post" in content or "## Tweet" in content or "## Description" in content
        marker = "[TWITTER]" if has_twitter else "[NO CONTENT]"
        print(f"{i}. {marker} {task.stem}")
    
    print(f"\n{len(tasks) + 1}. Post ALL tasks with Twitter content")
    
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
    print("  TWITTER AUTO-POST")
    print("=" * 70)
    
    # Initialize vault
    VaultManager.initialize()
    
    print("\nSelect mode:")
    print("1. Interactive mode (select task)")
    print("2. Auto-post all tasks with Twitter content")
    
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
