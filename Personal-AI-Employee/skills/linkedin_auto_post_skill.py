from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import time
import random
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from vault_manager import VaultManager
from bronze_logger import BronzeLogger
from config import Config


class LinkedInAutoPostSkill:
    """Agent skill for automated LinkedIn posting"""

    def __init__(self):
        self.skill_name = "LinkedInAutoPost"
        self.vault_manager = VaultManager()
        self.logger = BronzeLogger.get_logger("LinkedInAutoPost")
        self.browser = None
        self.context = None
        self.page = None
        self.session_file = Config.BASE_DIR / "credentials" / "linkedin_session.json"
        self.posted_ids: Set[str] = set()
        self._load_posted_ids()

    def _load_posted_ids(self):
        """Load previously posted task IDs from tracking file"""
        tracking_file = Config.LOGS_DIR / "linkedin_posted.txt"
        if tracking_file.exists():
            content = tracking_file.read_text(encoding='utf-8')
            self.posted_ids = set(content.strip().split('\n')) if content.strip() else set()
            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInAutoPostSkill", "load_posted_ids",
                "SUCCESS", f"Loaded {len(self.posted_ids)} posted IDs"
            )

    def _save_posted_id(self, post_id: str):
        """Save posted ID to tracking file"""
        tracking_file = Config.LOGS_DIR / "linkedin_posted.txt"
        with open(tracking_file, 'a', encoding='utf-8') as f:
            f.write(f"{post_id}\n")
        self.posted_ids.add(post_id)

    def is_already_posted(self, post_id: str) -> bool:
        """Check if content has already been posted"""
        return post_id in self.posted_ids

    def authenticate(self) -> bool:
        """
        Authenticate with LinkedIn using Playwright

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            from playwright.sync_api import sync_playwright

            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInAutoPostSkill", "authenticate",
                "IN_PROGRESS", "Launching browser for LinkedIn"
            )

            playwright = sync_playwright().start()

            # Use slower, more human-like browser settings
            self.browser = playwright.chromium.launch(
                headless=False,
                slow_mo=100  # Slow down operations by 100ms
            )

            # Load existing session if available
            if self.session_file.exists():
                self.context = self.browser.new_context(
                    storage_state=str(self.session_file),
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
            else:
                self.context = self.browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )

            self.page = self.context.new_page()
            self.page.goto("https://www.linkedin.com/feed/")

            # Wait and check if logged in
            time.sleep(3)

            if "feed" in self.page.url:
                # Already logged in, save session
                self.session_file.parent.mkdir(exist_ok=True)
                self.context.storage_state(path=str(self.session_file))

                BronzeLogger.log_skill_execution(
                    self.logger, "LinkedInAutoPostSkill", "authenticate",
                    "SUCCESS", "LinkedIn authenticated (existing session)"
                )
                return True

            # Need to login
            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInAutoPostSkill", "authenticate",
                "IN_PROGRESS", "Manual login required - please login in browser"
            )

            # Wait for user to login manually
            self.page.wait_for_url("**/feed/**", timeout=120000)

            # Save session
            self.session_file.parent.mkdir(exist_ok=True)
            self.context.storage_state(path=str(self.session_file))

            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInAutoPostSkill", "authenticate",
                "SUCCESS", "LinkedIn authenticated (new session)"
            )
            return True

        except ImportError as e:
            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInAutoPostSkill", "authenticate",
                "FAILED", f"Playwright not installed: {str(e)}"
            )
            return False
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInAutoPostSkill", "authenticate",
                "FAILED", str(e)
            )
            return False

    def post_to_linkedin(self, content: str, post_id: str) -> bool:
        """
        Post content to LinkedIn

        Args:
            content: Post content (text)
            post_id: Unique identifier for duplicate prevention

        Returns:
            True if post successful, False otherwise
        """
        BronzeLogger.log_skill_execution(
            self.logger, "LinkedInAutoPostSkill", "post_to_linkedin",
            "IN_PROGRESS", f"Posting content (ID: {post_id})"
        )

        if not self.page:
            if not self.authenticate():
                return False

        try:
            # Navigate to feed if not already there
            if "feed" not in self.page.url:
                self.page.goto("https://www.linkedin.com/feed/")
                self.page.wait_for_load_state("networkidle")
                time.sleep(2)

            # Try multiple selectors for "Start a post" button with proper waits
            start_post_button = None
            selectors = [
                # Class-based selectors (LinkedIn changes these frequently)
                '[class*="share-box-feed-entry__trigger"]',
                '[class*="share-box-feed-entry"]',
                'button[class*="share-box"]',
                '.share-box-feed-entry__trigger',

                # Text-based selectors (more reliable)
                'button:has-text("Start a post")',
                'button:has-text("Start post")',
                'div[role="button"]:has-text("Start a post")',

                # Aria label selectors
                'button[aria-label*="Start a post"]',
                '[aria-label*="Start a post"]',

                # Generic button with share-related classes
                'button[class*="artdeco-button"][class*="share"]',

                # Fallback: any button in the share box area
                '.share-box button',
                'div[class*="share-box"] button'
            ]

            for selector in selectors:
                try:
                    # Wait for selector with short timeout
                    self.page.wait_for_selector(selector, timeout=3000, state="visible")
                    start_post_button = self.page.query_selector(selector)
                    if start_post_button:
                        BronzeLogger.log_skill_execution(
                            self.logger, "LinkedInAutoPostSkill", "post_to_linkedin",
                            "IN_PROGRESS", f"Found 'Start a post' button using selector: {selector}"
                        )
                        break
                except:
                    continue

            if not start_post_button:
                BronzeLogger.log_skill_execution(
                    self.logger, "LinkedInAutoPostSkill", "post_to_linkedin",
                    "FAILED", "Could not find 'Start a post' button with any selector"
                )
                return False

            # Click the button and wait for editor to appear
            start_post_button.click()

            # Wait for post editor to appear
            self.page.wait_for_selector('[class*="ql-editor"]', timeout=5000, state="visible")
            time.sleep(1)

            # Find the post editor
            editor = self.page.query_selector('[class*="ql-editor"]')
            if not editor:
                BronzeLogger.log_skill_execution(
                    self.logger, "LinkedInAutoPostSkill", "post_to_linkedin",
                    "FAILED", "Could not find post editor"
                )
                return False

            # Type content with human-like delays
            editor.click()
            time.sleep(1)

            # Type character by character with random delays
            for char in content:
                editor.type(char)
                time.sleep(random.uniform(0.05, 0.15))

            time.sleep(2)

            # Click Post button
            post_button = self.page.query_selector('button[class*="share-actions__primary-action"]')
            if not post_button:
                BronzeLogger.log_skill_execution(
                    self.logger, "LinkedInAutoPostSkill", "post_to_linkedin",
                    "FAILED", "Could not find Post button"
                )
                return False

            post_button.click()
            time.sleep(3)

            # Verify post was created (check for success message or return to feed)
            if "feed" in self.page.url:
                self._save_posted_id(post_id)

                BronzeLogger.log_skill_execution(
                    self.logger, "LinkedInAutoPostSkill", "post_to_linkedin",
                    "SUCCESS", f"Posted successfully (ID: {post_id})"
                )

                # Log to vault
                self._log_post_to_vault(content, post_id)

                return True
            else:
                BronzeLogger.log_skill_execution(
                    self.logger, "LinkedInAutoPostSkill", "post_to_linkedin",
                    "FAILED", "Post may not have been created"
                )
                return False

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInAutoPostSkill", "post_to_linkedin",
                "FAILED", str(e)
            )
            return False

    def post_from_vault_task(self, task_path: Path) -> bool:
        """
        Create LinkedIn post from Vault task

        Args:
            task_path: Path to task file in Vault

        Returns:
            True if post successful, False otherwise
        """
        BronzeLogger.log_skill_execution(
            self.logger, "LinkedInAutoPostSkill", "post_from_vault_task",
            "IN_PROGRESS", f"Processing task: {task_path.name}"
        )

        try:
            # Read task content
            content = self.vault_manager.read_task(task_path)
            if not content:
                return False

            # Extract post content from task
            post_content = self._extract_post_content(content)

            if not post_content:
                BronzeLogger.log_skill_execution(
                    self.logger, "LinkedInAutoPostSkill", "post_from_vault_task",
                    "FAILED", "Could not extract post content from task"
                )
                return False

            # Generate post ID from task filename
            post_id = f"vault_{task_path.stem}"

            # Check if already posted
            if self.is_already_posted(post_id):
                BronzeLogger.log_skill_execution(
                    self.logger, "LinkedInAutoPostSkill", "post_from_vault_task",
                    "FAILED", f"Task already posted: {post_id}"
                )
                return False

            # Post to LinkedIn
            success = self.post_to_linkedin(post_content, post_id)

            if success:
                BronzeLogger.log_skill_execution(
                    self.logger, "LinkedInAutoPostSkill", "post_from_vault_task",
                    "SUCCESS", f"Posted task: {task_path.name}"
                )

            return success

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInAutoPostSkill", "post_from_vault_task",
                "FAILED", str(e)
            )
            return False

    def _extract_post_content(self, task_content: str) -> Optional[str]:
        """
        Extract LinkedIn post content from task markdown

        Args:
            task_content: Full task markdown content

        Returns:
            Extracted post content or None
        """
        # Look for "## LinkedIn Post" section
        if "## LinkedIn Post" in task_content:
            lines = task_content.split('\n')
            post_lines = []
            in_post_section = False

            for line in lines:
                if line.strip() == "## LinkedIn Post":
                    in_post_section = True
                    continue
                elif line.startswith("##") and in_post_section:
                    break
                elif in_post_section and line.strip():
                    post_lines.append(line.strip())

            return '\n'.join(post_lines) if post_lines else None

        # Fallback: use description section
        if "## Description" in task_content:
            lines = task_content.split('\n')
            desc_lines = []
            in_desc_section = False

            for line in lines:
                if line.strip() == "## Description":
                    in_desc_section = True
                    continue
                elif line.startswith("##") and in_desc_section:
                    break
                elif in_desc_section and line.strip():
                    desc_lines.append(line.strip())

            content = '\n'.join(desc_lines)
            # Limit to 3000 characters (LinkedIn limit)
            return content[:3000] if content else None

        return None

    def _log_post_to_vault(self, content: str, post_id: str):
        """Log posted content to Vault for record keeping"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"{timestamp}_LinkedIn_Post_{post_id}.md"
            log_path = Config.DONE / log_filename

            log_content = f"""# LinkedIn Post - {post_id}

**Posted**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status**: [POSTED]
**Platform**: LinkedIn

## Content

{content}

#linkedin #posted #auto-generated
"""

            log_path.write_text(log_content, encoding='utf-8')

            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInAutoPostSkill", "_log_post_to_vault",
                "SUCCESS", f"Logged post to Vault: {log_filename}"
            )

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInAutoPostSkill", "_log_post_to_vault",
                "FAILED", str(e)
            )

    def close(self):
        """Close browser and cleanup"""
        if self.browser:
            self.browser.close()
            BronzeLogger.log_skill_execution(
                self.logger, "LinkedInAutoPostSkill", "close",
                "SUCCESS", "Browser closed"
            )
