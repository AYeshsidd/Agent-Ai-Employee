#!/usr/bin/env python3
"""Silver Tier - Multi-Channel Watcher Runner"""
import time
import signal
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from vault_manager import VaultManager
from bronze_logger import BronzeLogger
from skills.watcher_skills import GmailWatcherSkill, LinkedInWatcherSkill, WhatsAppWatcherSkill


class MultiChannelWatcher:
    """Manages multiple watcher skills"""

    def __init__(self):
        self.logger = BronzeLogger.get_logger("MultiChannelWatcher")
        self.watchers = {}
        self.running = True

    def initialize_watchers(self, enable_gmail=True, enable_linkedin=True, enable_whatsapp=True):
        """
        Initialize selected watchers

        Args:
            enable_gmail: Enable Gmail watcher
            enable_linkedin: Enable LinkedIn watcher
            enable_whatsapp: Enable WhatsApp watcher
        """
        BronzeLogger.log_skill_execution(
            self.logger, "MultiChannelWatcher", "initialize_watchers",
            "IN_PROGRESS", "Initializing watchers"
        )

        if enable_gmail:
            try:
                self.watchers['gmail'] = GmailWatcherSkill()
                print("[OK] Gmail watcher initialized")
            except Exception as e:
                print(f"[WARN] Gmail watcher failed to initialize: {str(e)}")

        if enable_linkedin:
            try:
                self.watchers['linkedin'] = LinkedInWatcherSkill()
                print("[OK] LinkedIn watcher initialized")
            except Exception as e:
                print(f"[WARN] LinkedIn watcher failed to initialize: {str(e)}")

        if enable_whatsapp:
            try:
                self.watchers['whatsapp'] = WhatsAppWatcherSkill()
                print("[OK] WhatsApp watcher initialized")
            except Exception as e:
                print(f"[WARN] WhatsApp watcher failed to initialize: {str(e)}")

        BronzeLogger.log_skill_execution(
            self.logger, "MultiChannelWatcher", "initialize_watchers",
            "SUCCESS", f"Initialized {len(self.watchers)} watchers"
        )

    def run_watch_cycle(self):
        """Run one watch cycle for all watchers"""
        total_tasks = 0

        for name, watcher in self.watchers.items():
            try:
                print(f"\n[{name.upper()}] Checking for new items...")
                tasks_created = watcher.watch()
                total_tasks += tasks_created

                if tasks_created > 0:
                    print(f"[{name.upper()}] Created {tasks_created} new task(s)")
                else:
                    print(f"[{name.upper()}] No new items")

            except Exception as e:
                print(f"[{name.upper()}] Error: {str(e)}")
                BronzeLogger.log_skill_execution(
                    self.logger, "MultiChannelWatcher", f"watch_{name}",
                    "FAILED", str(e)
                )

        return total_tasks

    def run(self, interval_seconds=300):
        """
        Run watchers continuously

        Args:
            interval_seconds: Time between watch cycles (default: 5 minutes)
        """
        print("\n" + "=" * 60)
        print("  Silver Tier - Multi-Channel Watcher")
        print("=" * 60)
        print(f"\nActive watchers: {', '.join(self.watchers.keys())}")
        print(f"Check interval: {interval_seconds} seconds")
        print("\nPress Ctrl+C to stop\n")

        BronzeLogger.log_skill_execution(
            self.logger, "MultiChannelWatcher", "run",
            "IN_PROGRESS", f"Starting watch loop with {len(self.watchers)} watchers"
        )

        cycle_count = 0

        while self.running:
            try:
                cycle_count += 1
                print(f"\n{'='*60}")
                print(f"  Watch Cycle #{cycle_count}")
                print(f"{'='*60}")

                total_tasks = self.run_watch_cycle()

                print(f"\n[SUMMARY] Cycle #{cycle_count} complete: {total_tasks} total task(s) created")

                if self.running:
                    print(f"\nWaiting {interval_seconds} seconds until next check...")
                    time.sleep(interval_seconds)

            except KeyboardInterrupt:
                print("\n\nStopping watchers...")
                self.running = False
                break

        self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        print("\nCleaning up...")

        for name, watcher in self.watchers.items():
            try:
                if hasattr(watcher, 'close'):
                    watcher.close()
                    print(f"[OK] {name.capitalize()} watcher closed")
            except Exception as e:
                print(f"[WARN] Error closing {name} watcher: {str(e)}")

        BronzeLogger.log_skill_execution(
            self.logger, "MultiChannelWatcher", "cleanup",
            "SUCCESS", "All watchers cleaned up"
        )

        print("\nWatchers stopped successfully")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nReceived interrupt signal...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Initialize vault
    VaultManager.initialize()

    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Create and configure watcher
    watcher = MultiChannelWatcher()

    # Initialize watchers (can be configured via command line args)
    # For now, enable all watchers
    watcher.initialize_watchers(
        enable_gmail=True,
        enable_linkedin=True,
        enable_whatsapp=True
    )

    if not watcher.watchers:
        print("\n[ERROR] No watchers initialized. Exiting.")
        return

    # Run with 5-minute intervals
    watcher.run(interval_seconds=300)


if __name__ == "__main__":
    main()
