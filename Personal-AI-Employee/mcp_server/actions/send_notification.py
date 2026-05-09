#!/usr/bin/env python3
"""Send Notification Action - MCP Server"""
from pathlib import Path
from typing import Dict
from datetime import datetime
import sys

# Add Bronze-tier to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import Config


class SendNotificationAction:
    """Action to send notifications (console + log file)"""

    def __init__(self):
        self.log_file = Config.LOGS_DIR / "notifications.log"
        self.log_file.parent.mkdir(exist_ok=True)

    def execute(self, params: Dict[str, str]) -> Dict[str, str]:
        """
        Send notification (print to console and log to file)

        Args:
            params: Dictionary with 'title' and 'message'

        Returns:
            Dictionary with 'status' and 'message'
        """
        # Validate input
        if not params.get('title'):
            return {"status": "failed", "message": "Missing 'title' field"}

        if not params.get('message'):
            return {"status": "failed", "message": "Missing 'message' field"}

        try:
            title = params['title']
            message = params['message']
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Format notification
            notification = f"""
{'=' * 70}
NOTIFICATION: {title}
Time: {timestamp}
{'=' * 70}
{message}
{'=' * 70}
"""

            # Print to console
            print(notification)

            # Log to file
            log_entry = f"[{timestamp}] {title}: {message}\n"
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)

            return {
                "status": "success",
                "message": f"Notification sent: {title}"
            }

        except Exception as e:
            return {
                "status": "failed",
                "message": f"Failed to send notification: {str(e)}"
            }


if __name__ == "__main__":
    # Quick test
    action = SendNotificationAction()
    result = action.execute({
        "title": "Test Notification",
        "message": "This is a test notification from MCP Server"
    })
    print(f"Result: {result}")
