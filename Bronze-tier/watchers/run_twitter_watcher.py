#!/usr/bin/env python3
"""Run Twitter Watcher - Monitor Twitter/X for new messages and notifications"""
import sys
import signal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from vault_manager import VaultManager
from skills.watcher_skills.twitter_watcher_skill import TwitterWatcherSkill


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nReceived interrupt signal...")
    if 'watcher' in globals():
        watcher.close()
    sys.exit(0)


def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("  Twitter/X Watcher")
    print("=" * 60)

    # Initialize vault
    VaultManager.initialize()

    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Create watcher
    watcher = TwitterWatcherSkill()

    print("\n[INFO] Starting Twitter watcher...")
    print("[INFO] Monitoring for new notifications and DMs")
    print("[INFO] Press Ctrl+C to stop\n")

    try:
        # Run single watch cycle
        tasks_created = watcher.watch()
        
        print(f"\n[RESULT] Created {tasks_created} new task(s) from Twitter")
        print("[INFO] Tasks saved to Vault/Inbox")
        
    except Exception as e:
        print(f"\n[ERROR] Watcher failed: {str(e)}")
    finally:
        watcher.close()
        print("\n[INFO] Twitter watcher stopped")


if __name__ == "__main__":
    main()
