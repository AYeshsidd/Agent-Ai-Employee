from pathlib import Path
from typing import Dict, List, Optional
import sys
import time
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from skills.watcher_skills.base_watcher_skill import BaseWatcherSkill
from bronze_logger import BronzeLogger
from config import Config


class TwitterWatcherSkill(BaseWatcherSkill):
    """Agent skill for watching Twitter/X notifications and DMs"""

    def __init__(self):
        super().__init__("Twitter")
        self.browser = None
        self.context = None
        self.page = None
        self.session_file = Config.BASE_DIR / "credentials" / "twitter_session.json"

    def authenticate(self) -> bool:
        """
        Authenticate with Twitter/X using Playwright

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            from playwright.sync_api import sync_playwright

            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "authenticate",
                "IN_PROGRESS", "Launching browser for Twitter"
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
            self.page.goto("https://twitter.com/home")

            # Wait for page to load
            self.page.wait_for_timeout(5000)

            # Check if already logged in
            if "home" in self.page.url or "timeline" in self.page.url:
                # Already logged in, save session
                self.session_file.parent.mkdir(exist_ok=True)
                self.context.storage_state(path=str(self.session_file))

                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "authenticate",
                    "SUCCESS", "Twitter authenticated (existing session)"
                )
                return True

            # Need to login
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "authenticate",
                "IN_PROGRESS", "Manual login required - please login in browser"
            )

            # Wait for user to login manually (2 minutes timeout)
            try:
                self.page.wait_for_url("**/home**", timeout=120000)
            except:
                # Check if we're on timeline even if URL doesn't match exactly
                pass

            # Save session
            self.session_file.parent.mkdir(exist_ok=True)
            try:
                self.context.storage_state(path=str(self.session_file))
            except:
                pass  # Session might not be ready yet

            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "authenticate",
                "SUCCESS", "Twitter authenticated (new session)"
            )
            return True

        except ImportError as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "authenticate",
                "FAILED", f"Playwright not installed: {str(e)}"
            )
            return False
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "authenticate",
                "FAILED", str(e)
            )
            return False

    def watch(self) -> int:
        """
        Watch Twitter for new notifications and DMs

        Returns:
            Number of new tasks created
        """
        BronzeLogger.log_skill_execution(
            self.logger, "TwitterWatcherSkill", "watch",
            "IN_PROGRESS", "Checking Twitter notifications and DMs"
        )

        if not self.page:
            if not self.authenticate():
                return 0

        try:
            tasks_created = 0

            # Check notifications
            tasks_created += self._check_notifications()

            # Check DMs
            tasks_created += self._check_dms()

            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "watch",
                "SUCCESS", f"Created {tasks_created} tasks from Twitter"
            )

            return tasks_created

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "watch",
                "FAILED", str(e)
            )
            return 0

    def _check_notifications(self) -> int:
        """Check for new notifications"""
        try:
            # Navigate to notifications
            self.page.goto("https://twitter.com/notifications")
            self.page.wait_for_timeout(3000)

            # Look for unread notifications (various selectors for different notification types)
            notification_selectors = [
                '[data-testid="notification"]',
                'article[role="article"]',
                '[data-testid="primaryColumn"] article'
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
                    notif_id = f"twitter_notif_{notif_data.get('content', '')[:20]}_{int(time.time())}"

                    # Check for duplicates
                    if self.is_duplicate(notif_id):
                        continue

                    # Create task
                    task_path = self.create_task_in_inbox(
                        title=f"Twitter Notification: {notif_data.get('type', 'Unknown')}",
                        content=notif_data.get('content', 'No content'),
                        source="Twitter",
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

    def _check_dms(self) -> int:
        """Check for new direct messages"""
        try:
            # Navigate to messages
            self.page.goto("https://twitter.com/messages")
            self.page.wait_for_timeout(3000)

            # Look for conversations with unread messages
            conversation_selectors = [
                '[data-testid="DMDrawer"]',
                '[role="group"]',
                'div[role="group"]'
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
                    conv_data = self._extract_dm_data(conv)
                    if not conv_data:
                        continue

                    # Generate unique ID
                    dm_id = f"twitter_dm_{conv_data.get('from', '')}_{int(time.time())}"

                    # Check for duplicates
                    if self.is_duplicate(dm_id):
                        continue

                    # Create task
                    task_path = self.create_task_in_inbox(
                        title=f"Twitter DM: {conv_data.get('from', 'Unknown')}",
                        content=conv_data.get('message', 'No message'),
                        source="Twitter",
                        metadata={
                            "From": conv_data.get('from', 'Unknown'),
                            "Timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    )

                    if task_path:
                        self._save_processed_id(dm_id)
                        tasks_created += 1

                except Exception as e:
                    continue

            return tasks_created

        except Exception as e:
            return 0

    def _extract_notification_data(self, notif_element) -> Optional[Dict[str, str]]:
        """Extract data from Twitter notification element"""
        try:
            # Try to extract notification type and content
            content_elem = notif_element.query_selector('[data-testid="notificationText"]')
            content = content_elem.inner_text() if content_elem else ""

            # Extract username if available
            user_elem = notif_element.query_selector('[data-testid="User-Name"]')
            from_user = user_elem.inner_text() if user_elem else "Unknown"

            # Determine notification type
            notif_type = "General"
            if "liked" in content.lower():
                notif_type = "Like"
            elif "retweeted" in content.lower() or "reposted" in content.lower():
                notif_type = "Retweet/Repost"
            elif "followed" in content.lower():
                notif_type = "Follow"
            elif "mentioned" in content.lower():
                notif_type = "Mention"

            return {
                'type': notif_type,
                'content': content.strip()[:500],
                'from': from_user.strip()
            }

        except Exception as e:
            return None

    def _extract_dm_data(self, conv_element) -> Optional[Dict[str, str]]:
        """Extract data from Twitter DM conversation element"""
        try:
            # Extract sender name
            name_elem = conv_element.query_selector('[data-testid="User-Name"]')
            from_user = name_elem.inner_text() if name_elem else "Unknown"

            # Extract message preview
            message_elem = conv_element.query_selector('span[dir="auto"]')
            message = message_elem.inner_text() if message_elem else "No preview available"

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
                self.logger, "TwitterWatcherSkill", "close",
                "SUCCESS", "Browser closed"
            )
