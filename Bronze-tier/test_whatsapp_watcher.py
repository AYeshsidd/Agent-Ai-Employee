#!/usr/bin/env python3
"""Test WhatsApp Watcher Individually"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from vault_manager import VaultManager
from skills.watcher_skills import WhatsAppWatcherSkill


def main():
    print("\n" + "=" * 70)
    print("  WHATSAPP WATCHER - INDIVIDUAL TEST")
    print("=" * 70)

    # Initialize vault
    VaultManager.initialize()

    # Create WhatsApp watcher
    print("\n[STEP 1] Initializing WhatsApp Watcher...")
    watcher = WhatsAppWatcherSkill()
    print("[OK] WhatsApp Watcher initialized")

    # Authenticate
    print("\n[STEP 2] Authenticating with WhatsApp Web...")
    print("[INFO] This will open a browser window with WhatsApp Web")
    print("[INFO] If not logged in, you'll see a QR code")
    print("[INFO] Scan the QR code with your WhatsApp mobile app")
    print("[INFO] Session will be saved for future use")
    print("\nPress Enter to continue...")
    input()

    if watcher.authenticate():
        print("[SUCCESS] WhatsApp Web authentication successful!")
    else:
        print("[FAILED] WhatsApp Web authentication failed")
        print("\n[HELP] Troubleshooting:")
        print("  1. Make sure Playwright is installed: pip install playwright")
        print("  2. Install browsers: playwright install chromium")
        print("  3. Make sure your phone has internet connection")
        print("  4. Try deleting credentials/whatsapp_session.json and retry")
        return

    # Watch for messages
    print("\n[STEP 3] Checking for unread WhatsApp messages...")
    print("[INFO] This may take a few seconds...")

    try:
        tasks_created = watcher.watch()

        print(f"\n[RESULT] Created {tasks_created} task(s) from WhatsApp messages")

        if tasks_created > 0:
            print("[SUCCESS] WhatsApp watcher is working!")
            print("[INFO] Check Vault/Inbox/ for created tasks")
        else:
            print("[INFO] No unread messages found (this is normal)")
            print("[INFO] Send yourself a test message and run again")

    except Exception as e:
        print(f"[ERROR] Watch failed: {str(e)}")
    finally:
        # Close browser
        print("\n[STEP 4] Closing browser...")
        watcher.close()
        print("[OK] Browser closed")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
