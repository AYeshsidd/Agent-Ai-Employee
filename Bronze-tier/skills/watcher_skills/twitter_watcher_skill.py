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
        self.user_data_dir = Config.BASE_DIR / "credentials" / "twitter_profile"
        self._authenticated = False

    def authenticate(self) -> bool:
        """
        Authenticate with Twitter/X using Playwright with persistent browser profile

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            from playwright.sync_api import sync_playwright

            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "authenticate",
                "IN_PROGRESS", "Launching browser for Twitter/X"
            )

            # Close any existing browser
            if self.browser:
                try:
                    self.browser.close()
                except:
                    pass
                self.browser = None
                self.context = None
                self.page = None
                self._authenticated = False

            playwright = sync_playwright().start()

            # Create user data directory for persistent cookies
            self.user_data_dir.mkdir(exist_ok=True, parents=True)

            # Launch browser with persistent user data directory
            # This keeps you logged in across runs like a regular browser
            self.browser = playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir),
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--disable-background-networking',
                    '--disable-default-apps',
                    '--disable-extensions',
                    '--disable-sync',
                    '--no-first-run',
                ],
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                ignore_https_errors=True,
                java_script_enabled=True,
                bypass_csp=True,
            )

            # The persistent context IS the page context
            self.context = self.browser
            self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()

            # Navigate to Twitter
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "authenticate",
                "IN_PROGRESS", "Navigating to Twitter/X"
            )

            self.page.goto("https://twitter.com/home", wait_until="domcontentloaded", timeout=60000)
            self.page.wait_for_timeout(5000)

            # Check if logged in
            if self._check_if_logged_in():
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "authenticate",
                    "SUCCESS", "Already logged in (persistent profile)"
                )
                self._authenticated = True
                return True

            # Not logged in - guide user through login
            print("\n" + "=" * 70)
            print("  TWITTER/X LOGIN")
            print("=" * 70)
            print("\n  Browser window will open for Twitter/X login.")
            print("  Please complete the login process manually.")
            print("\n  Steps:")
            print("  1. Enter your email/phone/username")
            print("  2. Enter your password")
            print("  3. Complete 2FA if enabled")
            print("  4. Wait until you see your Twitter home timeline")
            print("\n  [INFO] Login credentials will be saved in browser profile")
            print("  [INFO] Future runs will auto-login using saved profile")
            print("=" * 70 + "\n")

            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "authenticate",
                "IN_PROGRESS", "Waiting for manual login completion"
            )

            # Wait for login with extended time
            login_success = self._wait_for_login_complete(300)  # 5 minutes

            if not login_success:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "authenticate",
                    "FAILED", "Login not completed within timeout"
                )
                print("\n[ERROR] Login timeout. Please try again.")
                return False

            # Successfully logged in
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "authenticate",
                "SUCCESS", "Twitter/X login complete - profile saved"
            )
            self._authenticated = True
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

    def _check_if_logged_in(self) -> bool:
        """
        Check if user is logged in by looking for authenticated UI elements

        Returns:
            True if logged in, False otherwise
        """
        try:
            if not self.page:
                return False

            # Multiple indicators of being logged in
            indicators = [
                # Sidebar navigation (only visible when logged in)
                lambda: self.page.query_selector('nav[role="navigation"]'),
                # Tweet composer
                lambda: self.page.query_selector('[data-testid="tweetTextarea_0"]'),
                # User avatar in sidebar
                lambda: self.page.query_selector('[data-testid="SideNav_Account"]'),
                # Home timeline
                lambda: self.page.query_selector('[data-testid="primaryColumn"]'),
                # Profile menu
                lambda: self.page.query_selector('[data-testid="app-bar-close"]'),
            ]

            # Check for at least 2 indicators
            found_count = 0
            for indicator in indicators:
                try:
                    element = indicator()
                    if element:
                        found_count += 1
                        if found_count >= 2:
                            return True
                except:
                    continue

            # Fallback: check URL
            current_url = self.page.url.lower()
            if any(x in current_url for x in ['home', 'timeline', 'compose']):
                return True

            return False

        except Exception:
            return False

    def _wait_for_login_complete(self, timeout_seconds: int = 300) -> bool:
        """
        Wait for user to complete login

        Args:
            timeout_seconds: Maximum time to wait

        Returns:
            True if login completed, False if timeout
        """
        start_time = time.time()
        check_interval = 5
        consecutive_success = 0
        required_successes = 3

        print("[INFO] Waiting for login completion...")
        print("[INFO] Checking every 5 seconds, need 3 consecutive successful checks\n")

        while (time.time() - start_time) < timeout_seconds:
            try:
                if self._check_if_logged_in():
                    consecutive_success += 1
                    remaining = int(timeout_seconds - (time.time() - start_time))

                    if consecutive_success >= required_successes:
                        print(f"[SUCCESS] Login confirmed! ({consecutive_success}/{required_successes})")
                        return True
                    else:
                        print(f"[INFO] Login detected, verifying... ({consecutive_success}/{required_successes}) - {remaining}s remaining")
                else:
                    if consecutive_success > 0:
                        print(f"[WARN] Login check failed, resetting counter")
                    consecutive_success = 0

                    elapsed = int(time.time() - start_time)
                    remaining = timeout_seconds - elapsed
                    if elapsed % 30 == 0 and elapsed > 0:
                        print(f"[INFO] Still waiting for login... ({remaining}s remaining)")
                        print("[INFO] Please complete login in the browser window")

            except Exception as e:
                consecutive_success = 0
                pass

            time.sleep(check_interval)

        print(f"\n[ERROR] Login timeout after {timeout_seconds} seconds")
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

        if not self._authenticated:
            if not self.authenticate():
                return 0

        if not self.page:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "watch",
                "FAILED", "No page available"
            )
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
            self.page.goto("https://twitter.com/notifications", wait_until="domcontentloaded")
            self.page.wait_for_timeout(5000)

            # Find notification articles
            notifications = self.page.query_selector_all('article[role="article"]')

            if not notifications:
                return 0

            tasks_created = 0
            for notif in notifications[:5]:
                try:
                    content = notif.inner_text()[:500]
                    if not content or len(content) < 10:
                        continue

                    notif_id = f"twitter_notif_{hash(content)}_{int(time.time())}"

                    if self.is_duplicate(notif_id):
                        continue

                    task_path = self.create_task_in_inbox(
                        title=f"Twitter Notification",
                        content=content,
                        source="Twitter",
                        metadata={
                            "Timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    )

                    if task_path:
                        self._save_processed_id(notif_id)
                        tasks_created += 1

                except:
                    continue

            return tasks_created

        except Exception as e:
            return 0

    def _check_dms(self) -> int:
        """Check for new direct messages"""
        try:
            self.page.goto("https://twitter.com/messages", wait_until="domcontentloaded")
            self.page.wait_for_timeout(5000)

            # Find message conversations
            conversations = self.page.query_selector_all('div[role="group"]')

            if not conversations:
                return 0

            tasks_created = 0
            for conv in conversations[:5]:
                try:
                    content = conv.inner_text()[:500]
                    if not content or len(content) < 10:
                        continue

                    dm_id = f"twitter_dm_{hash(content)}_{int(time.time())}"

                    if self.is_duplicate(dm_id):
                        continue

                    task_path = self.create_task_in_inbox(
                        title=f"Twitter DM",
                        content=content,
                        source="Twitter",
                        metadata={
                            "Timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    )

                    if task_path:
                        self._save_processed_id(dm_id)
                        tasks_created += 1

                except:
                    continue

            return tasks_created

        except Exception as e:
            return 0

    def close(self):
        """Close browser and cleanup"""
        if self.browser:
            try:
                # Don't close the persistent context immediately
                # Let it save cookies
                self.page = None
                self.context = None
                self._authenticated = False
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "close",
                    "SUCCESS", "Browser cleanup complete (profile saved)"
                )
            except Exception as e:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "close",
                    "FAILED", str(e)
                )
