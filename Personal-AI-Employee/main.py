#!/usr/bin/env python3
from pathlib import Path
import sys

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from config import Config
from vault_manager import VaultManager
from skills import TaskAnalyzerSkill, VaultWriterSkill


def process_inbox():
    """Process all markdown files in Inbox folder"""
    analyzer = TaskAnalyzerSkill()
    writer = VaultWriterSkill()

    markdown_files = list(Config.INBOX.glob("*.md"))

    if not markdown_files:
        print("No tasks found in Inbox")
        return

    print(f"Found {len(markdown_files)} task(s) in Inbox\n")

    for task_file in markdown_files:
        print(f"Processing: {task_file.name}")

        task_content = task_file.read_text(encoding="utf-8")

        task_data = analyzer.analyze(task_content, task_file)

        output_path = writer.write_to_needs_action(task_data)

        task_file.unlink()

        print(f"  [OK] Analyzed and moved to: {output_path.name}")
        print(f"  Priority: {task_data['priority']}/5")
        print(f"  Complexity: {task_data['complexity']}")
        print(f"  Action Items: {len(task_data['action_items'])}\n")

    print(f"Processed {len(markdown_files)} task(s) successfully")


def main():
    """Main entry point"""
    print("=" * 60)
    print("Bronze-tier Vault System")
    print("=" * 60)
    print()

    VaultManager.initialize()

    process_inbox()


if __name__ == "__main__":
    main()
