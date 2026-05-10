#!/usr/bin/env python3
"""Run Plan Generator - Silver Tier Part 3"""
import sys
from pathlib import Path

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from vault_manager import VaultManager
from skills.plan_generator_skill import PlanGeneratorSkill


def list_tasks_in_folder(folder_name: str) -> list:
    """List all tasks in a vault folder"""
    vault = VaultManager()
    folder_path = vault.vault_root / folder_name

    if not folder_path.exists():
        return []

    tasks = [f for f in folder_path.glob("*.md") if not f.name.endswith("_PLAN.md")]
    return tasks


def generate_plan_for_task(task_path: Path):
    """Generate plan for a specific task"""
    plan_gen = PlanGeneratorSkill()
    plan_path = plan_gen.generate_plan(task_path)

    if plan_path:
        print(f"\n[SUCCESS] Plan generated: {plan_path.name}")
        print(f"[INFO] Location: {plan_path}")
        return True
    else:
        print(f"\n[FAILED] Could not generate plan for: {task_path.name}")
        return False


def generate_plans_for_folder(folder_name: str):
    """Generate plans for all tasks in a folder"""
    tasks = list_tasks_in_folder(folder_name)

    if not tasks:
        print(f"\n[INFO] No tasks found in {folder_name}/")
        return

    print(f"\n[INFO] Found {len(tasks)} task(s) in {folder_name}/")
    print("[INFO] Generating plans...\n")

    success_count = 0
    for task in tasks:
        print(f"Processing: {task.name}")
        if generate_plan_for_task(task):
            success_count += 1

    print(f"\n[RESULT] Generated {success_count}/{len(tasks)} plans successfully")


def interactive_mode():
    """Interactive mode to select and generate plans"""
    print("\n" + "=" * 70)
    print("  PLAN GENERATOR - INTERACTIVE MODE")
    print("=" * 70)

    # Select folder
    print("\nSelect folder:")
    print("1. Inbox")
    print("2. Needs_Action")
    print("3. Done")

    choice = input("\nEnter choice (1-3): ").strip()

    folder_map = {"1": "Inbox", "2": "Needs_Action", "3": "Done"}
    folder_name = folder_map.get(choice)

    if not folder_name:
        print("[ERROR] Invalid choice")
        return

    # List tasks
    tasks = list_tasks_in_folder(folder_name)

    if not tasks:
        print(f"\n[INFO] No tasks found in {folder_name}/")
        return

    print(f"\n[INFO] Found {len(tasks)} task(s) in {folder_name}/:\n")
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task.stem}")

    print(f"{len(tasks) + 1}. Generate plans for ALL tasks")

    # Select task
    task_choice = input(f"\nEnter choice (1-{len(tasks) + 1}): ").strip()

    try:
        task_idx = int(task_choice) - 1

        if task_idx == len(tasks):
            # Generate for all
            generate_plans_for_folder(folder_name)
        elif 0 <= task_idx < len(tasks):
            # Generate for specific task
            generate_plan_for_task(tasks[task_idx])
        else:
            print("[ERROR] Invalid choice")
    except ValueError:
        print("[ERROR] Invalid input")


def main():
    print("\n" + "=" * 70)
    print("  PLAN GENERATOR - SILVER TIER PART 3")
    print("=" * 70)

    # Initialize vault
    VaultManager.initialize()

    print("\nSelect mode:")
    print("1. Interactive mode (select tasks)")
    print("2. Generate plans for all Inbox tasks")
    print("3. Generate plans for all Needs_Action tasks")
    print("4. Generate plans for all Done tasks")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        interactive_mode()
    elif choice == "2":
        generate_plans_for_folder("Inbox")
    elif choice == "3":
        generate_plans_for_folder("Needs_Action")
    elif choice == "4":
        generate_plans_for_folder("Done")
    else:
        print("[ERROR] Invalid choice")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
