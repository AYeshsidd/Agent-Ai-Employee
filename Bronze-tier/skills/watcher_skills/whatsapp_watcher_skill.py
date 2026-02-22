from pathlib import Path
from typing import Dict, List, Optional
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from skills.watcher_skills.base_watcher_skill import BaseWatcherSkill
from bronze_logger import BronzeLogger
from config import Config


class WhatsAppWatcherSkill(BaseWatcherSkill):
    """Agent skill for watching WhatsApp Web messages"""

    def __init__(self):
        super().__init__("WhatsApp")
        self.browser = None
        self.context = None
        self.page = None
        self.session_file = Config.BASE_DIR / "credentials" / "whatsapp_session.json"

    def authenticate(self) -> bool:
        """
        Authenticate with WhatsApp Web using Playwright

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            from playwright.sync_api import sync_playwright

            BronzeLogger.log_skill_execution(
                self.logger, "WhatsAppWatcherSkill", "authenticate",
                "IN_PROGRESS", "Launching browser for WhatsApp Web"
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
            self.page.goto("https://web.whatsapp.com/")

            # Wait for either QR code or chat list
            try:
                # Check if already logged in (chat list appears)
                self.page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)

                # Save session
                self.session_file.parent.mkdir(exist_ok=True)
                self.context.storage_state(path=str(self.session_file))

                BronzeLogger.log_skill_execution(
                    self.logger, "WhatsAppWatcherSkill", "authenticate",
                    "SUCCESS", "WhatsApp Web authenticated (existing session)"
                )
                return True

            except:
                # Need to scan QR code
                BronzeLogger.log_skill_execution(
                    self.logger, "WhatsAppWatcherSkill", "authenticate",
                    "IN_PROGRESS", "Please scan QR code in browser"
                )

                # Wait for QR code scan (chat list appears after successful scan)
                self.page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)

                # Save session
                self.session_file.parent.mkdir(exist_ok=True)
                self.context.storage_state(path=str(self.session_file))

                BronzeLogger.log_skill_execution(
                    self.logger, "WhatsAppWatcherSkill", "authenticate",
                    "SUCCESS", "WhatsApp Web authenticated (new session)"
                )
                return True

        except ImportError as e:
            BronzeLogger.log_skill_execution(
                self.logger, "WhatsAppWatcherSkill", "authenticate",
                "FAILED", f"Playwright not installed: {str(e)}"
            )
            return False
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "WhatsAppWatcherSkill", "authenticate",
                "FAILED", str(e)
            )
            return False

    def watch(self) -> int:
        """
        Watch WhatsApp Web for unread messages

        Returns:
            Number of new tasks created
        """
        BronzeLogger.log_skill_execution(
            self.logger, "WhatsAppWatcherSkill", "watch",
            "IN_PROGRESS", "Checking WhatsApp messages"
        )

        if not self.page:
            if not self.authenticate():
                return 0

        try:
            # Wait for chat list to load
            self.page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)
            self.page.wait_for_timeout(2000)

            # Get unread chats (chats with unread badge)
            unread_chats = self.page.query_selector_all(
                '[data-testid="cell-frame-container"]:has([data-testid="icon-unread-count"])'
            )

            if not unread_chats:
                BronzeLogger.log_skill_execution(
                    self.logger, "WhatsAppWatcherSkill", "watch",
                    "SUCCESS", "No unread messages found"
                )
                return 0

            tasks_created = 0

            for chat in unread_chats[:10]:  # Limit to 10
                try:
                    # Extract chat details
                    chat_data = self._extract_chat_data(chat)

                    if not chat_data:
                        continue

                    # Generate unique ID
                    chat_id = f"whatsapp_{chat_data['contact']}_{chat_data['timestamp']}"

                    # Check for duplicates
                    if self.is_duplicate(chat_id):
                        continue

                    # Create task
                    task_path = self.create_task_in_inbox(
                        title=f"WhatsApp Message: {chat_data['contact']}",
                        content=chat_data['message'],
                        source="WhatsApp",
                        metadata={
                            "Contact": chat_data['contact'],
                            "Unread Count": chat_data['unread_count'],
                            "Timestamp": chat_data['timestamp']
                        }
                    )

                    if task_path:
                        self._save_processed_id(chat_id)
                        tasks_created += 1

                except Exception as e:
                    BronzeLogger.log_skill_execution(
                        self.logger, "WhatsAppWatcherSkill", "watch",
                        "FAILED", f"Error processing chat: {str(e)}"
                    )
                    continue

            BronzeLogger.log_skill_execution(
                self.logger, "WhatsAppWatcherSkill", "watch",
                "SUCCESS", f"Created {tasks_created} tasks from WhatsApp messages"
            )

            return tasks_created

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "WhatsAppWatcherSkill", "watch",
                "FAILED", str(e)
            )
            return 0

    def _extract_chat_data(self, chat_element) -> Optional[Dict[str, str]]:
        """Extract data from WhatsApp chat element"""
        try:
            # Extract contact name
            contact_elem = chat_element.query_selector('[data-testid="cell-frame-title"]')
            contact = contact_elem.inner_text() if contact_elem else "Unknown"

            # Extract last message
            message_elem = chat_element.query_selector('[data-testid="last-msg-text"]')
            message = message_elem.inner_text() if message_elem else "No message preview"

            # Extract unread count
            unread_elem = chat_element.query_selector('[data-testid="icon-unread-count"]')
            unread_count = unread_elem.inner_text() if unread_elem else "1"

            # Extract timestamp
            time_elem = chat_element.query_selector('[data-testid="cell-frame-secondary"] span')
            timestamp = time_elem.inner_text() if time_elem else "Unknown"

            return {
                'contact': contact.strip(),
                'message': message.strip(),
                'unread_count': unread_count.strip(),
                'timestamp': timestamp.strip()
            }

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "WhatsAppWatcherSkill", "_extract_chat_data",
                "FAILED", str(e)
            )
            return None

    def close(self):
        """Close browser and cleanup"""
        if self.browser:
            self.browser.close()
            BronzeLogger.log_skill_execution(
                self.logger, "WhatsAppWatcherSkill", "close",
                "SUCCESS", "Browser closed"
            )
