#!/usr/bin/env python3
"""Test Plan Generator Skill"""
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


def create_sample_task():
    """Create a sample task for testing"""
    vault = VaultManager()

    sample_task = """# Implement User Authentication Feature

## Description
Need to implement a secure user authentication system with login, logout, and session management. The system should support email/password authentication and include password reset functionality.

**Source:** Gmail
**Priority:** High
**Tags:** development, security, authentication
**Timestamp:** 2026-02-24 10:30:00

## Action Items
- Design database schema for user accounts
- Implement password hashing with bcrypt
- Create login and logout endpoints
- Add session management with JWT tokens
- Implement password reset flow with email verification
- Write unit tests for authentication logic
- Update API documentation
"""

    task_path = vault.write_task(
        content=sample_task,
        folder="inbox",
        filename="Implement_User_Authentication_Feature.md"
    )

    return task_path


def main():
    print("\n" + "=" * 70)
    print("  PLAN GENERATOR SKILL - TEST")
    print("=" * 70)

    # Initialize vault
    VaultManager.initialize()

    # Create sample task
    print("\n[STEP 1] Creating sample task in Vault...")
    task_path = create_sample_task()
    if task_path:
        print(f"[OK] Sample task created: {task_path.name}")
    else:
        print("[FAILED] Could not create sample task")
        return

    # Initialize Plan Generator
    print("\n[STEP 2] Initializing Plan Generator Skill...")
    plan_gen = PlanGeneratorSkill()
    print("[OK] Plan Generator initialized")

    # Generate plan
    print("\n[STEP 3] Generating Plan.md from task...")
    plan_path = plan_gen.generate_plan(task_path)

    if plan_path:
        print(f"[SUCCESS] Plan generated: {plan_path.name}")
        print(f"[INFO] Location: {plan_path}")

        # Display plan content
        print("\n" + "=" * 70)
        print("  GENERATED PLAN CONTENT")
        print("=" * 70)
        print(plan_path.read_text(encoding='utf-8'))
        print("=" * 70)
    else:
        print("[FAILED] Plan generation failed")

    print("\n[RESULT] Test completed")
    print("[INFO] Check Vault/Inbox/ for the generated plan file")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
