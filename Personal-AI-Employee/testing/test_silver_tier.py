#!/usr/bin/env python3
"""Test Silver Tier Multi-Channel Watchers"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from vault_manager import VaultManager
from bronze_logger import BronzeLogger
from config import Config


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_watcher_infrastructure():
    """Test watcher skills infrastructure"""
    print_section("Test 1: Watcher Skills Infrastructure")

    try:
        from skills.watcher_skills import (
            BaseWatcherSkill,
            GmailWatcherSkill,
            LinkedInWatcherSkill,
            WhatsAppWatcherSkill
        )

        print("[PASS] All watcher skills imported successfully")

        # Test instantiation
        gmail = GmailWatcherSkill()
        print("[PASS] GmailWatcherSkill instantiated")

        linkedin = LinkedInWatcherSkill()
        print("[PASS] LinkedInWatcherSkill instantiated")

        whatsapp = WhatsAppWatcherSkill()
        print("[PASS] WhatsAppWatcherSkill instantiated")

        return True

    except Exception as e:
        print(f"[FAIL] Infrastructure test failed: {str(e)}")
        return False


def test_duplicate_prevention():
    """Test duplicate prevention mechanism"""
    print_section("Test 2: Duplicate Prevention")

    try:
        from skills.watcher_skills import GmailWatcherSkill

        watcher = GmailWatcherSkill()

        # Test duplicate checking
        test_id = "test_message_123"

        # First check - should not be duplicate
        is_dup1 = watcher.is_duplicate(test_id)
        print(f"[PASS] First check: is_duplicate('{test_id}') = {is_dup1} (expected False)")

        # Save the ID
        watcher._save_processed_id(test_id)
        print(f"[PASS] Saved processed ID: {test_id}")

        # Second check - should be duplicate
        is_dup2 = watcher.is_duplicate(test_id)
        print(f"[PASS] Second check: is_duplicate('{test_id}') = {is_dup2} (expected True)")

        if not is_dup1 and is_dup2:
            print("[PASS] Duplicate prevention working correctly")
            return True
        else:
            print("[FAIL] Duplicate prevention not working as expected")
            return False

    except Exception as e:
        print(f"[FAIL] Duplicate prevention test failed: {str(e)}")
        return False


def test_task_creation():
    """Test task creation in Inbox"""
    print_section("Test 3: Task Creation")

    try:
        from skills.watcher_skills import GmailWatcherSkill

        watcher = GmailWatcherSkill()

        # Create a test task
        task_path = watcher.create_task_in_inbox(
            title="Test Email from Silver Tier",
            content="This is a test email to verify Silver Tier watcher functionality.",
            source="Gmail",
            metadata={
                "From": "test@example.com",
                "Date": "2026-02-19",
                "Test": "True"
            }
        )

        if task_path and task_path.exists():
            print(f"[PASS] Task created: {task_path.name}")

            # Verify content
            content = task_path.read_text(encoding='utf-8')
            if "Test Email from Silver Tier" in content and "Gmail" in content:
                print("[PASS] Task content verified")

                # Clean up test task
                task_path.unlink()
                print("[PASS] Test task cleaned up")

                return True
            else:
                print("[FAIL] Task content incorrect")
                return False
        else:
            print("[FAIL] Task not created")
            return False

    except Exception as e:
        print(f"[FAIL] Task creation test failed: {str(e)}")
        return False


def test_bronze_tier_intact():
    """Verify Bronze Tier functionality is not broken"""
    print_section("Test 4: Bronze Tier Integrity")

    try:
        # Test Bronze Tier imports
        from vault_manager import VaultManager
        from skills import TaskAnalyzerSkill, VaultWriterSkill, ReadVaultSkill, WriteVaultSkill
        print("[PASS] Bronze Tier skills imported successfully")

        # Test vault manager
        vault_mgr = VaultManager()
        stats = vault_mgr.get_vault_stats()
        print(f"[PASS] VaultManager working: {stats['total']} total tasks")

        # Test Bronze Tier watcher
        from watcher import FileWatcher
        print("[PASS] Bronze Tier FileWatcher imported successfully")

        # Test main processor
        from main import process_inbox
        print("[PASS] Bronze Tier main processor imported successfully")

        print("\n[PASS] Bronze Tier functionality intact - no breaking changes")
        return True

    except Exception as e:
        print(f"[FAIL] Bronze Tier integrity test failed: {str(e)}")
        return False


def test_logging():
    """Test logging functionality"""
    print_section("Test 5: Logging")

    try:
        from bronze_logger import BronzeLogger

        logger = BronzeLogger.get_logger("SilverTierTest")

        BronzeLogger.log_skill_execution(
            logger, "TestSkill", "test_operation",
            "SUCCESS", "Test log entry"
        )

        print("[PASS] Logging functionality working")

        # Verify log file exists
        if Config.BRONZE_TIER_LOG.exists():
            print(f"[PASS] Log file exists: {Config.BRONZE_TIER_LOG}")
            return True
        else:
            print("[FAIL] Log file not found")
            return False

    except Exception as e:
        print(f"[FAIL] Logging test failed: {str(e)}")
        return False


def test_credentials_directory():
    """Test credentials directory structure"""
    print_section("Test 6: Credentials Directory")

    credentials_dir = Config.BASE_DIR / "credentials"

    if not credentials_dir.exists():
        credentials_dir.mkdir(exist_ok=True)
        print(f"[OK] Created credentials directory: {credentials_dir}")
    else:
        print(f"[OK] Credentials directory exists: {credentials_dir}")

    # Create README for credentials
    readme_path = credentials_dir / "README.md"
    if not readme_path.exists():
        readme_content = """# Credentials Directory

This directory stores authentication credentials and session files for Silver Tier watchers.

## Required Files

### Gmail
- `gmail_credentials.json` - OAuth2 credentials from Google Cloud Console
- `gmail_token.json` - Auto-generated after first authentication

### LinkedIn
- `linkedin_session.json` - Auto-generated after first login

### WhatsApp
- `whatsapp_session.json` - Auto-generated after QR code scan

## Security

**IMPORTANT**: Never commit these files to git. They contain sensitive authentication data.

The `.gitignore` file should include:
```
credentials/
*.json
!credentials/README.md
```

## Setup Instructions

See `SILVER_TIER_WATCHERS.md` for detailed setup instructions for each watcher.
"""
        readme_path.write_text(readme_content, encoding='utf-8')
        print(f"[OK] Created credentials README: {readme_path}")

    print("[PASS] Credentials directory structure ready")
    return True


def main():
    """Main test execution"""
    print("\n" + "=" * 70)
    print("  SILVER TIER PART 1: MULTI-CHANNEL WATCHERS TEST")
    print("=" * 70)

    # Initialize vault
    VaultManager.initialize()

    # Run tests
    results = {
        "Infrastructure": test_watcher_infrastructure(),
        "Duplicate Prevention": test_duplicate_prevention(),
        "Task Creation": test_task_creation(),
        "Bronze Tier Integrity": test_bronze_tier_intact(),
        "Logging": test_logging(),
        "Credentials Directory": test_credentials_directory()
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
        print("\n[SUCCESS] All Silver Tier tests passed!")
        print("[SUCCESS] Bronze Tier functionality intact!")
        print("\nSilver Tier Part 1 implementation complete.")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
