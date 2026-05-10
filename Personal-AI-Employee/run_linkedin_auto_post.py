#!/usr/bin/env python3
"""Silver Tier Part 2 - LinkedIn Auto Post Runner"""
import sys
from pathlib import Path

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from vault_manager import VaultManager
from bronze_logger import BronzeLogger
from skills.linkedin_auto_post_skill import LinkedInAutoPostSkill
from config import Config


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def post_predefined_content():
    """Post predefined business updates"""
    print_section("Posting Predefined Content")

    skill = LinkedInAutoPostSkill()

    # Example business updates
    posts = [
        {
            "id": "update_001",
            "content": """🚀 Excited to share our latest innovation in AI-powered task management!

Our new system automates workflow processing across multiple channels, helping teams stay organized and productive.

Key features:
✅ Multi-channel monitoring (Email, LinkedIn, WhatsApp)
✅ Intelligent task analysis
✅ Automated prioritization
✅ Seamless integration

Interested in learning more? Let's connect!

#AI #Automation #Productivity #Innovation"""
        },
        {
            "id": "update_002",
            "content": """💡 Did you know? Automating repetitive tasks can save your team up to 40% of their time.

We're building solutions that help businesses focus on what matters most - growth and innovation.

What's your biggest productivity challenge? Drop a comment below! 👇

#BusinessAutomation #Efficiency #TechSolutions"""
        }
    ]

    for post in posts:
        print(f"\n[INFO] Processing post: {post['id']}")

        if skill.is_already_posted(post['id']):
            print(f"[SKIP] Already posted: {post['id']}")
            continue

        print(f"[INFO] Content preview: {post['content'][:100]}...")

        success = skill.post_to_linkedin(post['content'], post['id'])

        if success:
            print(f"[SUCCESS] Posted: {post['id']}")
        else:
            print(f"[FAILED] Could not post: {post['id']}")

        # Wait between posts to avoid rate limiting
        if len(posts) > 1:
            print("[INFO] Waiting 60 seconds before next post...")
            import time
            time.sleep(60)

    skill.close()


def post_from_vault():
    """Post content from Vault tasks"""
    print_section("Posting from Vault Tasks")

    skill = LinkedInAutoPostSkill()
    vault_mgr = VaultManager()

    # Look for tasks tagged with #linkedin-post
    needs_action_tasks = vault_mgr.list_tasks("needs_action")

    linkedin_tasks = []
    for task_path in needs_action_tasks:
        content = vault_mgr.read_task(task_path)
        if content and "#linkedin-post" in content.lower():
            linkedin_tasks.append(task_path)

    if not linkedin_tasks:
        print("[INFO] No tasks found with #linkedin-post tag")
        skill.close()
        return

    print(f"[INFO] Found {len(linkedin_tasks)} task(s) to post")

    for task_path in linkedin_tasks:
        print(f"\n[INFO] Processing: {task_path.name}")

        success = skill.post_from_vault_task(task_path)

        if success:
            print(f"[SUCCESS] Posted from task: {task_path.name}")

            # Move task to Done
            vault_mgr.move_task(task_path, "done")
            print(f"[INFO] Moved task to Done")
        else:
            print(f"[FAILED] Could not post from task: {task_path.name}")

        # Wait between posts
        if len(linkedin_tasks) > 1:
            print("[INFO] Waiting 60 seconds before next post...")
            import time
            time.sleep(60)

    skill.close()


def create_sample_post_task():
    """Create a sample task for LinkedIn posting"""
    print_section("Creating Sample LinkedIn Post Task")

    vault_mgr = VaultManager()

    sample_content = """# LinkedIn Post: New Product Launch

**Status**: [TODO]
**Priority**: High
**Created**: 2026-02-22

## Description

Announce our new AI-powered automation platform to LinkedIn audience.

## LinkedIn Post

🎉 Big news! We're launching our AI-powered automation platform!

Transform your workflow with:
🤖 Intelligent task management
📊 Real-time analytics
🔗 Multi-channel integration
⚡ Lightning-fast processing

Early access available now! Comment "INTERESTED" to learn more.

#ProductLaunch #AI #Automation #Innovation #TechNews

## Action Items

- [ ] Review post content
- [ ] Schedule posting time
- [ ] Monitor engagement

#linkedin-post #marketing #announcement
"""

    task_path = vault_mgr.write_task(
        sample_content,
        folder="needs_action",
        filename="linkedin_post_sample.md"
    )

    if task_path:
        print(f"[SUCCESS] Created sample task: {task_path.name}")
        print(f"[INFO] Task location: {task_path}")
        print(f"[INFO] Task is tagged with #linkedin-post")
    else:
        print("[FAILED] Could not create sample task")


def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("  Silver Tier Part 2 - LinkedIn Auto Post")
    print("=" * 70)

    # Initialize vault
    VaultManager.initialize()

    print("\nOptions:")
    print("1. Post predefined content")
    print("2. Post from Vault tasks")
    print("3. Create sample post task")
    print("4. Exit")

    choice = input("\nSelect option (1-4): ").strip()

    if choice == "1":
        post_predefined_content()
    elif choice == "2":
        post_from_vault()
    elif choice == "3":
        create_sample_post_task()
    elif choice == "4":
        print("\nExiting...")
    else:
        print("\n[ERROR] Invalid option")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
