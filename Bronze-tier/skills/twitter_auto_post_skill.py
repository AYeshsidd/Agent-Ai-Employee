#!/usr/bin/env python3
"""Twitter Auto-Post Skill - Automated Twitter/X Posting"""
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import time
import random
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from vault_manager import VaultManager
from bronze_logger import BronzeLogger
from config import Config


class TwitterAutoPostSkill:
    """
    Agent skill for automated Twitter/X posting.
    
    Capabilities:
    - Auto-post tweets from Vault tasks
    - Session reuse via twitter_session.json
    - Duplicate prevention
    - Vault logging of posted content
    """

    def __init__(self):
        self.skill_name = "TwitterAutoPost"
        self.vault_manager = VaultManager()
        self.logger = BronzeLogger.get_logger("TwitterAutoPost")
        self.browser = None
        self.context = None
        self.page = None
        self.session_file = Config.BASE_DIR / "credentials" / "twitter_session.json"
        self.posted_ids: Set[str] = set()
        self._load_posted_ids()

    def _load_posted_ids(self):
        """Load previously posted tweet IDs from tracking file"""
        tracking_file = Config.LOGS_DIR / "twitter_posted.txt"
        if tracking_file.exists():
            content = tracking_file.read_text(encoding='utf-8')
            self.posted_ids = set(content.strip().split('\n')) if content.strip() else set()
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAutoPostSkill", "load_posted_ids",
                "SUCCESS", f"Loaded {len(self.posted_ids)} posted IDs"
            )

    def _save_posted_id(self, post_id: str):
        """Save posted ID to tracking file"""
        tracking_file = Config.LOGS_DIR / "twitter_posted.txt"
        with open(tracking_file, 'a', encoding='utf-8') as f:
            f.write(f"{post_id}\n")
        self.posted_ids.add(post_id)

    def is_already_posted(self, post_id: str) -> bool:
        """Check if content has already been posted"""
        return post_id in self.posted_ids

    def authenticate(self) -> bool:
        """
        Authenticate with Twitter/X using Playwright with session reuse.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            from playwright.sync_api import sync_playwright

            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAutoPostSkill", "authenticate",
                "IN_PROGRESS", "Launching browser for Twitter/X"
            )

            playwright = sync_playwright().start()

            # Launch browser
            self.browser = playwright.chromium.launch(
                headless=False,
                slow_mo=100,
                args=['--disable-blink-features=AutomationControlled']
            )

            # Load existing session if available
            if self.session_file.exists():
                print(f"[INFO] Loading saved Twitter session from {self.session_file}")
                try:
                    with open(self.session_file, 'r', encoding='utf-8') as f:
                        storage_state = json.load(f)
                    
                    self.context = self.browser.new_context(
                        storage_state=storage_state,
                        viewport={'width': 1280, 'height': 720},
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    )
                    print("[INFO] Session loaded successfully")
                except Exception as e:
                    print(f"[WARN] Failed to load session: {str(e)}")
                    self.context = self.browser.new_context(
                        viewport={'width': 1280, 'height': 720}
                    )
            else:
                print("[WARN] No saved session found - manual login required")
                self.context = self.browser.new_context(
                    viewport={'width': 1280, 'height': 720}
                )

            self.page = self.context.new_page()
            self.page.goto("https://twitter.com/home")

            # Wait and check if logged in
            self.page.wait_for_timeout(5000)

            if self._check_if_logged_in():
                # Already logged in, save/update session
                self._save_session()
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAutoPostSkill", "authenticate",
                    "SUCCESS", "Twitter authenticated (existing session)"
                )
                return True

            # Need to login
            print("\n" + "=" * 70)
            print("  TWITTER/X LOGIN REQUIRED")
            print("=" * 70)
            print("\n  Please log in to Twitter/X in the browser window.")
            print("  Session will be saved for future auto-posts.\n")

            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAutoPostSkill", "authenticate",
                "IN_PROGRESS", "Manual login required"
            )

            # Wait for user to login manually
            try:
                self.page.wait_for_url("**/home**", timeout=120000)
            except:
                pass

            # Wait for page to stabilize
            self.page.wait_for_timeout(3000)

            if self._check_if_logged_in():
                # Save session
                self._save_session()
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAutoPostSkill", "authenticate",
                    "SUCCESS", "Twitter authenticated (new session)"
                )
                return True
            else:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAutoPostSkill", "authenticate",
                    "FAILED", "Login verification failed"
                )
                return False

        except ImportError as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAutoPostSkill", "authenticate",
                "FAILED", f"Playwright not installed: {str(e)}"
            )
            return False
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAutoPostSkill", "authenticate",
                "FAILED", str(e)
            )
            return False

    def _check_if_logged_in(self) -> bool:
        """Check if user is logged in"""
        try:
            if not self.page:
                return False

            # Check for logged-in indicators
            indicators = [
                '[data-testid="tweetTextarea_0"]',  # Tweet composer
                'nav[role="navigation"]',           # Sidebar
                '[data-testid="SideNav_Account"]',  # Account menu
            ]

            for selector in indicators:
                try:
                    if self.page.query_selector(selector):
                        return True
                except:
                    continue

            return False
        except:
            return False

    def _save_session(self):
        """Save session to JSON file"""
        try:
            if self.context:
                self.session_file.parent.mkdir(exist_ok=True)
                storage_state = self.context.storage_state()
                with open(self.session_file, 'w', encoding='utf-8') as f:
                    json.dump(storage_state, f, indent=2)
                print(f"[OK] Session saved to {self.session_file}")
        except Exception as e:
            print(f"[WARN] Failed to save session: {str(e)}")

    def post_tweet(self, content: str, post_id: str) -> bool:
        """
        Post a tweet to Twitter/X
        
        Args:
            content: Tweet content (max 280 characters)
            post_id: Unique identifier for duplicate prevention
            
        Returns:
            True if successful, False otherwise
        """
        BronzeLogger.log_skill_execution(
            self.logger, "TwitterAutoPostSkill", "post_tweet",
            "IN_PROGRESS", f"Posting tweet (ID: {post_id})"
        )

        # Check character limit
        if len(content) > 280:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAutoPostSkill", "post_tweet",
                "FAILED", f"Content exceeds 280 chars: {len(content)}"
            )
            return False

        if not self.page:
            if not self.authenticate():
                return False

        try:
            # Navigate to home
            self.page.goto("https://twitter.com/home")
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(3000)

            # Find tweet composer
            composer = self.page.query_selector('[data-testid="tweetTextarea_0"]')
            if not composer:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAutoPostSkill", "post_tweet",
                    "FAILED", "Tweet composer not found"
                )
                return False

            # Click and type with human-like delays
            composer.click()
            time.sleep(1)

            for char in content:
                self.page.keyboard.type(char)
                time.sleep(random.uniform(0.05, 0.15))

            time.sleep(2)

            # Find and click Tweet button
            tweet_button = self.page.query_selector('[data-testid="tweetButton"]')
            if not tweet_button:
                tweet_button = self.page.query_selector('[data-testid="tweetButtonInline"]')

            if tweet_button:
                tweet_button.click()
                self.page.wait_for_timeout(3000)

                # Save posted ID
                self._save_posted_id(post_id)

                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAutoPostSkill", "post_tweet",
                    "SUCCESS", f"Tweet posted (ID: {post_id})"
                )

                # Log to vault
                self._log_post_to_vault(content, post_id)

                return True
            else:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAutoPostSkill", "post_tweet",
                    "FAILED", "Tweet button not found"
                )
                return False

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAutoPostSkill", "post_tweet",
                "FAILED", str(e)
            )
            return False

    def post_from_vault_task(self, task_path: Path) -> bool:
        """
        Create Twitter post from Vault task
        
        Args:
            task_path: Path to task file in Vault
            
        Returns:
            True if successful, False otherwise
        """
        BronzeLogger.log_skill_execution(
            self.logger, "TwitterAutoPostSkill", "post_from_vault_task",
            "IN_PROGRESS", f"Processing: {task_path.name}"
        )

        try:
            # Read task content
            content = self.vault_manager.read_task(task_path)
            if not content:
                return False

            # Extract tweet content
            tweet_content = self._extract_tweet_content(content)
            if not tweet_content:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAutoPostSkill", "post_from_vault_task",
                    "FAILED", "Could not extract tweet content"
                )
                return False

            # Generate post ID
            post_id = f"vault_{task_path.stem}"

            # Check if already posted
            if self.is_already_posted(post_id):
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAutoPostSkill", "post_from_vault_task",
                    "FAILED", f"Already posted: {post_id}"
                )
                return False

            # Post to Twitter
            success = self.post_tweet(tweet_content, post_id)

            if success:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAutoPostSkill", "post_from_vault_task",
                    "SUCCESS", f"Posted task: {task_path.name}"
                )

            return success

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAutoPostSkill", "post_from_vault_task",
                "FAILED", str(e)
            )
            return False

    def _extract_tweet_content(self, task_content: str) -> Optional[str]:
        """Extract tweet content from task markdown"""
        # Look for "## Twitter Post" section
        if "## Twitter Post" in task_content or "## Tweet" in task_content:
            lines = task_content.split('\n')
            post_lines = []
            in_section = False

            for line in lines:
                if line.strip() in ["## Twitter Post", "## Tweet"]:
                    in_section = True
                    continue
                elif line.startswith("##") and in_section:
                    break
                elif in_section and line.strip():
                    post_lines.append(line.strip())

            content = '\n'.join(post_lines)
            return content[:280] if content else None

        # Fallback: use description
        if "## Description" in task_content:
            lines = task_content.split('\n')
            desc_lines = []
            in_section = False

            for line in lines:
                if line.strip() == "## Description":
                    in_section = True
                    continue
                elif line.startswith("##") and in_section:
                    break
                elif in_section and line.strip():
                    desc_lines.append(line.strip())

            content = '\n'.join(desc_lines)
            return content[:280] if content else None

        return None

    def _log_post_to_vault(self, content: str, post_id: str):
        """Log posted content to Vault"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"{timestamp}_Twitter_Post_{post_id}.md"
            log_path = Config.DONE / log_filename

            log_content = f"""# Twitter Post - {post_id}

**Posted**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status**: [POSTED]
**Platform**: Twitter/X

## Content

{content}

#twitter #posted #auto-generated
"""

            log_path.write_text(log_content, encoding='utf-8')

            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAutoPostSkill", "_log_post_to_vault",
                "SUCCESS", f"Logged: {log_filename}"
            )

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAutoPostSkill", "_log_post_to_vault",
                "FAILED", str(e)
            )

    def close(self):
        """Close browser and cleanup"""
        if self.browser:
            try:
                self.browser.close()
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAutoPostSkill", "close",
                    "SUCCESS", "Browser closed"
                )
            except Exception as e:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAutoPostSkill", "close",
                    "FAILED", str(e)
                )
