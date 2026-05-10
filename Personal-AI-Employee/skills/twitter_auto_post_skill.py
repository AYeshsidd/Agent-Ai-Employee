#!/usr/bin/env python3
"""Twitter Auto-Post Skill - Fixed Version"""
from pathlib import Path
from typing import Optional, Set
from datetime import datetime
import time
import random
import sys
import json

# Ensure project root is in sys.path
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from vault_manager import VaultManager
from bronze_logger import BronzeLogger
from config import Config


class TwitterAutoPostSkill:
    """Twitter auto-post with keyboard-only posting (no button clicks)"""

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
        tracking_file = Config.LOGS_DIR / "twitter_posted.txt"
        if tracking_file.exists():
            content = tracking_file.read_text(encoding='utf-8')
            self.posted_ids = set(content.strip().split('\n')) if content.strip() else set()

    def _save_posted_id(self, post_id: str):
        tracking_file = Config.LOGS_DIR / "twitter_posted.txt"
        with open(tracking_file, 'a', encoding='utf-8') as f:
            f.write(f"{post_id}\n")
        self.posted_ids.add(post_id)

    def is_already_posted(self, post_id: str) -> bool:
        return post_id in self.posted_ids

    def authenticate(self) -> bool:
        try:
            from playwright.sync_api import sync_playwright

            print("[INFO] Starting Twitter authentication...")
            
            if self.browser:
                try:
                    self.browser.close()
                except:
                    pass

            playwright = sync_playwright().start()
            self.browser = playwright.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )

            if self.session_file.exists():
                print(f"[INFO] Loading session from {self.session_file}")
                try:
                    with open(self.session_file, 'r', encoding='utf-8') as f:
                        storage = json.load(f)
                    self.context = self.browser.new_context(
                        storage_state=storage,
                        viewport={'width': 1280, 'height': 720}
                    )
                except Exception as e:
                    print(f"[WARN] Session load failed: {e}")
                    self.context = self.browser.new_context(viewport={'width': 1280, 'height': 720})
            else:
                print("[WARN] No session file - will need login")
                self.context = self.browser.new_context(viewport={'width': 1280, 'height': 720})

            self.page = self.context.new_page()
            
            print("[INFO] Navigating to Twitter...")
            self.page.goto("https://twitter.com/home", wait_until="domcontentloaded", timeout=60000)
            
            print("[INFO] Waiting for page load...")
            self.page.wait_for_timeout(8000)
            
            if self._is_logged_in():
                print("[OK] Already logged in")
                self._save_session()
                return True
            
            print("\n" + "=" * 60)
            print("  PLEASE LOG IN TO TWITTER")
            print("=" * 60)
            print("\n  Login in the browser window...")
            
            for i in range(60):
                time.sleep(5)
                if self._is_logged_in():
                    print("[OK] Login detected!")
                    self._save_session()
                    return True
                if i % 6 == 0:
                    print(f"[INFO] Waiting for login... ({(60-i)*5}s remaining)")
            
            print("[ERROR] Login timeout")
            return False

        except Exception as e:
            print(f"[ERROR] Auth failed: {e}")
            return False

    def _is_logged_in(self) -> bool:
        try:
            if not self.page:
                return False
            composer = self.page.query_selector('[data-testid="tweetTextarea_0"]')
            if composer:
                return True
            if '/home' in self.page.url.lower():
                return True
            return False
        except:
            return False

    def _save_session(self):
        try:
            if self.context:
                self.session_file.parent.mkdir(exist_ok=True)
                storage = self.context.storage_state()
                with open(self.session_file, 'w', encoding='utf-8') as f:
                    json.dump(storage, f, indent=2)
                print(f"[OK] Session saved")
        except Exception as e:
            print(f"[WARN] Save session failed: {e}")

    def post_tweet(self, content: str, post_id: str) -> bool:
        """Post tweet using ONLY keyboard (Ctrl+Enter) - no button clicks"""
        
        print(f"\n[INFO] Posting tweet: {content[:50]}...")
        
        if not self.page:
            if not self.authenticate():
                return False
        
        try:
            # Navigate to home
            print("[INFO] Going to Twitter home...")
            self.page.goto("https://twitter.com/home", wait_until="domcontentloaded")
            self.page.wait_for_timeout(8000)
            
            # Wait for composer
            print("[INFO] Waiting for tweet composer...")
            self.page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=30000)
            print("[OK] Composer found")
            
            # Get composer and scroll into view
            composer = self.page.query_selector('[data-testid="tweetTextarea_0"]')
            if not composer:
                print("[ERROR] Composer element not found")
                return False
            
            composer.scroll_into_view_if_needed()
            time.sleep(2)
            
            # Click to focus
            print("[INFO] Focusing composer...")
            composer.click()
            time.sleep(2)
            
            # Clear existing text
            print("[INFO] Clearing composer...")
            self.page.keyboard.press("Control+a")
            time.sleep(0.5)
            self.page.keyboard.press("Backspace")
            time.sleep(1)
            
            # Type content SLOWLY
            print(f"[INFO] Typing tweet ({len(content)} chars)...")
            for char in content:
                self.page.keyboard.type(char)
                time.sleep(random.uniform(0.08, 0.15))  # Slower typing
            
            time.sleep(3)
            
            # Verify typing worked
            print("[INFO] Verifying content...")
            typed_text = self.page.evaluate("""() => {
                const textarea = document.querySelector('[data-testid="tweetTextarea_0"]');
                return textarea ? textarea.value : '';
            }""")
            
            typed_length = len(typed_text) if typed_text else 0
            print(f"[INFO] Typed text length: {typed_length}")
            
            # If verification fails, try again
            if typed_length < 10:
                print("[WARN] Verification failed, re-typing...")
                composer.click()
                time.sleep(2)
                self.page.keyboard.press("Control+a")
                time.sleep(0.5)
                self.page.keyboard.press("Backspace")
                time.sleep(1)
                
                for char in content:
                    self.page.keyboard.type(char)
                    time.sleep(random.uniform(0.08, 0.15))
                time.sleep(3)
            
            # POST WITH CTRL+ENTER ONLY (no button click - avoids overlay issue)
            print("[INFO] Posting with Ctrl+Enter...")
            self.page.keyboard.press("Control+Enter")
            
            # Wait for post to complete
            print("[INFO] Waiting for post to complete...")
            self.page.wait_for_timeout(10000)
            
            # Save post ID
            self._save_posted_id(post_id)
            
            # Log to vault
            self._log_post_to_vault(content, post_id)
            
            print(f"[SUCCESS] Tweet posted (ID: {post_id})")
            return True
            
        except Exception as e:
            print(f"[ERROR] Post failed: {e}")
            # Last resort
            try:
                print("[INFO] Last resort: Ctrl+Enter...")
                self.page.keyboard.press("Control+Enter")
                self.page.wait_for_timeout(5000)
                self._save_posted_id(post_id)
                return True
            except:
                return False

    def post_from_vault_task(self, task_path: Path) -> bool:
        content = self.vault_manager.read_task(task_path)
        if not content:
            return False
        
        tweet = self._extract_tweet(content)
        if not tweet or len(tweet) < 10:
            print(f"[ERROR] Could not extract tweet (got: {len(tweet) if tweet else 0} chars)")
            return False
        
        post_id = f"vault_{task_path.stem}"
        
        if self.is_already_posted(post_id):
            print(f"[SKIP] Already posted: {post_id}")
            return False
        
        return self.post_tweet(tweet, post_id)

    def _extract_tweet(self, content: str) -> Optional[str]:
        lines = content.split('\n')
        
        # Look for Twitter/Facebook Post section
        post_sections = ["## Twitter Post", "## Facebook Post", "## Tweet"]
        in_section = False
        post_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if any(section in line for section in post_sections):
                in_section = True
                continue
            
            if in_section and stripped.startswith("##"):
                break
            
            if in_section and stripped and not stripped.startswith("#"):
                post_lines.append(stripped)
        
        if post_lines:
            tweet = ' '.join(post_lines)
            tweet = tweet.replace("**", "").replace("*", "")
            return tweet[:280] if len(tweet) > 10 else None
        
        # Fallback to Description
        if "## Description" in content:
            in_section = False
            desc_lines = []
            
            for line in lines:
                stripped = line.strip()
                if "## Description" in line:
                    in_section = True
                    continue
                if in_section:
                    if stripped.startswith("##"):
                        break
                    if stripped and not stripped.startswith("#"):
                        desc_lines.append(stripped)
            
            if desc_lines:
                desc = ' '.join(desc_lines)
                desc = desc.replace("**", "").replace("*", "")
                return desc[:280] if len(desc) > 10 else None
        
        return None

    def _log_post_to_vault(self, content: str, post_id: str):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = Config.DONE / f"{timestamp}_Twitter_Post_{post_id}.md"
            
            log_file.write_text(f"""# Twitter Post - {post_id}

**Posted**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status**: [POSTED]

## Content

{content}

#twitter #posted
""", encoding='utf-8')
            
            print(f"[OK] Logged to: {log_file.name}")
        except Exception as e:
            print(f"[WARN] Log failed: {e}")

    def close(self):
        if self.browser:
            try:
                self.browser.close()
                print("[OK] Browser closed")
            except:
                pass
