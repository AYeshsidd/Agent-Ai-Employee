from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import sys
# Ensure project root is in sys.path
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from vault_manager import VaultManager
from config import Config
from bronze_logger import BronzeLogger


class WriteVaultSkill:
    """Agent skill for writing and managing tasks in Vault folders"""

    def __init__(self):
        self.vault_manager = VaultManager()
        self.logger = BronzeLogger.get_logger("WriteVaultSkill")

    def create_task(self, title: str, description: str, folder: str = "inbox",
                   priority: str = "Medium", action_items: list = None,
                   tags: list = None) -> Optional[Path]:
        """
        Create new task in specified folder

        Args:
            title: Task title
            description: Task description
            folder: Target folder (inbox, needs_action, done)
            priority: Task priority (Urgent, High, Medium, Low, Minimal)
            action_items: List of action items
            tags: List of tags

        Returns:
            Path to created task or None if error
        """
        BronzeLogger.log_skill_execution(
            self.logger, "WriteVaultSkill", f"create_task('{title}')",
            "IN_PROGRESS", f"Creating in {folder}"
        )

        content = self._format_task(title, description, priority, action_items, tags)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() or c in (" ", "_") else "_" for c in title)
        safe_title = "_".join(safe_title.split())[:50]
        filename = f"{timestamp}_{safe_title}.md"

        task_path = self.vault_manager.write_task(content, folder, filename)

        if task_path:
            BronzeLogger.log_skill_execution(
                self.logger, "WriteVaultSkill", f"create_task('{title}')",
                "SUCCESS", f"Created {filename} in {folder}"
            )
        else:
            BronzeLogger.log_skill_execution(
                self.logger, "WriteVaultSkill", f"create_task('{title}')",
                "FAILED", "Task creation failed"
            )

        return task_path

    def update_task(self, task_path: Path, updates: Dict[str, str]) -> bool:
        """
        Update existing task with new content

        Args:
            task_path: Path to task file
            updates: Dictionary with fields to update

        Returns:
            True if successful, False otherwise
        """
        BronzeLogger.log_skill_execution(
            self.logger, "WriteVaultSkill", f"update_task({task_path.name})",
            "IN_PROGRESS", f"Updating fields: {', '.join(updates.keys())}"
        )

        try:
            content = self.vault_manager.read_task(task_path)
            if not content:
                BronzeLogger.log_skill_execution(
                    self.logger, "WriteVaultSkill", f"update_task({task_path.name})",
                    "FAILED", "Could not read task"
                )
                return False

            lines = content.split("\n")
            updated_lines = []

            for line in lines:
                updated_line = line

                if "**Status**:" in line and "status" in updates:
                    updated_line = f"**Status**: {updates['status']}"
                elif "**Priority**:" in line and "priority" in updates:
                    updated_line = f"**Priority**: {updates['priority']}"
                elif "**Complexity**:" in line and "complexity" in updates:
                    updated_line = f"**Complexity**: {updates['complexity']}"

                updated_lines.append(updated_line)

            updated_content = "\n".join(updated_lines)
            task_path.write_text(updated_content, encoding="utf-8")

            BronzeLogger.log_task_action(
                self.logger, "UPDATE", task_path.name, "WriteVaultSkill",
                "SUCCESS", f"Updated: {', '.join(updates.keys())}"
            )
            BronzeLogger.log_skill_execution(
                self.logger, "WriteVaultSkill", f"update_task({task_path.name})",
                "SUCCESS", "Task updated successfully"
            )
            return True

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "WriteVaultSkill", f"update_task({task_path.name})",
                "FAILED", str(e)
            )
            return False

    def move_task_to_folder(self, task_path: Path, target_folder: str) -> Optional[Path]:
        """
        Move task to different folder

        Args:
            task_path: Current task path
            target_folder: Target folder (inbox, needs_action, done)

        Returns:
            New task path or None if error
        """
        BronzeLogger.log_skill_execution(
            self.logger, "WriteVaultSkill", f"move_task_to_folder({task_path.name})",
            "IN_PROGRESS", f"Moving to {target_folder}"
        )

        new_path = self.vault_manager.move_task(task_path, target_folder)

        if new_path:
            BronzeLogger.log_skill_execution(
                self.logger, "WriteVaultSkill", f"move_task_to_folder({task_path.name})",
                "SUCCESS", f"Moved to {target_folder}"
            )
        else:
            BronzeLogger.log_skill_execution(
                self.logger, "WriteVaultSkill", f"move_task_to_folder({task_path.name})",
                "FAILED", "Move operation failed"
            )

        return new_path

    def mark_task_complete(self, task_path: Path) -> Optional[Path]:
        """
        Mark task as complete and move to Done folder

        Args:
            task_path: Path to task file

        Returns:
            New path in Done folder or None if error
        """
        BronzeLogger.log_skill_execution(
            self.logger, "WriteVaultSkill", f"mark_task_complete({task_path.name})",
            "IN_PROGRESS", "Marking as complete"
        )

        self.update_task(task_path, {"status": "[DONE]"})
        new_path = self.move_task_to_folder(task_path, "done")

        if new_path:
            BronzeLogger.log_skill_execution(
                self.logger, "WriteVaultSkill", f"mark_task_complete({task_path.name})",
                "SUCCESS", "Task marked complete and moved to Done"
            )
        else:
            BronzeLogger.log_skill_execution(
                self.logger, "WriteVaultSkill", f"mark_task_complete({task_path.name})",
                "FAILED", "Could not complete task"
            )

        return new_path

    def delete_task(self, task_path: Path) -> bool:
        """
        Delete task file

        Args:
            task_path: Path to task file

        Returns:
            True if successful, False otherwise
        """
        BronzeLogger.log_skill_execution(
            self.logger, "WriteVaultSkill", f"delete_task({task_path.name})",
            "IN_PROGRESS", "Deleting task"
        )

        success = self.vault_manager.delete_task(task_path)

        if success:
            BronzeLogger.log_skill_execution(
                self.logger, "WriteVaultSkill", f"delete_task({task_path.name})",
                "SUCCESS", "Task deleted"
            )
        else:
            BronzeLogger.log_skill_execution(
                self.logger, "WriteVaultSkill", f"delete_task({task_path.name})",
                "FAILED", "Delete operation failed"
            )

        return success

    def add_action_item(self, task_path: Path, action_item: str) -> bool:
        """
        Add action item to existing task

        Args:
            task_path: Path to task file
            action_item: Action item text

        Returns:
            True if successful, False otherwise
        """
        BronzeLogger.log_skill_execution(
            self.logger, "WriteVaultSkill", f"add_action_item({task_path.name})",
            "IN_PROGRESS", f"Adding: {action_item[:50]}..."
        )

        try:
            content = self.vault_manager.read_task(task_path)
            if not content:
                BronzeLogger.log_skill_execution(
                    self.logger, "WriteVaultSkill", f"add_action_item({task_path.name})",
                    "FAILED", "Could not read task"
                )
                return False

            lines = content.split("\n")
            action_section_found = False
            insert_index = -1

            for i, line in enumerate(lines):
                if "## Action Items" in line:
                    action_section_found = True
                    insert_index = i + 2
                    break

            if action_section_found and insert_index > 0:
                lines.insert(insert_index, f"- [ ] {action_item}")
                updated_content = "\n".join(lines)
                task_path.write_text(updated_content, encoding="utf-8")

                BronzeLogger.log_task_action(
                    self.logger, "UPDATE", task_path.name, "WriteVaultSkill",
                    "SUCCESS", f"Added action item"
                )
                BronzeLogger.log_skill_execution(
                    self.logger, "WriteVaultSkill", f"add_action_item({task_path.name})",
                    "SUCCESS", "Action item added"
                )
                return True

            BronzeLogger.log_skill_execution(
                self.logger, "WriteVaultSkill", f"add_action_item({task_path.name})",
                "FAILED", "Action Items section not found"
            )
            return False

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "WriteVaultSkill", f"add_action_item({task_path.name})",
                "FAILED", str(e)
            )
            return False

    def _format_task(self, title: str, description: str, priority: str,
                    action_items: list = None, tags: list = None) -> str:
        """Format task as markdown"""
        timestamp = datetime.now().isoformat()

        content = f"""# {title}

**Status**: [TODO]
**Priority**: {priority}
**Created**: {timestamp}

## Description

{description}

## Action Items

"""

        if action_items:
            for item in action_items:
                content += f"- [ ] {item}\n"
        else:
            content += "- [ ] Define action items\n"

        if tags:
            content += f"\n## Tags\n\n{' '.join(f'#{tag}' for tag in tags)}\n"

        return content
