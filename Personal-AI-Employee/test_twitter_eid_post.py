#!/usr/bin/env python3
"""Test Twitter Eid Mubarak Post"""
import sys
from pathlib import Path

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from skills.twitter_auto_post_skill import TwitterAutoPostSkill
from config import Config

print("\n" + "=" * 70)
print("  TWITTER AUTO-POST TEST - EID MUBARAK")
print("=" * 70)

# Test post content (must be under 280 characters for Twitter)
eid_tweet = """Eid Mubarak to all celebrating! 🌙✨ May this blessed occasion bring joy, peace, and prosperity to you and your loved ones. #EidMubarak #Eid2026 #Blessings"""

post_id = "eid_mubarak_test_2026"

print(f"\n[INFO] Tweet length: {len(eid_tweet)} characters (max: 280)")
print(f"[INFO] Post ID: {post_id}")

# Check session
session_file = Config.BASE_DIR / "credentials" / "twitter_session.json"
if session_file.exists():
    print(f"\n[OK] Twitter session found: {session_file}")
    import json
    with open(session_file) as f:
        session = json.load(f)
    print(f"     Cookies: {len(session.get('cookies', []))}")
else:
    print(f"\n[WARN] No Twitter session - will require manual login")

print("\n[INFO] Starting Twitter auto-post...")
print("[INFO] Browser will open - please wait for login if needed\n")

# Create skill and post
skill = TwitterAutoPostSkill()

print("[STEP 1] Authenticating with Twitter...")
if not skill.authenticate():
    print("\n[ERROR] Authentication failed")
    sys.exit(1)

print("\n[STEP 2] Posting tweet...")
success = skill.post_tweet(eid_tweet, post_id)

if success:
    print("\n" + "=" * 70)
    print("  TWEET POSTED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\n[OK] Eid Mubarak tweet published")
    print(f"[OK] Post ID tracked: {post_id}")
    print(f"[INFO] Check Vault/Done for log file")
    print("=" * 70)
else:
    print("\n" + "=" * 70)
    print("  TWEET POST FAILED")
    print("=" * 70)
    print("\n[ERROR] Could not complete the post")
    print("[INFO] Check browser for any errors")
    print("=" * 70)

skill.close()
print("\n[OK] Test complete\n")
