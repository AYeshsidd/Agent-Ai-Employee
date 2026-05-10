#!/usr/bin/env python3
"""
Ralph Wiggum Loop Runner

Command-line interface for the Ralph Wiggum Loop autonomous task execution system.

Usage:
    python run_ralph_wiggum.py                  # Run continuously
    python run_ralph_wiggum.py --single         # Run single pass
    python run_ralph_wiggum.py --task FILE.md   # Process specific task
    python run_ralph_wiggum.py --interval 120   # Set scan interval
    python run_ralph_wiggum.py --help           # Show help
"""
import sys
import argparse
from pathlib import Path

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from vault_manager import VaultManager
from bronze_logger import BronzeLogger


def main():
    parser = argparse.ArgumentParser(
        description='Ralph Wiggum Loop - Autonomous Task Execution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_ralph_wiggum.py                     Run continuously (60s interval)
  python run_ralph_wiggum.py --single            Run once and exit
  python run_ralph_wiggum.py --interval 120      Run with 2-minute intervals
  python run_ralph_wiggum.py --task task.md      Process specific task
  python run_ralph_wiggum.py --retries 5         Set max retries to 5
        """
    )
    
    parser.add_argument(
        '--single', '-s',
        action='store_true',
        help='Run single pass and exit (no continuous scanning)'
    )
    
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Scan interval in seconds (default: 60)'
    )
    
    parser.add_argument(
        '--task', '-t',
        type=str,
        help='Process specific task file'
    )
    
    parser.add_argument(
        '--retries', '-r',
        type=int,
        default=3,
        help='Maximum retry attempts (default: 3)'
    )
    
    parser.add_argument(
        '--delay', '-d',
        type=float,
        default=2.0,
        help='Base retry delay in seconds (default: 2.0)'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show loop status and exit'
    )
    
    args = parser.parse_args()
    
    # Initialize vault
    VaultManager.initialize()
    
    print("\n" + "=" * 70)
    print("  RALPH WIGGUM LOOP - AUTONOMOUS TASK EXECUTION")
    print("=" * 70)
    
    # Handle status request
    if args.status:
        from ralph_wiggum_loop import get_loop
        loop = get_loop()
        status = loop.get_status()
        
        print("\nLoop Status:")
        print(f"  Running: {status['running']}")
        print(f"  Scan Interval: {status['scan_interval']}s")
        print(f"\nFolders:")
        print(f"  Inbox: {status['folders']['inbox']}")
        print(f"  Needs_Action: {status['folders']['needs_action']}")
        print(f"  Done: {status['folders']['done']}")
        return
    
    # Handle specific task
    if args.task:
        task_path = Path(args.task)
        
        if not task_path.exists():
            # Try in Needs_Action folder
            task_path = Config.NEEDS_ACTION / args.task
        
        if not task_path.exists():
            print(f"\n[ERROR] Task file not found: {args.task}")
            return
        
        from ralph_wiggum_loop import run_single_task
        
        print(f"\n[INFO] Processing task: {task_path.name}")
        success = run_single_task(task_path)
        
        if success:
            print(f"\n[OK] Task completed successfully")
        else:
            print(f"\n[WARN] Task completed with errors")
        return
    
    # Run loop
    from ralph_wiggum_loop import run_loop
    
    print(f"\n[INFO] Configuration:")
    print(f"  Mode: {'Single Pass' if args.single else 'Continuous'}")
    print(f"  Scan Interval: {args.interval}s")
    print(f"  Max Retries: {args.retries}")
    print(f"  Retry Delay: {args.delay}s")
    print(f"\n[INFO] Starting loop... (Press Ctrl+C to stop)")
    
    run_loop(
        single_pass=args.single,
        scan_interval=args.interval,
        max_retries=args.retries,
        retry_delay=args.delay
    )
    
    print("\n" + "=" * 70)
    print("  LOOP COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    from config import Config
    main()
