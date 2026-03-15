"""
Test All Scheduled Scripts - Verification Suite
Tests all 4 scheduled wrapper scripts before deploying to Task Scheduler
"""
import sys
from pathlib import Path
import time
import subprocess

BASE_DIR = Path(__file__).parent


def run_script(script_name: str) -> tuple[bool, str]:
    """Run a scheduled script and capture output"""
    script_path = BASE_DIR / script_name

    if not script_path.exists():
        return False, f"Script not found: {script_name}"

    try:
        print(f"\n{'='*60}")
        print(f"Testing: {script_name}")
        print(f"{'='*60}")

        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")

        success = result.returncode == 0
        return success, result.stdout

    except subprocess.TimeoutExpired:
        return False, "Script timeout (>2 minutes)"
    except Exception as e:
        return False, str(e)


def check_lock_files():
    """Check if any lock files remain after execution"""
    lock_dir = BASE_DIR / "logs"
    lock_files = list(lock_dir.glob("*.lock"))

    if lock_files:
        print(f"\n[WARNING] {len(lock_files)} lock file(s) still present:")
        for lock_file in lock_files:
            age = time.time() - lock_file.stat().st_mtime
            print(f"  - {lock_file.name} (age: {int(age)}s)")
        return False
    else:
        print("\n[OK] No lock files remaining (clean execution)")
        return True


def main():
    """Test all scheduled scripts"""
    print("="*60)
    print("SCHEDULED SCRIPTS VERIFICATION SUITE")
    print("="*60)
    print(f"Working Directory: {BASE_DIR}")
    print(f"Python: {sys.executable}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    scripts = [
        "scheduled_gmail_watcher.py",
        "scheduled_linkedin_watcher.py",
        "scheduled_approval_check.py",
        "scheduled_linkedin_auto_post.py"
    ]

    results = {}

    for script in scripts:
        success, output = run_script(script)
        results[script] = success
        time.sleep(2)  # Brief pause between tests

    # Check for remaining lock files
    locks_clean = check_lock_files()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for script, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} - {script}")

    print(f"\nLock Cleanup: {'[PASS]' if locks_clean else '[WARNING]'}")

    # Overall result
    all_passed = all(results.values()) and locks_clean

    print("\n" + "="*60)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED - Ready for Task Scheduler deployment")
    else:
        print("[FAILED] SOME TESTS FAILED - Review errors before deployment")
    print("="*60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
