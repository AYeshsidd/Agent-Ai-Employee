#!/usr/bin/env python3
import time
import signal
import sys
from pathlib import Path

# Ensure project root is in sys.path
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from vault_manager import VaultManager
from watchers.watcher import FileWatcher


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
