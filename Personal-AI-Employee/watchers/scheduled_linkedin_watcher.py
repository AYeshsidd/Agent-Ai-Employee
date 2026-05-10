"""
Scheduled LinkedIn Watcher - Safe for Windows Task Scheduler
Prevents overlapping executions with file-based lock
"""
import sys
from pathlib import Path
import time

# Ensure project root is in sys.path
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Local directory for lock files
BASE_DIR = Path(__file__).parent
from bronze_logger import BronzeLogger
from skills.watcher_skills.linkedin_watcher_skill import LinkedInWatcherSkill

# Lock file to prevent overlapping runs
LOCK_FILE = BASE_DIR / "logs" / "linkedin_watcher.lock"


def acquire_lock() -> bool:
    """Acquire lock to prevent duplicate execution"""
    if LOCK_FILE.exists():
        # Check if lock is stale (older than 15 minutes)
        lock_age = time.time() - LOCK_FILE.stat().st_mtime
        if lock_age < 900:  # 15 minutes
            print(f"[SKIP] LinkedIn Watcher already running (lock age: {int(lock_age)}s)")
            return False
        else:
            print(f"[WARN] Removing stale lock (age: {int(lock_age)}s)")
            LOCK_FILE.unlink()

    LOCK_FILE.parent.mkdir(exist_ok=True)
    LOCK_FILE.write_text(str(time.time()))
    return True


def release_lock():
    """Release lock after execution"""
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()


def main():
    """Run LinkedIn Watcher with lock protection"""
    if not acquire_lock():
        sys.exit(0)  # Exit silently if already running

    try:
        print(f"[START] LinkedIn Watcher - {time.strftime('%Y-%m-%d %H:%M:%S')}")

        watcher = LinkedInWatcherSkill()

        if watcher.authenticate():
            tasks_created = watcher.watch()
            print(f"[SUCCESS] Created {tasks_created} tasks from LinkedIn")
        else:
            print("[FAILED] LinkedIn authentication failed")

        watcher.close()

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        BronzeLogger.log_skill_execution(
            None, "ScheduledLinkedInWatcher", "main",
            "FAILED", str(e)
        )
    finally:
        release_lock()
        print(f"[END] LinkedIn Watcher - {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
