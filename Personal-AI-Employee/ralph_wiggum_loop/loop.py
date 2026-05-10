#!/usr/bin/env python3
"""
Ralph Wiggum Loop - Main Orchestrator

Orchestrates autonomous task execution:
1. Scans Inbox and Needs_Action folders
2. Analyzes each task
3. Plans and executes actions
4. Handles errors with retries
5. Logs all steps
6. Moves completed tasks to Done
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import time
import sys

# Ensure project root is in sys.path
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from ralph_wiggum_loop.core import TaskStatus, get_loop_logger
from ralph_wiggum_loop.task_analyzer import TaskAnalyzer
from ralph_wiggum_loop.action_executor import ActionExecutor
from ralph_wiggum_loop.error_handler import ErrorHandler, ErrorSeverity
from config import Config


class RalphWiggumLoop:
    """Main orchestrator for autonomous task execution"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0,
                 scan_interval: int = 60, auto_start: bool = False):
        """
        Initialize Ralph Wiggum Loop
        
        Args:
            max_retries: Maximum retry attempts per action
            retry_delay: Base delay between retries (seconds)
            scan_interval: Time between scans (seconds, 0 = run once)
            auto_start: Auto-start execution on init
        """
        self.logger = get_loop_logger()
        self.analyzer = TaskAnalyzer()
        self.executor = ActionExecutor()
        self.error_handler = ErrorHandler(max_retries, retry_delay)
        self.scan_interval = scan_interval
        self.running = False
        
        self.logger.logger.info("=" * 60)
        self.logger.logger.info("  RALPH WIGGUM LOOP INITIALIZED")
        self.logger.logger.info(f"  Max Retries: {max_retries}")
        self.logger.logger.info(f"  Retry Delay: {retry_delay}s")
        self.logger.logger.info(f"  Scan Interval: {scan_interval}s")
        self.logger.logger.info("=" * 60)
    
    def run(self, single_pass: bool = False):
        """
        Run the Ralph Wiggum Loop
        
        Args:
            single_pass: If True, run once and exit (no continuous scanning)
        """
        self.running = True
        
        self.logger.logger.info("\n[LOOP] Starting Ralph Wiggum Loop...")
        
        try:
            while self.running:
                # Scan and process tasks
                tasks_processed = self._scan_and_process()
                
                if single_pass:
                    self.logger.logger.info(f"\n[LOOP] Single pass complete. Processed {tasks_processed} tasks.")
                    break
                
                # Wait before next scan
                if self.scan_interval > 0 and tasks_processed == 0:
                    self.logger.logger.info(f"[LOOP] No tasks found. Waiting {self.scan_interval}s...")
                    time.sleep(self.scan_interval)
                elif self.scan_interval > 0:
                    time.sleep(self.scan_interval)
                    
        except KeyboardInterrupt:
            self.logger.logger.info("\n[LOOP] Interrupted by user")
            self.running = False
        except Exception as e:
            self.logger.logger.error(f"[LOOP] Fatal error: {e}")
            self.running = False
        
        self.logger.logger.info("[LOOP] Ralph Wiggum Loop stopped")
    
    def _scan_and_process(self) -> int:
        """Scan folders and process tasks"""
        tasks_processed = 0
        
        # Scan Needs_Action folder (primary)
        needs_action_tasks = self._scan_folder(Config.NEEDS_ACTION)
        tasks_processed += len(needs_action_tasks)
        
        # Scan Inbox folder (secondary - auto-categorize)
        inbox_tasks = self._scan_folder(Config.INBOX)
        tasks_processed += len(inbox_tasks)
        
        return tasks_processed
    
    def _scan_folder(self, folder: Path) -> List[str]:
        """Scan a folder for tasks and process them"""
        processed_ids = []
        
        if not folder.exists():
            return processed_ids
        
        # Get all markdown files
        task_files = list(folder.glob("*.md"))
        
        if not task_files:
            return processed_ids
        
        self.logger.logger.info(f"\n[SCAN] Found {len(task_files)} task(s) in {folder.name}/")
        
        for task_file in task_files:
            task_id = task_file.stem
            
            # Skip already processed in this run
            if task_id in processed_ids:
                continue
            
            # Process task
            success = self._process_task(task_file)
            
            if success:
                processed_ids.append(task_id)
        
        return processed_ids
    
    def _process_task(self, task_path: Path) -> bool:
        """
        Process a single task through the full loop
        
        Args:
            task_path: Path to task file
            
        Returns:
            True if task completed successfully
        """
        task_id = task_path.stem
        
        self.logger.logger.info(f"\n{'='*60}")
        self.logger.logger.info(f"  PROCESSING: {task_path.name}")
        self.logger.logger.info(f"{'='*60}")
        
        # Log task start
        self.logger.log_task_start(task_id, "unknown")
        
        try:
            # Step 1: Analyze task
            analysis = self.analyzer.analyze_task(task_path)
            
            if 'error' in analysis:
                self.logger.log_task_complete(task_id, False, analysis)
                return False
            
            task_type = analysis['task_type']
            actions = analysis['actions']
            parameters = analysis['parameters']
            
            self.logger.logger.info(f"[TASK] Type: {task_type}")
            self.logger.logger.info(f"[TASK] Actions: {', '.join(actions)}")
            self.logger.logger.info(f"[TASK] Priority: {analysis['priority']}/5")
            
            # Add task_path to parameters for move operations
            parameters['task_path'] = str(task_path)
            
            # Step 2: Execute actions
            all_success = True
            for action_str in actions:
                from ralph_wiggum_loop.core import TaskAction
                action = TaskAction(action_str)
                
                # Execute with retry
                result = self.error_handler.execute_with_retry(
                    task_id, 
                    action_str,
                    self.executor.execute,
                    task_id, action, parameters
                )
                
                if result.get('status') == 'success':
                    self.logger.logger.info(f"[OK] {action_str}: {result.get('message')}")
                elif result.get('status') == 'skipped':
                    self.logger.logger.info(f"[SKIP] {action_str}: {result.get('message')}")
                else:
                    self.logger.logger.error(f"[FAIL] {action_str}: {result.get('message')}")
                    all_success = False
                    
                    # Check if we can continue
                    if not self.error_handler.can_continue(result):
                        # Try fallback action
                        fallback = self.error_handler.get_fallback_action(action_str)
                        if fallback:
                            self.logger.logger.info(f"[FALLBACK] Trying: {fallback}")
                            fallback_action = TaskAction(fallback)
                            self.executor.execute(task_id, fallback_action, parameters)
                        break
            
            # Step 3: Log completion
            self.logger.log_task_complete(task_id, all_success, {
                'task_type': task_type,
                'actions_executed': actions,
                'priority': analysis['priority']
            })
            
            if all_success:
                self.logger.logger.info(f"[COMPLETE] Task {task_id} completed successfully")
            else:
                self.logger.logger.info(f"[PARTIAL] Task {task_id} completed with errors")
            
            return all_success
            
        except Exception as e:
            self.logger.log_task_complete(task_id, False, {'error': str(e)})
            self.logger.logger.error(f"[ERROR] Task {task_id} failed: {e}")
            return False
    
    def stop(self):
        """Stop the loop"""
        self.running = False
        self.logger.logger.info("[LOOP] Stop requested")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current loop status"""
        return {
            'running': self.running,
            'scan_interval': self.scan_interval,
            'folders': {
                'inbox': str(Config.INBOX),
                'needs_action': str(Config.NEEDS_ACTION),
                'done': str(Config.DONE)
            }
        }


# Singleton instance
_loop_instance: Optional[RalphWiggumLoop] = None


def get_loop() -> RalphWiggumLoop:
    """Get or create the Ralph Wiggum Loop instance"""
    global _loop_instance
    if _loop_instance is None:
        _loop_instance = RalphWiggumLoop()
    return _loop_instance


def run_single_task(task_path: Path) -> bool:
    """
    Run Ralph Wiggum Loop on a single task
    
    Args:
        task_path: Path to task file
        
    Returns:
        True if task completed successfully
    """
    loop = RalphWiggumLoop()
    return loop._process_task(task_path)
