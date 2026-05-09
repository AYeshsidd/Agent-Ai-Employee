#!/usr/bin/env python3
"""Run Approval Dashboard - Silver Tier Part 5"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from approval_system import ApprovalDashboard


def main():
    """Run approval dashboard"""
    dashboard = ApprovalDashboard()

    # Check for command line mode
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

        if mode == "batch":
            print("[INFO] Running in batch approval mode")
            dashboard.batch_approve_mode()

        elif mode == "list":
            print("[INFO] Listing pending approvals")
            dashboard.display_pending_approvals()

        elif mode == "stats":
            print("[INFO] Showing statistics")
            dashboard.show_statistics()

        elif mode == "help":
            print("\nApproval Dashboard - Usage:")
            print("  python run_approval_dashboard.py          # Interactive mode")
            print("  python run_approval_dashboard.py batch    # Batch approval mode")
            print("  python run_approval_dashboard.py list     # List pending approvals")
            print("  python run_approval_dashboard.py stats    # Show statistics")
            print("  python run_approval_dashboard.py help     # Show this help")
            print()

        else:
            print(f"[ERROR] Unknown mode: {mode}")
            print("[INFO] Use 'help' to see available modes")

    else:
        # Run interactive mode
        dashboard.interactive_mode()


if __name__ == "__main__":
    main()
