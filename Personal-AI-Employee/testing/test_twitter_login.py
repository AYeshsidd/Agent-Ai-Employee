#!/usr/bin/env python3
"""
Twitter/X Login Test Script

This script will help you log in to Twitter/X and save your credentials.

IMPORTANT: 
- A browser window will open
- You need to manually log in with your credentials
- The script will wait up to 5 minutes
- After successful login, credentials are saved automatically
"""
import sys
from pathlib import Path

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from skills.watcher_skills.twitter_watcher_skill import TwitterWatcherSkill
from vault_manager import VaultManager


def main():
    print("\n" + "=" * 70)
    print("  TWITTER/X LOGIN TEST")
    print("=" * 70)
    
    # Initialize vault
    VaultManager.initialize()
    
    # Create watcher
    watcher = TwitterWatcherSkill()
    
    print("\n[INFO] Profile location:", watcher.user_data_dir)
    print("[INFO] Browser will open in 3 seconds...")
    
    import time
    time.sleep(3)
    
    print("\n" + "=" * 70)
    print("  LOGIN INSTRUCTIONS")
    print("=" * 70)
    print("\n  A Chromium browser window should have opened.")
    print("\n  Please follow these steps:")
    print("  1. If you see Twitter login page, enter your credentials")
    print("  2. Enter username/email: ayesh_sidd")
    print("  3. Enter password: [your password]")
    print("  4. Complete any 2FA verification if prompted")
    print("  5. Wait until you see your Twitter home timeline")
    print("\n  [INFO] The script will detect login automatically")
    print("  [INFO] After successful login, close the script with Ctrl+C")
    print("=" * 70)
    
    try:
        # Start authentication
        print("\n[INFO] Starting authentication process...\n")
        success = watcher.authenticate()
        
        if success:
            print("\n" + "=" * 70)
            print("  LOGIN SUCCESSFUL!")
            print("=" * 70)
            print(f"\n[OK] Twitter/X authentication complete")
            print(f"[OK] Profile saved to: {watcher.user_data_dir}")
            print(f"\n[INFO] Future runs will auto-login using this profile")
            print("[INFO] You can now run: python run_twitter_watcher.py")
            print("=" * 70)
            
            # Test if we can access Twitter
            print("\n[INFO] Testing Twitter access...")
            if watcher.page:
                watcher.page.goto("https://twitter.com/home", wait_until="domcontentloaded")
                time.sleep(3)
                print(f"[OK] Current URL: {watcher.page.url}")
                
                if watcher._check_if_logged_in():
                    print("[OK] Login confirmed - you are logged in!")
                else:
                    print("[WARN] May not be fully logged in yet")
        else:
            print("\n" + "=" * 70)
            print("  LOGIN FAILED")
            print("=" * 70)
            print("\n[ERROR] Authentication was not completed")
            print("\nPossible reasons:")
            print("  1. Browser didn't open - check if Playwright is installed")
            print("  2. Login took too long - timeout after 5 minutes")
            print("  3. Network issues - check your internet connection")
            print("  4. X blocked the login attempt - try again")
            print("\n[INFO] Try running this script again")
            print("=" * 70)
            
    except KeyboardInterrupt:
        print("\n\n[INFO] Script interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Script failed: {str(e)}")
        print("\n[INFO] Please check the error message above")
    finally:
        # Cleanup
        print("\n[INFO] Cleaning up...")
        watcher.close()
        print("[OK] Done!")


if __name__ == "__main__":
    main()
