#!/usr/bin/env python3
"""Test Gmail Watcher Individually"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from vault_manager import VaultManager
from skills.watcher_skills import GmailWatcherSkill


def main():
    print("\n" + "=" * 70)
    print("  GMAIL WATCHER - INDIVIDUAL TEST")
    print("=" * 70)

    # Initialize vault
    VaultManager.initialize()

    # Create Gmail watcher
    print("\n[STEP 1] Initializing Gmail Watcher...")
    watcher = GmailWatcherSkill()
    print("[OK] Gmail Watcher initialized")

    # Authenticate
    print("\n[STEP 2] Authenticating with Gmail...")
    print("[INFO] This will open a browser for OAuth2 authentication")
    print("[INFO] Make sure you have gmail_credentials.json in credentials/ folder")

    if watcher.authenticate():
        print("[SUCCESS] Gmail authentication successful!")
    else:
        print("[FAILED] Gmail authentication failed")
        print("\n[HELP] Setup instructions:")
        print("  1. Go to Google Cloud Console")
        print("  2. Enable Gmail API")
        print("  3. Create OAuth2 credentials (Desktop app)")
        print("  4. Download as gmail_credentials.json")
        print("  5. Place in Bronze-tier/credentials/ folder")
        return

    # Watch for emails
    print("\n[STEP 3] Checking for unread emails...")
    tasks_created = watcher.watch()

    print(f"\n[RESULT] Created {tasks_created} task(s) from unread emails")

    if tasks_created > 0:
        print("[SUCCESS] Gmail watcher is working!")
        print("[INFO] Check Vault/Inbox/ for created tasks")
    else:
        print("[INFO] No unread emails found (this is normal)")
        print("[INFO] Send yourself a test email and run again")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
