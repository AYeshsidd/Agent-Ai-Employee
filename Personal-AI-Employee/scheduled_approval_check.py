"""
Scheduled MCP Approval Check - Safe for Windows Task Scheduler
Checks for pending approvals and processes auto-approved actions
"""
import sys
from pathlib import Path
import time
import json

# Set working directory
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from bronze_logger import BronzeLogger
from approval_system.approval_manager import ApprovalManager

# Lock file to prevent overlapping runs
LOCK_FILE = BASE_DIR / "logs" / "approval_check.lock"


def acquire_lock() -> bool:
    """Acquire lock to prevent duplicate execution"""
    if LOCK_FILE.exists():
        # Check if lock is stale (older than 5 minutes)
        lock_age = time.time() - LOCK_FILE.stat().st_mtime
        if lock_age < 300:  # 5 minutes
            print(f"[SKIP] Approval check already running (lock age: {int(lock_age)}s)")
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
    """Check for pending approvals and report status"""
    if not acquire_lock():
        sys.exit(0)  # Exit silently if already running

    try:
        print(f"[START] Approval Check - {time.strftime('%Y-%m-%d %H:%M:%S')}")

        manager = ApprovalManager()
        pending = manager.get_pending_approvals()

        if pending:
            print(f"[INFO] {len(pending)} pending approval(s)")

            # Log summary of pending approvals
            for approval in pending[:5]:  # Show first 5
                action_type = approval.get('action_type', 'unknown')
                action_id = approval.get('action_id', 'unknown')[:8]
                print(f"  - {action_type} (ID: {action_id})")

            if len(pending) > 5:
                print(f"  ... and {len(pending) - 5} more")
        else:
            print("[INFO] No pending approvals")

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import logging
        logger = logging.getLogger("ApprovalCheck")
        if logger.hasHandlers():
            BronzeLogger.log_skill_execution(
                logger, "ScheduledApprovalCheck", "main",
                "FAILED", str(e)
            )
    finally:
        release_lock()
        print(f"[END] Approval Check - {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
