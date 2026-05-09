"""
Ralph Wiggum Loop - Autonomous Multi-Step Task Execution

This package provides autonomous task execution capabilities for the
Autonomous FTE system.

Features:
- Automatic task detection from Inbox/Needs_Action
- Task type analysis and action planning
- Multi-MCP support (Social, Odoo, Email)
- Error handling with retries and fallbacks
- Comprehensive logging and audit trail
- Continuous or single-pass execution modes

Usage:
    from ralph_wiggum_loop import run_loop
    
    # Run continuously
    run_loop()
    
    # Run single pass
    run_loop(single_pass=True)
    
    # Process specific task
    from ralph_wiggum_loop import run_single_task
    from pathlib import Path
    run_single_task(Path("Vault/Needs_Action/task.md"))
"""

from ralph_wiggum_loop.core import TaskType, TaskStatus, TaskAction, get_loop_logger
from ralph_wiggum_loop.loop import RalphWiggumLoop, get_loop, run_single_task


def run_loop(single_pass: bool = False, scan_interval: int = 60, 
             max_retries: int = 3, retry_delay: float = 2.0):
    """
    Run the Ralph Wiggum Loop
    
    Args:
        single_pass: If True, run once and exit
        scan_interval: Seconds between scans (ignored if single_pass=True)
        max_retries: Maximum retry attempts per action
        retry_delay: Base delay between retries (seconds)
    """
    loop = RalphWiggumLoop(
        max_retries=max_retries,
        retry_delay=retry_delay,
        scan_interval=scan_interval
    )
    loop.run(single_pass=single_pass)


__all__ = [
    # Core
    'TaskType',
    'TaskStatus', 
    'TaskAction',
    'get_loop_logger',
    
    # Loop
    'RalphWiggumLoop',
    'get_loop',
    'run_single_task',
    'run_loop',
]
