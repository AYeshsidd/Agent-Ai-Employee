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
        self._authenticated = False

    def authenticate(self, force_fresh: bool = False) -> bool:
        """
        Authenticate with Twitter/X using Playwright

        Args:
            force_fresh: If True, ignore existing session and force fresh login

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "authenticate",
                "IN_PROGRESS", "Launching browser for Twitter"
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

            playwright = sync_playwright().start()
            
            # Launch browser with settings that prevent early closing
            self.browser = playwright.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )

            # Decide whether to use existing session or force fresh login
            use_existing_session = self.session_file.exists() and not force_fresh
            
            if use_existing_session:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "authenticate",
                    "IN_PROGRESS", "Loading existing session"
                )
                
                try:
                    # Try to load existing session
                    self.context = self.browser.new_context(
                        storage_state=str(self.session_file),
                        viewport={'width': 1280, 'height': 720},
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    )
                    
                    self.page = self.context.new_page()
                    
                    # Navigate to Twitter and check if session is still valid
                    self.page.goto("https://twitter.com/home", wait_until="domcontentloaded")
                    self.page.wait_for_timeout(5000)
                    
                    # Check if we're actually logged in by looking for authenticated elements
                    is_logged_in = self._check_if_logged_in()
                    
                    if is_logged_in:
                        BronzeLogger.log_skill_execution(
                            self.logger, "TwitterWatcherSkill", "authenticate",
                            "SUCCESS", "Twitter authenticated (existing session valid)"
                        )
                        self._authenticated = True
                        return True
                    else:
                        BronzeLogger.log_skill_execution(
                            self.logger, "TwitterWatcherSkill", "authenticate",
                            "IN_PROGRESS", "Existing session expired, forcing fresh login"
                        )
                        # Session expired, close and do fresh login
                        self.page.close()
                        self.context.close()
                        use_existing_session = False
                        
                except Exception as e:
                    BronzeLogger.log_skill_execution(
                        self.logger, "TwitterWatcherSkill", "authenticate",
                        "IN_PROGRESS", f"Session load failed: {str(e)}, forcing fresh login"
                    )
                    try:
                        if self.page:
                            self.page.close()
                        if self.context:
                            self.context.close()
                    except:
                        pass
                    use_existing_session = False

            # Fresh login required
            if not use_existing_session:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "authenticate",
                    "IN_PROGRESS", "Creating new browser context for fresh login"
                )
                
                self.context = self.browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                self.page = self.context.new_page()
                
                # Navigate to Twitter login
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "authenticate",
                    "IN_PROGRESS", "Navigating to Twitter login page"
                )
                
                self.page.goto("https://twitter.com/i/flow/login", wait_until="domcontentloaded")
                self.page.wait_for_timeout(3000)
                
                # Inform user to login manually
                print("\n" + "=" * 70)
                print("  TWITTER LOGIN REQUIRED")
                print("=" * 70)
                print("\n  Please log in to Twitter/X in the browser window.")
                print("  The script will wait for successful login...")
                print("\n  [INFO] Browser will remain open until login is complete")
                print("  [INFO] After login, session will be saved for future runs")
                print("=" * 70)
                
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "authenticate",
                    "IN_PROGRESS", "Waiting for manual login (up to 3 minutes)"
                )
                
                # Wait for login with extended timeout
                # We'll poll for the home page elements instead of relying on URL
                login_success = self._wait_for_login(180)  # 3 minutes
                
                if not login_success:
                    BronzeLogger.log_skill_execution(
                        self.logger, "TwitterWatcherSkill", "authenticate",
                        "FAILED", "Login timeout - user did not complete login"
                    )
                    print("\n[ERROR] Login timeout. Please try again.")
                    return False
                
                # Login successful - save session
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "authenticate",
                    "IN_PROGRESS", "Login successful, saving session"
                )
                
                # Wait a bit for all cookies to settle
                self.page.wait_for_timeout(3000)
                
                # Save session/cookies
                self.session_file.parent.mkdir(exist_ok=True, parents=True)
                try:
                    self.context.storage_state(path=str(self.session_file))
                    BronzeLogger.log_skill_execution(
                        self.logger, "TwitterWatcherSkill", "authenticate",
                        "SUCCESS", f"Session saved to {self.session_file}"
                    )
                except Exception as e:
                    BronzeLogger.log_skill_execution(
                        self.logger, "TwitterWatcherSkill", "authenticate",
                        "FAILED", f"Failed to save session: {str(e)}"
                    )
                    return False

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
        Check if user is logged in by looking for authenticated elements
        
        Returns:
            True if logged in, False otherwise
        """
        try:
            # Look for elements that only appear when logged in
            logged_in_selectors = [
                '[data-testid="SideNav_Account"]',  # Account menu in sidebar
                '[data-testid="app-bar-close"]',    # App bar (logged in view)
                'nav[role="navigation"]',           # Main navigation
                '[data-testid="primaryColumn"]',    # Main content column
            ]
            
            for selector in logged_in_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element:
                        # Double-check by looking for user avatar or name
                        avatar = self.page.query_selector('[data-testid="SideNav_Account"] img')
                        if avatar:
                            return True
                except:
                    continue
            
            # Also check URL as fallback
            current_url = self.page.url.lower()
            if "home" in current_url or "timeline" in current_url:
                # Verify by checking for tweet composer (only visible when logged in)
                composer = self.page.query_selector('[data-testid="tweetTextarea_0"]')
                if composer:
                    return True
            
            return False
            
        except Exception as e:
            return False

    def _wait_for_login(self, timeout_seconds: int = 180) -> bool:
        """
        Wait for user to complete login by polling for authenticated state
        
        Args:
            timeout_seconds: Maximum time to wait for login
        
        Returns:
            True if login successful, False if timeout
        """
        start_time = time.time()
        check_interval = 3  # Check every 3 seconds
        stable_count = 0  # Count consecutive successful checks
        
        print("\n[INFO] Waiting for login completion...")
        
        while (time.time() - start_time) < timeout_seconds:
            try:
                # Check if logged in
                if self._check_if_logged_in():
                    stable_count += 1
                    print(f"[INFO] Login detected! Verifying... ({stable_count}/3)")
                    
                    # Require 3 consecutive successful checks to ensure stable login
                    if stable_count >= 3:
                        print("[INFO] Login confirmed!")
                        return True
                else:
                    stable_count = 0
                    elapsed = int(time.time() - start_time)
                    remaining = timeout_seconds - elapsed
                    if elapsed % 15 == 0:  # Print status every 15 seconds
                        print(f"[INFO] Still waiting for login... ({remaining}s remaining)")
                
            except Exception as e:
                stable_count = 0
                pass
            
            time.sleep(check_interval)
        
        print(f"[ERROR] Login timeout after {timeout_seconds} seconds")
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
                "FAILED", "No page available - authentication failed"
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
            # Navigate to notifications
            self.page.goto("https://twitter.com/notifications", wait_until="domcontentloaded")
            self.page.wait_for_timeout(5000)

            # Look for notifications with multiple selector strategies
            notification_selectors = [
                'article[role="article"]',
                '[data-testid="primaryColumn"] article',
                'div[data-testid="cellInner"]'
            ]

            notifications = []
            for selector in notification_selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        notifications = elements
                        break
                except:
                    continue

            if not notifications:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "_check_notifications",
                    "SUCCESS", "No notifications found"
                )
                return 0

            tasks_created = 0
            for notif in notifications[:5]:  # Limit to 5
                try:
                    notif_data = self._extract_notification_data(notif)
                    if not notif_data or not notif_data.get('content'):
                        continue

                    # Generate unique ID
                    notif_id = f"twitter_notif_{notif_data.get('content', '')[:30]}_{int(time.time())}"

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
                    BronzeLogger.log_skill_execution(
                        self.logger, "TwitterWatcherSkill", "_check_notifications",
                        "FAILED", f"Error processing notification: {str(e)}"
                    )
                    continue

            return tasks_created

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "_check_notifications",
                "FAILED", str(e)
            )
            return 0

    def _check_dms(self) -> int:
        """Check for new direct messages"""
        try:
            # Navigate to messages
            self.page.goto("https://twitter.com/messages", wait_until="domcontentloaded")
            self.page.wait_for_timeout(5000)

            # Look for conversation containers
            conversation_selectors = [
                'div[role="group"]',
                '[data-testid="DMDrawerItem"]',
                'a[href*="/messages"]'
            ]

            conversations = []
            for selector in conversation_selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        conversations = elements
                        break
                except:
                    continue

            if not conversations:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "_check_dms",
                    "SUCCESS", "No DM conversations found"
                )
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
                    BronzeLogger.log_skill_execution(
                        self.logger, "TwitterWatcherSkill", "_check_dms",
                        "FAILED", f"Error processing DM: {str(e)}"
                    )
                    continue

            return tasks_created

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterWatcherSkill", "_check_dms",
                "FAILED", str(e)
            )
            return 0

    def _extract_notification_data(self, notif_element) -> Optional[Dict[str, str]]:
        """Extract data from Twitter notification element"""
        try:
            # Try to extract notification content
            content = ""
            content_elem = notif_element.query_selector('[data-testid="notificationText"]')
            if content_elem:
                content = content_elem.inner_text()
            else:
                # Fallback: get all text content
                content = notif_element.inner_text()[:500]

            # Extract username if available
            from_user = "Unknown"
            user_elem = notif_element.query_selector('[data-testid="User-Name"]')
            if user_elem:
                from_user = user_elem.inner_text()

            # Determine notification type
            notif_type = "General"
            content_lower = content.lower()
            if "liked" in content_lower or "like" in content_lower:
                notif_type = "Like"
            elif "retweeted" in content_lower or "reposted" in content_lower or "repost" in content_lower:
                notif_type = "Retweet/Repost"
            elif "followed" in content_lower or "follow" in content_lower:
                notif_type = "Follow"
            elif "mentioned" in content_lower or "mention" in content_lower:
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
            from_user = "Unknown"
            name_elem = conv_element.query_selector('[data-testid="User-Name"]')
            if name_elem:
                from_user = name_elem.inner_text()
            else:
                # Try alternative selector
                name_elem = conv_element.query_selector('span[dir="auto"]')
                if name_elem:
                    from_user = name_elem.inner_text()

            # Extract message preview
            message = "No preview available"
            message_elem = conv_element.query_selector('span[dir="auto"]')
            if message_elem:
                message = message_elem.inner_text()

            return {
                'from': from_user.strip() if from_user else "Unknown",
                'message': message.strip()[:500] if message else "No message"
            }

        except Exception as e:
            return None

    def close(self):
        """Close browser and cleanup"""
        if self.browser:
            try:
                self.browser.close()
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "close",
                    "SUCCESS", "Browser closed"
                )
            except Exception as e:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterWatcherSkill", "close",
                    "FAILED", f"Error closing browser: {str(e)}"
                )
            finally:
                self.browser = None
                self.context = None
                self.page = None
                self._authenticated = False
