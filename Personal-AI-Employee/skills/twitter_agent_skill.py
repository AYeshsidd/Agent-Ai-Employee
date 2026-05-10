#!/usr/bin/env python3
"""Twitter Agent Skill - Post, Read, Summary, Reply"""
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import time
import random
import sys

# Ensure project root is in sys.path
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from vault_manager import VaultManager
from bronze_logger import BronzeLogger
from config import Config


class TwitterAgentSkill:
    """
    Agent skill for Twitter/X operations.
    
    Capabilities:
    - Auto post tweets
    - Read DMs and notifications
    - Generate summaries
    - Basic reply functionality
    """

    def __init__(self):
        self.skill_name = "TwitterAgent"
        self.vault_manager = VaultManager()
        self.logger = BronzeLogger.get_logger("TwitterAgent")
        self.browser = None
        self.context = None
        self.page = None
        self.session_file = Config.BASE_DIR / "credentials" / "twitter_session.json"
        self.posted_ids: Set[str] = set()
        self._load_posted_ids()

    def _load_posted_ids(self):
        """Load previously posted tweet IDs"""
        tracking_file = Config.LOGS_DIR / "twitter_posted.txt"
        if tracking_file.exists():
            content = tracking_file.read_text(encoding='utf-8')
            self.posted_ids = set(content.strip().split('\n')) if content.strip() else set()
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAgentSkill", "load_posted_ids",
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
        Authenticate with Twitter/X using Playwright

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            from playwright.sync_api import sync_playwright

            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAgentSkill", "authenticate",
                "IN_PROGRESS", "Launching browser for Twitter"
            )

            playwright = sync_playwright().start()
            self.browser = playwright.chromium.launch(
                headless=False,
                slow_mo=100
            )

            # Load existing session if available
            if self.session_file.exists():
                self.context = self.browser.new_context(
                    storage_state=str(self.session_file),
                    viewport={'width': 1280, 'height': 720}
                )
            else:
                self.context = self.browser.new_context(
                    viewport={'width': 1280, 'height': 720}
                )

            self.page = self.context.new_page()
            self.page.goto("https://twitter.com/home")

            # Wait and check if logged in
            time.sleep(3)

            if "home" in self.page.url or "timeline" in self.page.url:
                # Already logged in, save session
                self.session_file.parent.mkdir(exist_ok=True)
                try:
                    self.context.storage_state(path=str(self.session_file))
                except:
                    pass

                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAgentSkill", "authenticate",
                    "SUCCESS", "Twitter authenticated (existing session)"
                )
                return True

            # Need to login
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAgentSkill", "authenticate",
                "IN_PROGRESS", "Manual login required - please login in browser"
            )

            # Wait for user to login manually
            try:
                self.page.wait_for_url("**/home**", timeout=120000)
            except:
                pass

            # Save session
            self.session_file.parent.mkdir(exist_ok=True)
            try:
                self.context.storage_state(path=str(self.session_file))
            except:
                pass

            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAgentSkill", "authenticate",
                "SUCCESS", "Twitter authenticated (new session)"
            )
            return True

        except ImportError as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAgentSkill", "authenticate",
                "FAILED", f"Playwright not installed: {str(e)}"
            )
            return False
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAgentSkill", "authenticate",
                "FAILED", str(e)
            )
            return False

    def post_tweet(self, content: str, post_id: str) -> bool:
        """
        Post a tweet to Twitter/X

        Args:
            content: Tweet content (max 280 characters for basic, 25000 for Premium)
            post_id: Unique identifier for duplicate prevention

        Returns:
            True if post successful, False otherwise
        """
        BronzeLogger.log_skill_execution(
            self.logger, "TwitterAgentSkill", "post_tweet",
            "IN_PROGRESS", f"Posting tweet (ID: {post_id})"
        )

        if not self.page:
            if not self.authenticate():
                return False

        try:
            # Navigate to home
            if "home" not in self.page.url:
                self.page.goto("https://twitter.com/home")
                self.page.wait_for_load_state("networkidle")
                time.sleep(2)

            # Check character count (basic limit is 280)
            if len(content) > 280:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAgentSkill", "post_tweet",
                    "FAILED", f"Content exceeds 280 characters: {len(content)}"
                )
                return False

            # Find the tweet composer
            composer_selectors = [
                '[data-testid="tweetTextarea_0"]',
                '[placeholder*="What is happening"]',
                '[placeholder*="Whats happening"]',
                'div[contenteditable="true"]'
            ]

            composer = None
            for selector in composer_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=3000, state="visible")
                    composer = self.page.query_selector(selector)
                    if composer:
                        break
                except:
                    continue

            if not composer:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAgentSkill", "post_tweet",
                    "FAILED", "Could not find tweet composer"
                )
                return False

            # Click and type with human-like delays
            composer.click()
            time.sleep(1)

            # Type character by character with random delays
            for char in content:
                self.page.keyboard.type(char)
                time.sleep(random.uniform(0.05, 0.15))

            time.sleep(2)

            # Find and click the Tweet/Post button
            tweet_button_selectors = [
                '[data-testid="tweetButton"]',
                '[data-testid="tweetButtonInline"]',
                'div[role="button"]:has-text("Post")',
                'div[role="button"]:has-text("Tweet")'
            ]

            tweet_button = None
            for selector in tweet_button_selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    for elem in elements:
                        if elem.is_visible():
                            tweet_button = elem
                            break
                    if tweet_button:
                        break
                except:
                    continue

            if not tweet_button:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAgentSkill", "post_tweet",
                    "FAILED", "Could not find Tweet/Post button"
                )
                return False

            tweet_button.click()
            time.sleep(3)

            # Verify post was created
            self._save_posted_id(post_id)

            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAgentSkill", "post_tweet",
                "SUCCESS", f"Tweet posted successfully (ID: {post_id})"
            )

            # Log to vault
            self._log_post_to_vault(content, post_id)

            return True

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAgentSkill", "post_tweet",
                "FAILED", str(e)
            )
            return False

    def read_messages(self, count: int = 10) -> List[Dict[str, str]]:
        """
        Read recent DMs from Twitter

        Args:
            count: Number of messages to read

        Returns:
            List of message dictionaries
        """
        BronzeLogger.log_skill_execution(
            self.logger, "TwitterAgentSkill", "read_messages",
            "IN_PROGRESS", f"Reading {count} messages"
        )

        if not self.page:
            if not self.authenticate():
                return []

        try:
            # Navigate to messages
            self.page.goto("https://twitter.com/messages")
            self.page.wait_for_timeout(3000)

            messages = []

            # Get conversation list
            conv_selectors = [
                '[role="group"]',
                'div[role="group"]'
            ]

            conversations = []
            for selector in conv_selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    if elements:
                        conversations = elements[:count]
                        break
                except:
                    continue

            for conv in conversations:
                try:
                    # Extract sender
                    name_elem = conv.query_selector('[data-testid="User-Name"]')
                    sender = name_elem.inner_text() if name_elem else "Unknown"

                    # Extract message
                    msg_elem = conv.query_selector('span[dir="auto"]')
                    message = msg_elem.inner_text() if msg_elem else "No content"

                    messages.append({
                        'from': sender,
                        'message': message,
                        'timestamp': datetime.now().isoformat()
                    })
                except:
                    continue

            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAgentSkill", "read_messages",
                "SUCCESS", f"Read {len(messages)} messages"
            )

            return messages

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAgentSkill", "read_messages",
                "FAILED", str(e)
            )
            return []

    def generate_summary(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a summary of Twitter messages

        Args:
            messages: List of message dictionaries

        Returns:
            Summary text
        """
        if not messages:
            return "No messages to summarize."

        summary_lines = [
            f"Twitter Messages Summary",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Messages: {len(messages)}",
            "",
            "Recent Activity:"
        ]

        # Group by sender
        by_sender = {}
        for msg in messages:
            sender = msg.get('from', 'Unknown')
            if sender not in by_sender:
                by_sender[sender] = []
            by_sender[sender].append(msg.get('message', ''))

        for sender, msgs in list(by_sender.items())[:5]:  # Top 5 senders
            summary_lines.append(f"\n  From {sender}:")
            for msg in msgs[:2]:  # Last 2 messages per sender
                summary_lines.append(f"    - {msg[:100]}...")

        return "\n".join(summary_lines)

    def reply_to_message(self, recipient: str, message: str, original_content: str = "") -> bool:
        """
        Reply to a Twitter DM

        Args:
            recipient: Username to reply to
            message: Reply message content
            original_content: Optional original message to quote

        Returns:
            True if reply successful, False otherwise
        """
        BronzeLogger.log_skill_execution(
            self.logger, "TwitterAgentSkill", "reply_to_message",
            "IN_PROGRESS", f"Replying to {recipient}"
        )

        if not self.page:
            if not self.authenticate():
                return False

        try:
            # Navigate to messages
            self.page.goto("https://twitter.com/messages")
            self.page.wait_for_timeout(3000)

            # Find conversation with recipient
            conversations = self.page.query_selector_all('[role="group"]')
            
            target_conv = None
            for conv in conversations:
                name_elem = conv.query_selector('[data-testid="User-Name"]')
                if name_elem and recipient.lower() in name_elem.inner_text().lower():
                    target_conv = conv
                    break

            if not target_conv:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAgentSkill", "reply_to_message",
                    "FAILED", f"Conversation with {recipient} not found"
                )
                return False

            # Click conversation
            target_conv.click()
            time.sleep(2)

            # Find message input
            input_selectors = [
                '[data-testid="dmComposerTextarea"]',
                '[placeholder*="Start a new message"]',
                'div[contenteditable="true"]'
            ]

            msg_input = None
            for selector in input_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=3000, state="visible")
                    msg_input = self.page.query_selector(selector)
                    if msg_input:
                        break
                except:
                    continue

            if not msg_input:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAgentSkill", "reply_to_message",
                    "FAILED", "Could not find message input"
                )
                return False

            # Type message
            msg_input.click()
            time.sleep(1)

            for char in message:
                self.page.keyboard.type(char)
                time.sleep(random.uniform(0.05, 0.15))

            time.sleep(2)

            # Click send
            send_button = self.page.query_selector('[data-testid="dmComposerSend"]')
            if send_button:
                send_button.click()
                time.sleep(2)

                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAgentSkill", "reply_to_message",
                    "SUCCESS", f"Reply sent to {recipient}"
                )
                return True
            else:
                BronzeLogger.log_skill_execution(
                    self.logger, "TwitterAgentSkill", "reply_to_message",
                    "FAILED", "Could not find send button"
                )
                return False

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAgentSkill", "reply_to_message",
                "FAILED", str(e)
            )
            return False

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
                self.logger, "TwitterAgentSkill", "_log_post_to_vault",
                "SUCCESS", f"Logged post to Vault: {log_filename}"
            )

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAgentSkill", "_log_post_to_vault",
                "FAILED", str(e)
            )

    def close(self):
        """Close browser and cleanup"""
        if self.browser:
            self.browser.close()
            BronzeLogger.log_skill_execution(
                self.logger, "TwitterAgentSkill", "close",
                "SUCCESS", "Browser closed"
            )
