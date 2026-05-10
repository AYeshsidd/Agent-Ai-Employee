#!/usr/bin/env python3
"""
Error Handler - Handles errors with retries and graceful degradation

Features:
- Configurable retry attempts
- Exponential backoff
- Error categorization
- Graceful degradation for non-critical failures
"""
import time
from typing import Dict, Any, Callable, Optional
from enum import Enum
import sys
from pathlib import Path

# Ensure project root is in sys.path
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from ralph_wiggum_loop.core import get_loop_logger


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"           # Can be ignored or retried later
    MEDIUM = "medium"     # Should be retried
    HIGH = "high"         # Critical, stop execution
    RECOVERABLE = "recoverable"  # Can continue with degraded functionality


class ErrorHandler:
    """Handles errors with retries and graceful degradation"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.logger = get_loop_logger()
        
        # Error patterns and their severities
        self.error_patterns = {
            'connection': ErrorSeverity.MEDIUM,
            'timeout': ErrorSeverity.MEDIUM,
            'authentication': ErrorSeverity.HIGH,
            'permission': ErrorSeverity.HIGH,
            'not found': ErrorSeverity.HIGH,
            'invalid': ErrorSeverity.MEDIUM,
            'rate limit': ErrorSeverity.MEDIUM,
        }
    
    def execute_with_retry(self, task_id: str, operation: str, 
                          func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute function with retry logic
        
        Args:
            task_id: Task identifier
            operation: Operation name for logging
            func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            Function result or error dict
        """
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.log_step(task_id, f"RETRY_{operation}", 
                                   f"ATTEMPT_{attempt}",
                                   {"max_retries": self.max_retries})
                
                result = func(*args, **kwargs)
                
                # Check if result indicates failure
                if isinstance(result, dict) and result.get('status') == 'failed':
                    error_msg = result.get('message', 'Unknown error')
                    severity = self._categorize_error(error_msg)
                    
                    if severity == ErrorSeverity.HIGH:
                        self.logger.log_step(task_id, f"RETRY_{operation}", 
                                           "STOPPED", 
                                           error=f"High severity error: {error_msg}")
                        return result
                    
                    if severity == ErrorSeverity.RECOVERABLE:
                        return result
                    
                    last_error = error_msg
                    
                    if attempt < self.max_retries:
                        delay = self._calculate_delay(attempt)
                        self.logger.log_step(task_id, f"RETRY_{operation}", 
                                           f"WAITING_{delay}s",
                                           error=error_msg)
                        time.sleep(delay)
                        continue
                    
                    return result
                else:
                    return result
                    
            except Exception as e:
                last_error = str(e)
                severity = self._categorize_error(last_error)
                
                if severity == ErrorSeverity.HIGH:
                    self.logger.log_step(task_id, f"RETRY_{operation}", 
                                       "STOPPED", 
                                       error=f"High severity error: {last_error}")
                    return {'status': 'failed', 'message': last_error}
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    self.logger.log_step(task_id, f"RETRY_{operation}", 
                                       f"WAITING_{delay}s",
                                       error=last_error)
                    time.sleep(delay)
                else:
                    self.logger.log_step(task_id, f"RETRY_{operation}", 
                                       "EXHAUSTED",
                                       error=last_error)
                    return {'status': 'failed', 'message': last_error}
        
        return {'status': 'failed', 'message': last_error or 'Unknown error'}
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        return self.base_delay * (2 ** (attempt - 1))
    
    def _categorize_error(self, error_msg: str) -> ErrorSeverity:
        """Categorize error by severity"""
        error_lower = error_msg.lower()
        
        for pattern, severity in self.error_patterns.items():
            if pattern in error_lower:
                return severity
        
        # Default severity
        return ErrorSeverity.MEDIUM
    
    def can_continue(self, result: Dict) -> bool:
        """Check if execution can continue after this result"""
        if result.get('status') == 'success':
            return True
        
        message = result.get('message', '').lower()
        
        # These errors allow continuation
        recoverable_patterns = ['skipped', 'optional', 'non-critical']
        
        return any(p in message for p in recoverable_patterns)
    
    def get_fallback_action(self, failed_action: str) -> Optional[str]:
        """Get fallback action for failed action"""
        fallbacks = {
            'post_twitter': 'move_to_done',
            'post_facebook': 'move_to_done',
            'post_linkedin': 'move_to_done',
            'create_invoice': 'move_to_needs_action',
            'register_payment': 'move_to_needs_action',
            'send_email': 'move_to_needs_action',
        }
        return fallbacks.get(failed_action)
