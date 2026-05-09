from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from config import Config
from bronze_logger import BronzeLogger


class VaultManager:
    """Manages Vault structure initialization and operations"""

    def __init__(self):
        # self.logger = BronzeLogger.get_logger("VaultManager", Config.VAULT_LOG)
        self.logger = BronzeLogger.get_logger("VaultManager", Config.VAULT_LOG)
        self.vault_root = Path(Config.VAULT_ROOT)

    @staticmethod
    def initialize():
        """Create Vault directory structure and initialize markdown files"""
        BronzeLogger.setup_logs_directory()
        VaultManager._create_folders()
        VaultManager._initialize_markdown_files()

    @staticmethod
    def _create_folders():
        """Create all required Vault folders"""
        Config.VAULT_ROOT.mkdir(exist_ok=True)
        Config.DROPS.mkdir(exist_ok=True)
        Config.INBOX.mkdir(exist_ok=True)
        Config.NEEDS_ACTION.mkdir(exist_ok=True)
        Config.DONE.mkdir(exist_ok=True)

    @staticmethod
    def _initialize_markdown_files():
        """Initialize Dashboard and Handbook if they don't exist"""
        if not Config.DASHBOARD.exists():
            Config.DASHBOARD.write_text(VaultManager._get_dashboard_template(), encoding="utf-8")

        if not Config.HANDBOOK.exists():
            Config.HANDBOOK.write_text(VaultManager._get_handbook_template(), encoding="utf-8")

    def list_tasks(self, folder: str = "needs_action") -> List[Path]:
        """
        List all tasks in specified folder

        Args:
            folder: Target folder (inbox, needs_action, done)

        Returns:
            List of task file paths
        """
        folder_map = {
            "inbox": Config.INBOX,
            "needs_action": Config.NEEDS_ACTION,
            "done": Config.DONE
        }

        target_folder = folder_map.get(folder.lower())
        if not target_folder:
            BronzeLogger.log_task_action(
                self.logger, "LIST", f"folder:{folder}", "VaultManager",
                "FAILED", f"Invalid folder: {folder}"
            )
            return []

        tasks = list(target_folder.glob("*.md"))
        BronzeLogger.log_task_action(
            self.logger, "LIST", f"folder:{folder}", "VaultManager",
            "SUCCESS", f"Found {len(tasks)} tasks"
        )
        return sorted(tasks, key=lambda x: x.stat().st_mtime, reverse=True)

    def read_task(self, task_path: Path) -> Optional[str]:
        """
        Read task content from file

        Args:
            task_path: Path to task file

        Returns:
            Task content as string or None if error
        """
        try:
            content = task_path.read_text(encoding="utf-8")
            BronzeLogger.log_task_action(
                self.logger, "READ", task_path.name, "VaultManager",
                "SUCCESS", f"Read {len(content)} characters"
            )
            return content
        except Exception as e:
            BronzeLogger.log_task_action(
                self.logger, "READ", task_path.name, "VaultManager",
                "FAILED", str(e)
            )
            return None

    def write_task(self, content: str, folder: str = "inbox", filename: Optional[str] = None) -> Optional[Path]:
        """
        Write task to specified folder

        Args:
            content: Task content (markdown)
            folder: Target folder (inbox, needs_action, done)
            filename: Optional filename (auto-generated if not provided)

        Returns:
            Path to created file or None if error
        """
        folder_map = {
            "inbox": Config.INBOX,
            "needs_action": Config.NEEDS_ACTION,
            "done": Config.DONE
        }

        target_folder = folder_map.get(folder.lower())
        if not target_folder:
            BronzeLogger.log_task_action(
                self.logger, "WRITE", filename or "unknown", "VaultManager",
                "FAILED", f"Invalid folder: {folder}"
            )
            return None

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_task.md"

        if not filename.endswith(".md"):
            filename += ".md"

        task_path = target_folder / filename

        try:
            task_path.write_text(content, encoding="utf-8")
            BronzeLogger.log_task_action(
                self.logger, "CREATE", filename, "VaultManager",
                "SUCCESS", f"Written to {folder}"
            )
            return task_path
        except Exception as e:
            BronzeLogger.log_task_action(
                self.logger, "CREATE", filename, "VaultManager",
                "FAILED", str(e)
            )
            return None

    def move_task(self, task_path: Path, target_folder: str) -> Optional[Path]:
        """
        Move task from one folder to another

        Args:
            task_path: Current task path
            target_folder: Target folder (inbox, needs_action, done)

        Returns:
            New task path or None if error
        """
        folder_map = {
            "inbox": Config.INBOX,
            "needs_action": Config.NEEDS_ACTION,
            "done": Config.DONE
        }

        target = folder_map.get(target_folder.lower())
        if not target:
            BronzeLogger.log_task_action(
                self.logger, "MOVE", task_path.name, "VaultManager",
                "FAILED", f"Invalid target folder: {target_folder}"
            )
            return None

        # Determine source folder
        source_folder = "unknown"
        if task_path.parent == Config.INBOX:
            source_folder = "inbox"
        elif task_path.parent == Config.NEEDS_ACTION:
            source_folder = "needs_action"
        elif task_path.parent == Config.DONE:
            source_folder = "done"

        try:
            new_path = target / task_path.name
            task_path.rename(new_path)

            BronzeLogger.log_lifecycle_event(
                self.logger, task_path.name, source_folder, target_folder, "SUCCESS"
            )
            BronzeLogger.log_task_action(
                self.logger, "MOVE", task_path.name, "VaultManager",
                "SUCCESS", f"{source_folder} -> {target_folder}"
            )
            return new_path
        except Exception as e:
            BronzeLogger.log_lifecycle_event(
                self.logger, task_path.name, source_folder, target_folder, "FAILED"
            )
            BronzeLogger.log_task_action(
                self.logger, "MOVE", task_path.name, "VaultManager",
                "FAILED", str(e)
            )
            return None

    def delete_task(self, task_path: Path) -> bool:
        """
        Delete task file

        Args:
            task_path: Path to task file

        Returns:
            True if successful, False otherwise
        """
        try:
            task_path.unlink()
            BronzeLogger.log_task_action(
                self.logger, "DELETE", task_path.name, "VaultManager",
                "SUCCESS", "Task permanently deleted"
            )
            return True
        except Exception as e:
            BronzeLogger.log_task_action(
                self.logger, "DELETE", task_path.name, "VaultManager",
                "FAILED", str(e)
            )
            return False

    def get_vault_stats(self) -> Dict[str, int]:
        """
        Get statistics about vault contents

        Returns:
            Dictionary with task counts per folder
        """
        stats = {
            "inbox": len(list(Config.INBOX.glob("*.md"))),
            "needs_action": len(list(Config.NEEDS_ACTION.glob("*.md"))),
            "done": len(list(Config.DONE.glob("*.md"))),
            "total": 0
        }
        stats["total"] = stats["inbox"] + stats["needs_action"] + stats["done"]

        BronzeLogger.log_task_action(
            self.logger, "STATS", "vault", "VaultManager",
            "SUCCESS", f"Total: {stats['total']} (Inbox: {stats['inbox']}, Needs_Action: {stats['needs_action']}, Done: {stats['done']})"
        )
        return stats

    @staticmethod
    def _get_dashboard_template() -> str:
        """Return Dashboard markdown template"""
        return """# Dashboard

## Vault Status

### Inbox
Tasks awaiting processing

### Needs Action
Tasks analyzed and ready for execution

### Done
Completed tasks

## Quick Stats
- Total Tasks: 0
- Pending: 0
- In Progress: 0
- Completed: 0
"""

    @staticmethod
    def _get_handbook_template() -> str:
        """Return Company Handbook markdown template"""
        return """# Company Handbook

## Vault System Overview

### Purpose
Automated task processing system using AI Agent Skills

### Workflow
1. Tasks arrive in `/Inbox`
2. AI Agent analyzes tasks using `TaskAnalyzerSkill`
3. Structured output written to `/Needs_Action` via `VaultWriterSkill`
4. Completed tasks moved to `/Done`

### Agent Skills
- **TaskAnalyzerSkill**: Extracts task metadata, priority, and requirements
- **VaultWriterSkill**: Writes structured markdown to vault locations
- **ReadVaultSkill**: Reads tasks from vault folders
- **WriteVaultSkill**: Writes and manages tasks in vault

### Standards
- Python 3.10+
- Pathlib for file operations
- Modular skill-based architecture
- No business logic outside skills
"""
