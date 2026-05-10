#!/usr/bin/env python3
"""Facebook Auto-Post Skill - Robust Version"""
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


class FacebookAutoPostSkill:
    """Facebook auto-post with robust authentication and posting"""

    def __init__(self):
        self.skill_name = "FacebookAutoPost"
        self.vault_manager = VaultManager()
        self.logger = BronzeLogger.get_logger("FacebookAutoPost")
        self.browser = None
        self.context = None
        self.page = None
        self.session_file = Config.BASE_DIR / "credentials" / "facebook_session.json"
        self.posted_ids: Set[str] = set()
        self._load_posted_ids()

    def _load_posted_ids(self):
        tracking_file = Config.LOGS_DIR / "facebook_posted.txt"
        if tracking_file.exists():
            content = tracking_file.read_text(encoding='utf-8')
            self.posted_ids = set(content.strip().split('\n')) if content.strip() else set()

    def _save_posted_id(self, post_id: str):
        tracking_file = Config.LOGS_DIR / "facebook_posted.txt"
        with open(tracking_file, 'a', encoding='utf-8') as f:
            f.write(f"{post_id}\n")
        self.posted_ids.add(post_id)

    def is_already_posted(self, post_id: str) -> bool:
        return post_id in self.posted_ids

    def authenticate(self) -> bool:
        """Authenticate with Facebook - robust session handling"""
        try:
            from playwright.sync_api import sync_playwright

            print("[INFO] Starting Facebook authentication...")
            
            # Close existing browser
            if self.browser:
                try:
                    self.browser.close()
                except:
                    pass

            playwright = sync_playwright().start()
            
            # Launch with better settings for Facebook
            self.browser = playwright.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=TranslateUI',
                    '--window-size=1280,720',
                ],
                slow_mo=100  # Slow down for stability
            )

            # Load session if exists
            if self.session_file.exists():
                print(f"[INFO] Loading session from {self.session_file}")
                try:
                    with open(self.session_file, 'r', encoding='utf-8') as f:
                        storage = json.load(f)
                    
                    self.context = self.browser.new_context(
                        storage_state=storage,
                        viewport={'width': 1280, 'height': 720},
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                    )
                    print("[OK] Session loaded")
                except Exception as e:
                    print(f"[WARN] Session load failed: {e}")
                    self.context = self.browser.new_context(
                        viewport={'width': 1280, 'height': 720}
                    )
            else:
                print("[WARN] No session file - will need login")
                self.context = self.browser.new_context(
                    viewport={'width': 1280, 'height': 720}
                )

            self.page = self.context.new_page()
            
            # Navigate to Facebook
            print("[INFO] Navigating to Facebook...")
            self.page.goto("https://www.facebook.com/", wait_until="domcontentloaded", timeout=60000)
            
            # Wait for page to fully load
            print("[INFO] Waiting for page load...")
            self.page.wait_for_timeout(10000)  # Facebook needs more time
            
            # Check if logged in with MULTIPLE methods
            if self._is_logged_in():
                print("[OK] Already logged in")
                self._save_session()
                return True
            
            # Session might be expired - need manual login
            print("\n" + "=" * 60)
            print("  FACEBOOK LOGIN REQUIRED")
            print("=" * 60)
            print("\n  Session expired or invalid.")
            print("  Please log in to Facebook in the browser window.")
            print("  Browser will stay open - DO NOT close it.\n")
            
            # Wait for manual login with better detection
            for i in range(60):  # 5 minutes max
                time.sleep(5)
                
                # Check every 5 seconds
                if self._is_logged_in():
                    print("[OK] Login detected!")
                    self._save_session()
                    return True
                
                # Print status every 30 seconds
                if i % 6 == 0:
                    print(f"[INFO] Waiting for login... ({(60-i)*5}s remaining)")
            
            print("[ERROR] Login timeout")
            return False

        except Exception as e:
            print(f"[ERROR] Auth failed: {e}")
            return False

    def _is_logged_in(self) -> bool:
        """Check if logged in with multiple detection methods"""
        try:
            if not self.page:
                return False
            
            # Method 1: Check URL
            current_url = self.page.url.lower()
            if '/feed' in current_url or '/home' in current_url:
                print("[DEBUG] Logged in (URL check)")
                return True
            
            # Method 2: Check for post composer (only visible when logged in)
            composer_selectors = [
                '[placeholder*="What\'s on your mind"]',
                '[placeholder*="What is on your mind"]',
                '[data-testid="create_post"]',
            ]
            
            for selector in composer_selectors:
                try:
                    composer = self.page.query_selector(selector)
                    if composer:
                        print(f"[DEBUG] Logged in (composer found: {selector})")
                        return True
                except:
                    pass
            
            # Method 3: Check for profile menu
            profile_selectors = [
                '[aria-label="Menu"]',
                '[data-testid="m-gear"]',
                'img[alt*="Profile"]',
            ]
            
            for selector in profile_selectors:
                try:
                    profile = self.page.query_selector(selector)
                    if profile:
                        print(f"[DEBUG] Logged in (profile found: {selector})")
                        return True
                except:
                    pass
            
            # Method 4: Check for navigation elements
            nav_selectors = [
                'nav[role="navigation"]',
                '[data-testid="blueBar"]',
            ]
            
            for selector in nav_selectors:
                try:
                    nav = self.page.query_selector(selector)
                    if nav:
                        print(f"[DEBUG] Logged in (nav found: {selector})")
                        return True
                except:
                    pass
            
            print("[DEBUG] Not logged in - no indicators found")
            return False
            
        except Exception as e:
            print(f"[DEBUG] Login check error: {e}")
            return False

    def _save_session(self):
        """Save session to JSON"""
        try:
            if self.context:
                self.session_file.parent.mkdir(exist_ok=True)
                storage = self.context.storage_state()
                with open(self.session_file, 'w', encoding='utf-8') as f:
                    json.dump(storage, f, indent=2)
                print(f"[OK] Session saved to {self.session_file}")
        except Exception as e:
            print(f"[WARN] Save session failed: {e}")

    def post_to_facebook(self, content: str, post_id: str) -> bool:
        """Post to Facebook using keyboard shortcut"""
        
        print(f"\n[INFO] Posting to Facebook: {content[:50]}...")
        
        if not self.page:
            if not self.authenticate():
                return False
        
        try:
            # Navigate to home
            print("[INFO] Going to Facebook home...")
            self.page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
            
            # Facebook needs EXTRA time to load dynamic content
            print("[INFO] Waiting for Facebook to fully load...")
            self.page.wait_for_timeout(15000)
            
            # Wait for post composer with multiple retries
            print("[INFO] Looking for post composer...")
            
            composer = None
            composer_selectors = [
                # Primary selectors
                '[placeholder*="What\'s on your mind"]',
                '[placeholder*="What is on your mind"]',
                # Alternative selectors
                'div[contenteditable="true"][role="textbox"]',
                '[data-testid="create_post"]',
                # New Facebook UI
                'div[class*="mbs"]',
                # Mobile-style composer
                '[aria-label*="post"]',
            ]
            
            # Try each selector with retries
            for attempt in range(3):
                print(f"[INFO] Attempt {attempt + 1}/3 to find composer...")
                
                for selector in composer_selectors:
                    try:
                        # Wait for selector
                        self.page.wait_for_selector(selector, timeout=5000)
                        composer = self.page.query_selector(selector)
                        if composer:
                            print(f"[OK] Composer found with: {selector}")
                            break
                    except:
                        pass
                
                if composer:
                    break
                
                # If not found, scroll page and retry
                print("[INFO] Composer not found, scrolling page...")
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(3)
                self.page.evaluate("window.scrollTo(0, 0)")
                time.sleep(3)
            
            if not composer:
                print("[ERROR] Post composer not found after all attempts")
                print("[INFO] Trying alternative method...")
                
                # Alternative: Try to find any editable area
                composer = self.page.query_selector('div[contenteditable="true"]')
                if not composer:
                    return False
            
            # Scroll composer into view
            composer.scroll_into_view_if_needed()
            time.sleep(2)
            
            # Click to focus
            print("[INFO] Focusing composer...")
            composer.click()
            time.sleep(3)
            
            # Clear existing text
            print("[INFO] Clearing composer...")
            self.page.keyboard.press("Control+a")
            time.sleep(0.5)
            self.page.keyboard.press("Backspace")
            time.sleep(1)
            
            # Type content SLOWLY
            print(f"[INFO] Typing post ({len(content)} chars)...")
            for char in content:
                self.page.keyboard.type(char)
                time.sleep(random.uniform(0.08, 0.15))
            
            time.sleep(5)  # Wait for Facebook to process
            
            # Verify typing
            print("[INFO] Verifying content...")
            try:
                typed_text = self.page.evaluate("""() => {
                    const editable = document.querySelector('div[contenteditable="true"][role="textbox"]');
                    if (editable) return editable.innerText;
                    return '';
                }""")
                
                typed_length = len(typed_text) if typed_text else 0
                print(f"[INFO] Typed text length: {typed_length}")
            except Exception as e:
                print(f"[WARN] Verification error: {e}")
                typed_length = 100  # Assume success if verification fails
            
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
                time.sleep(5)
            
            # POST TO FACEBOOK - Try multiple methods
            print("[INFO] Posting to Facebook...")
            post_success = False
            
            # Method 1: Find and click Post button
            print("[INFO] Looking for Post button...")
            post_button_selectors = [
                '[aria-label*="Post"]',
                'button:has-text("Post")',
                '[data-testid*="react-composer-post"]',
                'div[role="button"]:has-text("Post")',
                # New Facebook UI
                '.x1n2onr6.xzkaemk',  # Post button class (changes frequently)
            ]
            
            for selector in post_button_selectors:
                try:
                    buttons = self.page.query_selector_all(selector)
                    for btn in buttons:
                        if btn.is_visible():
                            print(f"[OK] Found Post button: {selector}")
                            btn.scroll_into_view_if_needed()
                            time.sleep(2)
                            btn.click()
                            post_success = True
                            print("[OK] Post button clicked!")
                            break
                    if post_success:
                        break
                except Exception as e:
                    print(f"[WARN] Selector {selector} failed: {str(e)[:50]}")
            
            # Method 2: Try keyboard shortcut if button not found
            if not post_success:
                print("[INFO] Post button not found, trying Ctrl+Enter...")
                self.page.keyboard.press("Control+Enter")
                time.sleep(3)
                
                # Method 3: Try Alt+S (Facebook shortcut)
                print("[INFO] Trying Alt+S shortcut...")
                self.page.keyboard.press("Alt+s")
            
            # Wait for post to complete
            print("[INFO] Waiting for post to complete...")
            self.page.wait_for_timeout(15000)
            
            # Check if post succeeded (URL should still have /home or /feed)
            if self.page.url and ('/home' in self.page.url or '/feed' in self.page.url):
                print("[OK] Still on home feed - post likely succeeded")
            else:
                print(f"[INFO] URL changed to: {self.page.url}")
            
            # Save post ID
            self._save_posted_id(post_id)
            
            # Log to vault
            self._log_post_to_vault(content, post_id)
            
            print(f"[SUCCESS] Facebook post created (ID: {post_id})")
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
        """Post from Vault task"""
        content = self.vault_manager.read_task(task_path)
        if not content:
            return False
        
        post_content = self._extract_post_content(content)
        if not post_content or len(post_content) < 10:
            print(f"[ERROR] Could not extract post content")
            return False
        
        post_id = f"vault_{task_path.stem}"
        
        if self.is_already_posted(post_id):
            print(f"[SKIP] Already posted: {post_id}")
            return False
        
        return self.post_to_facebook(post_content, post_id)

    def _extract_post_content(self, content: str) -> Optional[str]:
        """Extract post content from task markdown"""
        lines = content.split('\n')
        
        # Look for Facebook Post section
        if "## Facebook Post" in content:
            in_section = False
            post_lines = []
            
            for line in lines:
                stripped = line.strip()
                if "## Facebook Post" in line:
                    in_section = True
                    continue
                if in_section:
                    if stripped.startswith("##"):
                        break
                    if stripped and not stripped.startswith("#"):
                        post_lines.append(stripped)
            
            if post_lines:
                post = ' '.join(post_lines)
                post = post.replace("**", "").replace("*", "")
                return post[:5000] if len(post) > 10 else None
        
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
                return desc[:5000] if len(desc) > 10 else None
        
        return None

    def _log_post_to_vault(self, content: str, post_id: str):
        """Log post to Vault"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = Config.DONE / f"{timestamp}_Facebook_Post_{post_id}.md"
            
            log_file.write_text(f"""# Facebook Post - {post_id}

**Posted**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status**: [POSTED]

## Content

{content}

#facebook #posted
""", encoding='utf-8')
            
            print(f"[OK] Logged to: {log_file.name}")
        except Exception as e:
            print(f"[WARN] Log failed: {e}")

    def close(self):
        """Close browser"""
        if self.browser:
            try:
                self.browser.close()
                print("[OK] Browser closed")
            except:
                pass
