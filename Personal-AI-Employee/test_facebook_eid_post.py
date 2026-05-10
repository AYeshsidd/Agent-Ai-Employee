#!/usr/bin/env python3
"""Test Facebook Post - Eid Mubarak"""
import sys
from pathlib import Path

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from skills.facebook_auto_post_skill import FacebookAutoPostSkill
from config import Config

print("\n" + "=" * 70)
print("  FACEBOOK AUTO-POST TEST - EID MUBARAK")
print("=" * 70)

# Test post content
eid_post = """Eid Mubarak to all those celebrating! 🌙✨

May this blessed occasion bring joy, peace, and prosperity to you and your loved ones. Wishing you moments filled with happiness and togetherness.

#EidMubarak #Eid2026 #Celebration #Blessings"""

post_id = "test_eid_mubarak_2026"

print(f"\n[INFO] Post content length: {len(eid_post)} characters")
print(f"[INFO] Post ID: {post_id}")

# Check session
session_file = Config.BASE_DIR / "credentials" / "facebook_session.json"
if session_file.exists():
    print(f"\n[OK] Facebook session found: {session_file}")
else:
    print(f"\n[WARN] No Facebook session - will require login")

print("\n[INFO] Starting Facebook auto-post...")
print("[INFO] Browser will open - please wait for login if needed\n")

# Create skill and post
skill = FacebookAutoPostSkill()

print("[STEP 1] Authenticating with Facebook...")
if not skill.authenticate():
    print("\n[ERROR] Authentication failed")
    sys.exit(1)

print("\n[STEP 2] Posting to Facebook...")
success = skill.post_to_facebook(eid_post, post_id)

if success:
    print("\n" + "=" * 70)
    print("  POST SUCCESSFUL!")
    print("=" * 70)
    print(f"\n[OK] Eid Mubarak post published to Facebook")
    print(f"[OK] Post ID tracked: {post_id}")
    print(f"[INFO] Check Vault/Done for log file")
    print("=" * 70)
else:
    print("\n" + "=" * 70)
    print("  POST FAILED")
    print("=" * 70)
    print("\n[ERROR] Could not complete the post")
    print("[INFO] Check browser for any errors")
    print("=" * 70)

skill.close()
