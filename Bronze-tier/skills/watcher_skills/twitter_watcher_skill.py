from pathlib import Path
from typing import Dict, List, Optional
import sys
import time
import json
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
        self._authenticated = False
        self._playwright = None

    def authenticate(self) -> bool:
        """
        Authenticate with Twitter/X using Playwright.
        
        Flow:
        1. Check if twitter_session.json exists
        2. If exists, try to load session and skip login
        3. If not exists or invalid, open browser for manual login
        4. After login, save session to twitter_session.json
        5. Browser stays open until login completes
        """
        try:
            from playwright.sync_api import sync_playwright

            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "authenticate",
                "IN_PROGRESS", "Starting Twitter/X authentication"
            )

            # Close any existing browser first
            self._cleanup_browser()

            # Start Playwright
            self._playwright = sync_playwright().start()

            # Check if session file exists
            has_session = self.session_file.exists()
            
            if has_session:
                print("\n[INFO] Found existing session file")
                print(f"       {self.session_file}")
                
                # Try to load and use existing session
                session_success = self._authenticate_with_session()
                
                if session_success:
                    print("\n[OK] Logged in using saved session!")
                    BronzeLogger.log_skill_execution(
                        self.logger, "TwitterWatcherSkill", "authenticate",
                        "SUCCESS", "Authenticated with saved session"
                    )
                    self._authenticated = True
                    return True
                else:
                    print("\n[INFO] Saved session expired or invalid")
                    print("[INFO] Will perform fresh login\n")

            # No session or session expired - need fresh login
            print("\n" + "=" * 70)
            print("  TWITTER/X LOGIN REQUIRED")
            print("=" * 70)
            print("\n[INFO] Opening browser for login...")
            print("[INFO] Browser will stay open until you complete login")
            print("[INFO] DO NOT close the browser window\n")

            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "authenticate",
                "IN_PROGRESS", "Launching browser for manual login"
            )

            # Launch browser WITHOUT persistent context (we'll save session manually)
            self.browser = self._playwright.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=TranslateUI',
                ]
            )

            # Create new context
            self.context = self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            self.page = self.context.new_page()

            # Navigate to Twitter login
            print("[INFO] Navigating to Twitter/X login page...")
            self.page.goto("https://twitter.com/i/flow/login", wait_until="domcontentloaded", timeout=60000)
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(5000)

            # Check if somehow already logged in
            if self._check_if_logged_in():
                print("\n[OK] Already logged in!")
                self._save_session()
                self._authenticated = True
                return True

            # Guide user through login
            print("\n" + "=" * 70)
            print("  PLEASE LOG IN TO TWITTER/X")
            print("=" * 70)
            print("\n  Browser window is open with Twitter login page.")
            print("\n  Steps:")
            print("  1. Enter your email/phone/username")
            print("  2. Enter your password")
            print("  3. Complete 2FA if enabled")
            print("  4. Wait for home timeline to load")
            print("\n  IMPORTANT:")
            print("  - Browser will stay open - DO NOT close it")
            print("  - Script will auto-detect when login completes")
            print("  - Session will be saved for future runs")
            print("=" * 70 + "\n")

            # Wait for login (browser stays open)
            login_success = self._wait_for_login_complete(600)  # 10 minutes

            if not login_success:
                print("\n" + "=" * 70)
                print("  LOGIN NOT COMPLETED")
                print("=" * 70)
                print("\n[WARN] Login was not detected within 10 minutes.")
                print("[INFO] Browser is still open - you can continue logging in.")
                print("[INFO] Close browser when done, or continue in this window.")
                print("=" * 70 + "\n")
                
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "authenticate",
                    "FAILED", "Login timeout (browser still open)"
                )
                
                # Keep browser open for user
                self.page = None
                self.context = None
                self._authenticated = False
                return False

            # Successfully logged in!
            print("\n" + "=" * 70)
            print("  LOGIN SUCCESSFUL!")
            print("=" * 70)
            print("\n[OK] Twitter/X authentication complete")
            
            # Save session for future runs
            self._save_session()
            
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "authenticate",
                "SUCCESS", "Login complete - session saved"
            )
            
            self._authenticated = True
            return True

        except ImportError as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "authenticate",
                "FAILED", f"Playwright not installed: {str(e)}"
            )
            print("\n[ERROR] Playwright not installed")
            print("[INFO] Run: playwright install chromium")
            return False
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "authenticate",
                "FAILED", str(e)
            )
            print(f"\n[ERROR] Authentication failed: {str(e)}")
            return False

    def _authenticate_with_session(self) -> bool:
        """
        Try to authenticate using saved session file.
        
        Returns:
            True if session is valid and logged in, False otherwise
        """
        try:
            from playwright.sync_api import sync_playwright
            
            # Load session from JSON
            with open(self.session_file, 'r', encoding='utf-8') as f:
                storage_state = json.load(f)
            
            print("[INFO] Loading saved session...")
            
            # Launch browser
            self.browser = self._playwright.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Create context with saved storage state (cookies, localStorage)
            self.context = self.browser.new_context(
                storage_state=storage_state,
                viewport={'width': 1280, 'height': 720}
            )
            
            self.page = self.context.new_page()
            
            # Navigate to Twitter
            print("[INFO] Navigating to Twitter with saved session...")
            self.page.goto("https://twitter.com/home", wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(3000)
            
            # Check if logged in
            if self._check_if_logged_in():
                print("[OK] Session valid - already logged in")
                return True
            else:
                print("[WARN] Session expired - not logged in")
                # Clean up
                self._cleanup_browser()
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to load session: {str(e)}")
            try:
                self._cleanup_browser()
            except:
                pass
            return False

    def _check_if_logged_in(self) -> bool:
        """
        Check if user is logged in by looking for authenticated UI elements.
        
        Returns:
            True if logged in, False otherwise
        """
        try:
            if not self.page:
                return False

            # Check for multiple indicators of being logged in
            indicators_found = 0
            
            selectors = [
                'nav[role="navigation"]',           # Sidebar navigation
                '[data-testid="tweetTextarea_0"]',  # Tweet composer
                '[data-testid="SideNav_Account"]',  # User account menu
                '[data-testid="primaryColumn"]',    # Main timeline
                '[data-testid="app-bar-close"]',    # Profile menu
                '[data-testid="SideNav_NewTweet"]', # Tweet button
            ]

            for selector in selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element:
                        indicators_found += 1
                        if indicators_found >= 2:
                            return True
                except:
                    continue

            # Fallback: check URL + at least 1 indicator
            if self.page.url:
                current_url = self.page.url.lower()
                if '/home' in current_url or '/timeline' in current_url:
                    if indicators_found >= 1:
                        return True

            return False

        except Exception:
            return False

    def _wait_for_login_complete(self, timeout_seconds: int = 600) -> bool:
        """
        Wait for user to complete login. Browser stays open the entire time.
        
        Args:
            timeout_seconds: Maximum time to wait (default: 10 minutes)
            
        Returns:
            True if login completed, False if timeout
        """
        start_time = time.time()
        check_interval = 3
        consecutive_success = 0
        required_successes = 3
        last_status_time = time.time()

        print("[INFO] Waiting for login completion...")
        print(f"[INFO] Checking every {check_interval} seconds")
        print("[INFO] Need 3 consecutive successful checks\n")

        while (time.time() - start_time) < timeout_seconds:
            try:
                # Ensure page is still valid
                if not self.page:
                    print("[ERROR] Page closed unexpectedly")
                    return False

                if self._check_if_logged_in():
                    consecutive_success += 1
                    remaining = int(timeout_seconds - (time.time() - start_time))

                    if consecutive_success >= required_successes:
                        print(f"\n[SUCCESS] ✓ Login confirmed! ({consecutive_success}/{required_successes})")
                        return True
                    else:
                        print(f"[INFO] Login detected, verifying... ({consecutive_success}/{required_successes}) - {remaining}s remaining")
                else:
                    if consecutive_success > 0:
                        print(f"[INFO] Verification reset (page may be loading)")
                    consecutive_success = 0

                    # Print status every 30 seconds
                    elapsed = int(time.time() - start_time)
                    if elapsed > 0 and elapsed % 30 == 0 and (time.time() - last_status_time) >= 25:
                        remaining = timeout_seconds - elapsed
                        print(f"[INFO] Still waiting... ({remaining}s remaining)")
                        print("[INFO] Please complete login in the browser window")
                        last_status_time = time.time()

            except Exception:
                consecutive_success = 0

            time.sleep(check_interval)

        print(f"\n[WARN] Timeout after {timeout_seconds} seconds")
        print("[INFO] Browser still open - you can continue using it")
        return False

    def _save_session(self):
        """Save session cookies and storage to JSON file for future runs."""
        try:
            if self.context and self.page:
                # Ensure directory exists
                self.session_file.parent.mkdir(exist_ok=True, parents=True)
                
                # Get storage state (cookies, localStorage, etc.)
                storage_state = self.context.storage_state()
                
                # Save to JSON
                with open(self.session_file, 'w', encoding='utf-8') as f:
                    json.dump(storage_state, f, indent=2)
                
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "_save_session",
                    "SUCCESS", f"Session saved to {self.session_file}"
                )
                print(f"[OK] Session saved to: {self.session_file}")
                
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "_save_session",
                "FAILED", str(e)
            )
            print(f"[WARN] Failed to save session: {str(e)}")

    def _cleanup_browser(self):
        """Clean up any existing browser instance."""
        try:
            if self.page:
                try:
                    self.page.close()
                except:
                    pass
            if self.context:
                try:
                    self.context.close()
                except:
                    pass
            if self.browser:
                try:
                    self.browser.close()
                except:
                    pass
            if self._playwright:
                try:
                    self._playwright.stop()
                except:
                    pass
        except:
            pass
        
        self.browser = None
        self.context = None
        self.page = None
        self._playwright = None
        self._authenticated = False

    def watch(self) -> int:
        """
        Watch Twitter for new notifications and DMs.
        
        Returns:
            Number of new tasks created
        """
        BronzeLogger.log_skill_execution(
            self.logger, "TwitterWatcherSkill", "watch",
            "IN_PROGRESS", "Checking Twitter notifications and DMs"
        )

        # Authenticate if needed
        if not self._authenticated:
            if not self.authenticate():
                print("[INFO] Authentication failed or cancelled")
                return 0

        # Verify page is available
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
        """Check for new notifications."""
        try:
            print("[INFO] Checking notifications...")
            
            self.page.goto("https://twitter.com/notifications", wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(5000)

            notifications = self.page.query_selector_all('article[role="article"]')

            if not notifications or len(notifications) == 0:
                print("[INFO] No notifications found")
                return 0

            print(f"[INFO] Found {len(notifications)} notification(s)")

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
                        title="Twitter Notification",
                        content=content,
                        source="Twitter",
                        metadata={"Timestamp": time.strftime('%Y-%m-%d %H:%M:%S')}
                    )

                    if task_path:
                        self._save_processed_id(notif_id)
                        tasks_created += 1

                except:
                    continue

            return tasks_created

        except Exception as e:
            print(f"[ERROR] Notifications check failed: {str(e)}")
            return 0

    def _check_dms(self) -> int:
        """Check for new direct messages."""
        try:
            print("[INFO] Checking DMs...")
            
            self.page.goto("https://twitter.com/messages", wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(5000)

            conversations = self.page.query_selector_all('div[role="group"]')

            if not conversations or len(conversations) == 0:
                print("[INFO] No DM conversations found")
                return 0

            print(f"[INFO] Found {len(conversations)} conversation(s)")

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
                        title="Twitter DM",
                        content=content,
                        source="Twitter",
                        metadata={"Timestamp": time.strftime('%Y-%m-%d %H:%M:%S')}
                    )

                    if task_path:
                        self._save_processed_id(dm_id)
                        tasks_created += 1

                except:
                    continue

            return tasks_created

        except Exception as e:
            print(f"[ERROR] DM check failed: {str(e)}")
            return 0

    def close(self):
        """Close browser and cleanup."""
        print("\n[INFO] Closing Twitter watcher...")
        
        try:
            # Save session before closing (if authenticated)
            if self._authenticated and self.context:
                self._save_session()
            
            # Give time for cookies to save
            if self.browser:
                time.sleep(2)
                try:
                    self.browser.close()
                except:
                    pass
            
            if self._playwright:
                try:
                    self._playwright.stop()
                except:
                    pass
                    
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "close",
                "SUCCESS", "Browser closed"
            )
            print("[OK] Twitter watcher closed")
            
        except Exception as e:
            print(f"[WARN] Cleanup error: {str(e)}")
        finally:
            self.browser = None
            self.context = None
            self.page = None
            self._playwright = None
            self._authenticated = False
