#!/usr/bin/env python3
"""Test Silver Tier Part 2: LinkedIn Auto Post Skill"""
import sys
from pathlib import Path

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from vault_manager import VaultManager
from bronze_logger import BronzeLogger
from config import Config


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_skill_import():
    """Test LinkedIn Auto Post skill import"""
    print_section("Test 1: Skill Import")

    try:
        from skills.linkedin_auto_post_skill import LinkedInAutoPostSkill
        print("[PASS] LinkedInAutoPostSkill imported successfully")

        # Test instantiation
        skill = LinkedInAutoPostSkill()
        print("[PASS] LinkedInAutoPostSkill instantiated")

        return True

    except Exception as e:
        print(f"[FAIL] Skill import failed: {str(e)}")
        return False


def test_duplicate_prevention():
    """Test duplicate post prevention"""
    print_section("Test 2: Duplicate Prevention")

    try:
        from skills.linkedin_auto_post_skill import LinkedInAutoPostSkill

        skill = LinkedInAutoPostSkill()

        # Test duplicate checking
        test_id = "test_post_123"

        # First check - should not be duplicate
        is_dup1 = skill.is_already_posted(test_id)
        print(f"[PASS] First check: is_already_posted('{test_id}') = {is_dup1} (expected False)")

        # Save the ID
        skill._save_posted_id(test_id)
        print(f"[PASS] Saved posted ID: {test_id}")

        # Second check - should be duplicate
        is_dup2 = skill.is_already_posted(test_id)
        print(f"[PASS] Second check: is_already_posted('{test_id}') = {is_dup2} (expected True)")

        if not is_dup1 and is_dup2:
            print("[PASS] Duplicate prevention working correctly")
            return True
        else:
            print("[FAIL] Duplicate prevention not working as expected")
            return False

    except Exception as e:
        print(f"[FAIL] Duplicate prevention test failed: {str(e)}")
        return False


def test_content_extraction():
    """Test post content extraction from task"""
    print_section("Test 3: Content Extraction")

    try:
        from skills.linkedin_auto_post_skill import LinkedInAutoPostSkill

        skill = LinkedInAutoPostSkill()

        # Test task with LinkedIn Post section
        task_content = """# Test Task

## Description

This is a test task.

## LinkedIn Post

This is the LinkedIn post content.
It should be extracted correctly.

#test #linkedin

## Action Items

- [ ] Test item
"""

        extracted = skill._extract_post_content(task_content)

        if extracted and "This is the LinkedIn post content" in extracted:
            print("[PASS] Content extracted from ## LinkedIn Post section")
            print(f"[INFO] Extracted: {extracted[:100]}...")
            return True
        else:
            print("[FAIL] Content extraction failed")
            return False

    except Exception as e:
        print(f"[FAIL] Content extraction test failed: {str(e)}")
        return False


def test_vault_logging():
    """Test post logging to Vault"""
    print_section("Test 4: Vault Logging")

    try:
        from skills.linkedin_auto_post_skill import LinkedInAutoPostSkill

        skill = LinkedInAutoPostSkill()

        # Test logging
        test_content = "Test LinkedIn post content for logging"
        test_id = "test_log_001"

        skill._log_post_to_vault(test_content, test_id)

        # Check if log file was created in Done folder
        done_files = list(Config.DONE.glob(f"*{test_id}*.md"))

        if done_files:
            print(f"[PASS] Post logged to Vault: {done_files[0].name}")

            # Verify content
            content = done_files[0].read_text(encoding='utf-8')
            if test_content in content and "LinkedIn Post" in content:
                print("[PASS] Log content verified")

                # Clean up test file
                done_files[0].unlink()
                print("[PASS] Test log cleaned up")

                return True
            else:
                print("[FAIL] Log content incorrect")
                return False
        else:
            print("[FAIL] Log file not created")
            return False

    except Exception as e:
        print(f"[FAIL] Vault logging test failed: {str(e)}")
        return False


def test_bronze_tier_intact():
    """Verify Bronze Tier functionality is not broken"""
    print_section("Test 5: Bronze Tier Integrity")

    try:
        # Test Bronze Tier imports
        from vault_manager import VaultManager
        from skills import TaskAnalyzerSkill, VaultWriterSkill, ReadVaultSkill, WriteVaultSkill
        print("[PASS] Bronze Tier skills imported successfully")

        # Test Silver Tier Part 1 imports
        from skills.watcher_skills import GmailWatcherSkill, LinkedInWatcherSkill, WhatsAppWatcherSkill
        print("[PASS] Silver Tier Part 1 skills imported successfully")

        # Test vault manager
        vault_mgr = VaultManager()
        stats = vault_mgr.get_vault_stats()
        print(f"[PASS] VaultManager working: {stats['total']} total tasks")

        print("\n[PASS] Bronze Tier and Silver Tier Part 1 functionality intact")
        return True

    except Exception as e:
        print(f"[FAIL] Bronze Tier integrity test failed: {str(e)}")
        return False


def test_sample_task_creation():
    """Test creating a sample LinkedIn post task"""
    print_section("Test 6: Sample Task Creation")

    try:
        vault_mgr = VaultManager()

        sample_content = """# Test LinkedIn Post

## LinkedIn Post

Test post content for automated posting.

#linkedin-post #test
"""

        task_path = vault_mgr.write_task(
            sample_content,
            folder="needs_action",
            filename="test_linkedin_post.md"
        )

        if task_path and task_path.exists():
            print(f"[PASS] Sample task created: {task_path.name}")

            # Verify content
            content = task_path.read_text(encoding='utf-8')
            if "#linkedin-post" in content:
                print("[PASS] Task tagged correctly")

                # Clean up
                task_path.unlink()
                print("[PASS] Test task cleaned up")

                return True
            else:
                print("[FAIL] Task not tagged correctly")
                return False
        else:
            print("[FAIL] Sample task not created")
            return False

    except Exception as e:
        print(f"[FAIL] Sample task creation test failed: {str(e)}")
        return False


def main():
    """Main test execution"""
    print("\n" + "=" * 70)
    print("  SILVER TIER PART 2: LINKEDIN AUTO POST TEST")
    print("=" * 70)

    # Initialize vault
    VaultManager.initialize()

    # Run tests
    results = {
        "Skill Import": test_skill_import(),
        "Duplicate Prevention": test_duplicate_prevention(),
        "Content Extraction": test_content_extraction(),
        "Vault Logging": test_vault_logging(),
        "Bronze Tier Integrity": test_bronze_tier_intact(),
        "Sample Task Creation": test_sample_task_creation()
    }

    # Summary
    print_section("TEST SUMMARY")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {test_name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All Silver Tier Part 2 tests passed!")
        print("[SUCCESS] Bronze Tier and Silver Tier Part 1 functionality intact!")
        print("\nSilver Tier Part 2 implementation complete.")
        print("\nNOTE: Actual LinkedIn posting requires:")
        print("  1. Valid LinkedIn session")
        print("  2. Manual testing with run_linkedin_auto_post.py")
        print("  3. Monitoring for automation detection")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
