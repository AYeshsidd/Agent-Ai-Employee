#!/usr/bin/env python3
import time
import signal
import sys
from vault_manager import VaultManager
from watcher import FileWatcher


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nStopping watcher...")
    sys.exit(0)


def main():
    """Main entry point for watcher"""
    print("=" * 60)
    print("Bronze-tier File Watcher")
    print("=" * 60)
    print()

    VaultManager.initialize()

    watcher = FileWatcher()

    signal.signal(signal.SIGINT, signal_handler)

    try:
        watcher.start()
        print("Watcher is running. Press Ctrl+C to stop.")
        print()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        watcher.stop()
        print("Watcher stopped successfully")


if __name__ == "__main__":
    main()
