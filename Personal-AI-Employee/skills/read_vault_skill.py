from pathlib import Path
from typing import List, Dict, Optional
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from vault_manager import VaultManager
from config import Config
from bronze_logger import BronzeLogger


class ReadVaultSkill:
    """Agent skill for reading tasks from Vault folders"""

    def __init__(self):
        self.vault_manager = VaultManager()
        self.logger = BronzeLogger.get_logger("ReadVaultSkill")

    def read_all_tasks(self, folder: str = "needs_action") -> List[Dict[str, str]]:
        """
        Read all tasks from specified folder

        Args:
            folder: Target folder (inbox, needs_action, done)

        Returns:
            List of task dictionaries with path and content
        """
        BronzeLogger.log_skill_execution(
            self.logger, "ReadVaultSkill", f"read_all_tasks({folder})",
            "IN_PROGRESS", f"Reading tasks from {folder}"
        )

        tasks = []
        task_paths = self.vault_manager.list_tasks(folder)

        for task_path in task_paths:
            content = self.vault_manager.read_task(task_path)
            if content:
                tasks.append({
                    "filename": task_path.name,
                    "path": str(task_path),
                    "content": content,
                    "folder": folder
                })

        BronzeLogger.log_skill_execution(
            self.logger, "ReadVaultSkill", f"read_all_tasks({folder})",
            "SUCCESS", f"Read {len(tasks)} tasks"
        )
        return tasks

    def read_task_by_name(self, filename: str, folder: str = "needs_action") -> Optional[Dict[str, str]]:
        """
        Read specific task by filename

        Args:
            filename: Task filename
            folder: Target folder (inbox, needs_action, done)

        Returns:
            Task dictionary or None if not found
        """
        BronzeLogger.log_skill_execution(
            self.logger, "ReadVaultSkill", f"read_task_by_name({filename})",
            "IN_PROGRESS", f"Searching in {folder}"
        )

        folder_map = {
            "inbox": Config.INBOX,
            "needs_action": Config.NEEDS_ACTION,
            "done": Config.DONE
        }

        target_folder = folder_map.get(folder.lower())
        if not target_folder:
            BronzeLogger.log_skill_execution(
                self.logger, "ReadVaultSkill", f"read_task_by_name({filename})",
                "FAILED", f"Invalid folder: {folder}"
            )
            return None

        task_path = target_folder / filename
        if not task_path.exists():
            BronzeLogger.log_skill_execution(
                self.logger, "ReadVaultSkill", f"read_task_by_name({filename})",
                "FAILED", f"Task not found in {folder}"
            )
            return None

        content = self.vault_manager.read_task(task_path)
        if content:
            BronzeLogger.log_skill_execution(
                self.logger, "ReadVaultSkill", f"read_task_by_name({filename})",
                "SUCCESS", f"Found in {folder}"
            )
            return {
                "filename": filename,
                "path": str(task_path),
                "content": content,
                "folder": folder
            }

        return None

    def search_tasks(self, keyword: str, folder: str = "needs_action") -> List[Dict[str, str]]:
        """
        Search tasks by keyword in content

        Args:
            keyword: Search keyword
            folder: Target folder (inbox, needs_action, done)

        Returns:
            List of matching task dictionaries
        """
        BronzeLogger.log_skill_execution(
            self.logger, "ReadVaultSkill", f"search_tasks('{keyword}')",
            "IN_PROGRESS", f"Searching in {folder}"
        )

        all_tasks = self.read_all_tasks(folder)
        matching_tasks = [
            task for task in all_tasks
            if keyword.lower() in task["content"].lower()
        ]

        BronzeLogger.log_skill_execution(
            self.logger, "ReadVaultSkill", f"search_tasks('{keyword}')",
            "SUCCESS", f"Found {len(matching_tasks)} matching tasks"
        )
        return matching_tasks

    def get_task_summary(self, folder: str = "needs_action") -> Dict[str, any]:
        """
        Get summary of tasks in folder

        Args:
            folder: Target folder (inbox, needs_action, done)

        Returns:
            Summary dictionary with count and task list
        """
        BronzeLogger.log_skill_execution(
            self.logger, "ReadVaultSkill", f"get_task_summary({folder})",
            "IN_PROGRESS", "Generating summary"
        )

        tasks = self.read_all_tasks(folder)

        summary = {
            "folder": folder,
            "count": len(tasks),
            "tasks": [
                {
                    "filename": task["filename"],
                    "preview": task["content"][:100] + "..." if len(task["content"]) > 100 else task["content"]
                }
                for task in tasks
            ]
        }

        BronzeLogger.log_skill_execution(
            self.logger, "ReadVaultSkill", f"get_task_summary({folder})",
            "SUCCESS", f"Summary generated: {summary['count']} tasks"
        )
        return summary

    def extract_metadata(self, task_content: str) -> Dict[str, str]:
        """
        Extract metadata from task markdown

        Args:
            task_content: Task markdown content

        Returns:
            Dictionary with extracted metadata
        """
        metadata = {
            "title": "",
            "status": "",
            "priority": "",
            "complexity": "",
            "source": ""
        }

        lines = task_content.split("\n")
        for line in lines:
            if line.startswith("# "):
                metadata["title"] = line[2:].strip()
            elif "**Status**:" in line:
                metadata["status"] = line.split("**Status**:")[1].strip()
            elif "**Priority**:" in line:
                metadata["priority"] = line.split("**Priority**:")[1].strip()
            elif "**Complexity**:" in line:
                metadata["complexity"] = line.split("**Complexity**:")[1].strip()
            elif "**Source**:" in line:
                metadata["source"] = line.split("**Source**:")[1].strip()

        return metadata
