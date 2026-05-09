from pathlib import Path
from typing import Dict, List, Optional
import sys
import time
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from skills.watcher_skills.base_watcher_skill import BaseWatcherSkill
from bronze_logger import BronzeLogger
from config import Config


class FacebookWatcherSkill(BaseWatcherSkill):
    """Agent skill for watching Facebook notifications and messages"""

    def __init__(self):
        super().__init__("Facebook")
        self.browser = None
        self.context = None
        self.page = None
        self.session_file = Config.BASE_DIR / "credentials" / "facebook_session.json"

    def authenticate(self) -> bool:
        """
        Authenticate with Facebook using Playwright

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            from playwright.sync_api import sync_playwright

            BronzeLogger.log_skill_execution(
                self.logger, "FacebookWatcherSkill", "authenticate",
                "IN_PROGRESS", "Launching browser for Facebook"
            )

            playwright = sync_playwright().start()
            self.browser = playwright.chromium.launch(headless=False)

            # Load existing session if available
            if self.session_file.exists():
                self.context = self.browser.new_context(
                    storage_state=str(self.session_file)
                )
            else:
                self.context = self.browser.new_context()

            self.page = self.context.new_page()
            self.page.goto("https://www.facebook.com/")

            # Wait for page to load
            self.page.wait_for_timeout(5000)

            # Check if already logged in
            if "feed" in self.page.url or "facebook.com/home" in self.page.url:
                # Already logged in, save session
                self.session_file.parent.mkdir(exist_ok=True)
                self.context.storage_state(path=str(self.session_file))

                BronzeLogger.log_skill_execution(
                    self.logger, "FacebookWatcherSkill", "authenticate",
                    "SUCCESS", "Facebook authenticated (existing session)"
                )
                return True

            # Need to login
            BronzeLogger.log_skill_execution(
                self.logger, "FacebookWatcherSkill", "authenticate",
                "IN_PROGRESS", "Manual login required - please login in browser"
            )

            # Wait for user to login manually (2 minutes timeout)
            try:
                self.page.wait_for_url("**/feed**", timeout=120000)
            except:
                pass

            # Save session
            self.session_file.parent.mkdir(exist_ok=True)
            try:
                self.context.storage_state(path=str(self.session_file))
            except:
                pass

            BronzeLogger.log_skill_execution(
                self.logger, "FacebookWatcherSkill", "authenticate",
                "SUCCESS", "Facebook authenticated (new session)"
            )
            return True

        except ImportError as e:
            BronzeLogger.log_skill_execution(
                self.logger, "FacebookWatcherSkill", "authenticate",
                "FAILED", f"Playwright not installed: {str(e)}"
            )
            return False
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "FacebookWatcherSkill", "authenticate",
                "FAILED", str(e)
            )
            return False

    def watch(self) -> int:
        """
        Watch Facebook for new notifications and messages

        Returns:
            Number of new tasks created
        """
        BronzeLogger.log_skill_execution(
            self.logger, "FacebookWatcherSkill", "watch",
            "IN_PROGRESS", "Checking Facebook notifications and messages"
        )

        if not self.page:
            if not self.authenticate():
                return 0

        try:
            tasks_created = 0

            # Check notifications
            tasks_created += self._check_notifications()

            # Check Messenger
            tasks_created += self._check_messages()

            BronzeLogger.log_skill_execution(
                self.logger, "FacebookWatcherSkill", "watch",
                "SUCCESS", f"Created {tasks_created} tasks from Facebook"
            )

            return tasks_created

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "FacebookWatcherSkill", "watch",
                "FAILED", str(e)
            )
            return 0

    def _check_notifications(self) -> int:
        """Check for new notifications"""
        try:
            # Navigate to notifications
            self.page.goto("https://www.facebook.com/notifications")
            self.page.wait_for_timeout(3000)

            # Look for unread notifications
            notification_selectors = [
                '[role="article"]',
                'div[role="article"]',
                '[data-testid="notification"]'
            ]

            notifications = []
            for selector in notification_selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    if elements:
                        notifications = elements
                        break
                except:
                    continue

            if not notifications:
                return 0

            tasks_created = 0
            for notif in notifications[:5]:  # Limit to 5
                try:
                    notif_data = self._extract_notification_data(notif)
                    if not notif_data:
                        continue

                    # Generate unique ID
                    notif_id = f"fb_notif_{notif_data.get('content', '')[:20]}_{int(time.time())}"

                    # Check for duplicates
                    if self.is_duplicate(notif_id):
                        continue

                    # Create task
                    task_path = self.create_task_in_inbox(
                        title=f"Facebook Notification: {notif_data.get('type', 'Unknown')}",
                        content=notif_data.get('content', 'No content'),
                        source="Facebook",
                        metadata={
                            "Type": notif_data.get('type', 'Unknown'),
                            "From": notif_data.get('from', 'Unknown'),
                            "Timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    )

                    if task_path:
                        self._save_processed_id(notif_id)
                        tasks_created += 1

                except Exception as e:
                    continue

            return tasks_created

        except Exception as e:
            return 0

    def _check_messages(self) -> int:
        """Check for new Messenger messages"""
        try:
            # Navigate to Messenger
            self.page.goto("https://www.facebook.com/messages")
            self.page.wait_for_timeout(3000)

            # Look for conversations with unread messages
            conversation_selectors = [
                '[role="row"]',
                'div[role="row"]',
                '[class*="conversation"]'
            ]

            conversations = []
            for selector in conversation_selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    if elements:
                        conversations = elements
                        break
                except:
                    continue

            if not conversations:
                return 0

            tasks_created = 0
            for conv in conversations[:5]:  # Limit to 5
                try:
                    conv_data = self._extract_message_data(conv)
                    if not conv_data:
                        continue

                    # Generate unique ID
                    msg_id = f"fb_msg_{conv_data.get('from', '')}_{int(time.time())}"

                    # Check for duplicates
                    if self.is_duplicate(msg_id):
                        continue

                    # Create task
                    task_path = self.create_task_in_inbox(
                        title=f"Facebook Message: {conv_data.get('from', 'Unknown')}",
                        content=conv_data.get('message', 'No message'),
                        source="Facebook",
                        metadata={
                            "From": conv_data.get('from', 'Unknown'),
                            "Timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    )

                    if task_path:
                        self._save_processed_id(msg_id)
                        tasks_created += 1

                except Exception as e:
                    continue

            return tasks_created

        except Exception as e:
            return 0

    def _extract_notification_data(self, notif_element) -> Optional[Dict[str, str]]:
        """Extract data from Facebook notification element"""
        try:
            # Extract content
            content_elem = notif_element.query_selector('span[dir="auto"]')
            content = content_elem.inner_text() if content_elem else ""

            # Extract username if available
            user_elem = notif_element.query_selector('[data-tooltip-content*="User"]')
            from_user = user_elem.inner_text() if user_elem else "Unknown"

            # Determine notification type
            notif_type = "General"
            content_lower = content.lower()
            if "liked" in content_lower:
                notif_type = "Like"
            elif "shared" in content_lower:
                notif_type = "Share"
            elif "commented" in content_lower:
                notif_type = "Comment"
            elif "posted" in content_lower:
                notif_type = "Post"
            elif "friend" in content_lower:
                notif_type = "Friend Request"

            return {
                'type': notif_type,
                'content': content.strip()[:500],
                'from': from_user.strip()
            }

        except Exception as e:
            return None

    def _extract_message_data(self, conv_element) -> Optional[Dict[str, str]]:
        """Extract data from Facebook Messenger conversation element"""
        try:
            # Extract sender name
            name_elem = conv_element.query_selector('span[dir="auto"]')
            from_user = name_elem.inner_text() if name_elem else "Unknown"

            # Extract message preview (try multiple selectors)
            message = "No preview available"
            message_selectors = [
                'span[dir="auto"]',
                '[class*="message"]',
                'span[dir="auto"]:last-child'
            ]
            
            for selector in message_selectors:
                try:
                    message_elem = conv_element.query_selector(selector)
                    if message_elem:
                        message = message_elem.inner_text()
                        if message and len(message) > 3:
                            break
                except:
                    continue

            return {
                'from': from_user.strip(),
                'message': message.strip()[:500]
            }

        except Exception as e:
            return None

    def close(self):
        """Close browser and cleanup"""
        if self.browser:
            self.browser.close()
            BronzeLogger.log_skill_execution(
                self.logger, "FacebookWatcherSkill", "close",
                "SUCCESS", "Browser closed"
            )
