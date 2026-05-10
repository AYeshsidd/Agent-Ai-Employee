from pathlib import Path
from typing import Dict, List, Optional
import sys
# Ensure project root is in sys.path
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from skills.watcher_skills.base_watcher_skill import BaseWatcherSkill
from bronze_logger import BronzeLogger
from config import Config


class LinkedInWatcherSkill(BaseWatcherSkill):
    """Agent skill for watching LinkedIn messages and notifications"""

    def __init__(self):
        super().__init__("LinkedIn")
        self.browser = None
        self.context = None
        self.page = None
        self.session_file = Config.BASE_DIR / "credentials" / "linkedin_session.json"

    def authenticate(self) -> bool:
        """
        Authenticate with LinkedIn using Playwright

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            from playwright.sync_api import sync_playwright

            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInWatcherSkill", "authenticate",
                "IN_PROGRESS", "Launching browser"
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
            self.page.goto("https://www.linkedin.com/messaging/")

            # Check if already logged in
            self.page.wait_for_timeout(3000)

            if "feed" in self.page.url or "messaging" in self.page.url:
                # Already logged in, save session
                self.session_file.parent.mkdir(exist_ok=True)
                self.context.storage_state(path=str(self.session_file))

                BronzeLogger.log_skill_execution(
                    self.logger, "LinkedInWatcherSkill", "authenticate",
                    "SUCCESS", "LinkedIn authenticated (existing session)"
                )
                return True

            # Need to login
            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInWatcherSkill", "authenticate",
                "IN_PROGRESS", "Manual login required - please login in browser"
            )

            # Wait for user to login manually
            self.page.wait_for_url("**/feed/**", timeout=120000)

            # Save session
            self.session_file.parent.mkdir(exist_ok=True)
            self.context.storage_state(path=str(self.session_file))

            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInWatcherSkill", "authenticate",
                "SUCCESS", "LinkedIn authenticated (new session)"
            )
            return True

        except ImportError as e:
            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInWatcherSkill", "authenticate",
                "FAILED", f"Playwright not installed: {str(e)}"
            )
            return False
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInWatcherSkill", "authenticate",
                "FAILED", str(e)
            )
            return False

    def watch(self) -> int:
        """
        Watch LinkedIn for new messages and notifications

        Returns:
            Number of new tasks created
        """
        BronzeLogger.log_skill_execution(
            self.logger, "LinkedInWatcherSkill", "watch",
            "IN_PROGRESS", "Checking LinkedIn messages"
        )

        if not self.page:
            if not self.authenticate():
                return 0

        try:
            # Navigate to messaging
            self.page.goto("https://www.linkedin.com/messaging/")
            self.page.wait_for_timeout(3000)

            # Get unread message conversations
            unread_conversations = self.page.query_selector_all(
                '[class*="msg-conversation-card"][class*="unread"]'
            )

            if not unread_conversations:
                BronzeLogger.log_skill_execution(
                    self.logger, "LinkedInWatcherSkill", "watch",
                    "SUCCESS", "No unread messages found"
                )
                return 0

            tasks_created = 0

            for conversation in unread_conversations[:10]:  # Limit to 10
                try:
                    # Extract conversation details
                    conversation_data = self._extract_conversation_data(conversation)

                    if not conversation_data:
                        continue

                    # Generate unique ID
                    conversation_id = f"linkedin_{conversation_data['sender']}_{conversation_data['timestamp']}"

                    # Check for duplicates
                    if self.is_duplicate(conversation_id):
                        continue

                    # Create task
                    task_path = self.create_task_in_inbox(
                        title=f"LinkedIn Message: {conversation_data['sender']}",
                        content=conversation_data['preview'],
                        source="LinkedIn",
                        metadata={
                            "Sender": conversation_data['sender'],
                            "Timestamp": conversation_data['timestamp']
                        }
                    )

                    if task_path:
                        self._save_processed_id(conversation_id)
                        tasks_created += 1

                except Exception as e:
                    BronzeLogger.log_skill_execution(
                        self.logger, "LinkedInWatcherSkill", "watch",
                        "FAILED", f"Error processing conversation: {str(e)}"
                    )
                    continue

            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInWatcherSkill", "watch",
                "SUCCESS", f"Created {tasks_created} tasks from LinkedIn messages"
            )

            return tasks_created

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInWatcherSkill", "watch",
                "FAILED", str(e)
            )
            return 0

    def _extract_conversation_data(self, conversation_element) -> Optional[Dict[str, str]]:
        """Extract data from LinkedIn conversation element"""
        try:
            # Extract sender name
            sender_elem = conversation_element.query_selector('[class*="msg-conversation-card__participant-names"]')
            sender = sender_elem.inner_text() if sender_elem else "Unknown"

            # Extract message preview
            preview_elem = conversation_element.query_selector('[class*="msg-conversation-card__message-snippet"]')
            preview = preview_elem.inner_text() if preview_elem else "No preview available"

            # Extract timestamp
            time_elem = conversation_element.query_selector('[class*="msg-conversation-card__time-stamp"]')
            timestamp = time_elem.inner_text() if time_elem else "Unknown"

            return {
                'sender': sender.strip(),
                'preview': preview.strip(),
                'timestamp': timestamp.strip()
            }

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInWatcherSkill", "_extract_conversation_data",
                "FAILED", str(e)
            )
            return None

    def close(self):
        """Close browser and cleanup"""
        if self.browser:
            self.browser.close()
            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInWatcherSkill", "close",
                "SUCCESS", "Browser closed"
            )
