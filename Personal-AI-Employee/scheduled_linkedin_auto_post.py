"""
Scheduled LinkedIn Auto Post - Safe for Windows Task Scheduler
Posts content from Vault/Needs_Action to LinkedIn
"""
import sys
from pathlib import Path
import time

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from bronze_logger import BronzeLogger
from skills.linkedin_auto_post_skill import LinkedInAutoPostSkill
from vault_manager import VaultManager

# Lock file to prevent overlapping runs
LOCK_FILE = root / "logs" / "linkedin_auto_post.lock"


def acquire_lock() -> bool:
    """Acquire lock to prevent duplicate execution"""
    if LOCK_FILE.exists():
        # Check if lock is stale (older than 30 minutes)
        lock_age = time.time() - LOCK_FILE.stat().st_mtime
        if lock_age < 1800:  # 30 minutes
            print(f"[SKIP] LinkedIn Auto Post already running (lock age: {int(lock_age)}s)")
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
    """Run LinkedIn Auto Post with lock protection"""
    if not acquire_lock():
        sys.exit(0)  # Exit silently if already running

    poster = None
    try:
        print(f"[START] LinkedIn Auto Post - {time.strftime('%Y-%m-%d %H:%M:%S')}")

        poster = LinkedInAutoPostSkill()
        vault_mgr = VaultManager()

        if not poster.authenticate():
            print("[FAILED] LinkedIn authentication failed")
            return

        # Look for tasks tagged with #linkedin-post in Needs_Action
        needs_action_tasks = vault_mgr.list_tasks("needs_action")

        linkedin_tasks = []
        for task_path in needs_action_tasks:
            content = vault_mgr.read_task(task_path)
            if content and "#linkedin-post" in content.lower():
                linkedin_tasks.append(task_path)

        if not linkedin_tasks:
            print("[INFO] No tasks found with #linkedin-post tag")
            return

        print(f"[INFO] Found {len(linkedin_tasks)} task(s) to post")

        posts_created = 0
        for task_path in linkedin_tasks:
            print(f"[INFO] Processing: {task_path.name}")

            success = poster.post_from_vault_task(task_path)

            if success:
                print(f"[SUCCESS] Posted from task: {task_path.name}")
                vault_mgr.move_task(task_path, "done")
                posts_created += 1
            else:
                print(f"[FAILED] Could not post from task: {task_path.name}")

            # Wait between posts
            if len(linkedin_tasks) > 1 and posts_created < len(linkedin_tasks):
                print("[INFO] Waiting 60 seconds before next post...")
                time.sleep(60)

        print(f"[SUCCESS] Posted {posts_created} item(s) to LinkedIn")

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import logging
        logger = logging.getLogger("LinkedInAutoPost")
        if logger.hasHandlers():
            BronzeLogger.log_skill_execution(
                logger, "ScheduledLinkedInAutoPost", "main",
                "FAILED", str(e)
            )
    finally:
        if poster:
            poster.close()
        release_lock()
        print(f"[END] LinkedIn Auto Post - {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
