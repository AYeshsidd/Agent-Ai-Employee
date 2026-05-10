from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Set
from abc import ABC, abstractmethod
import sys
# Ensure project root is in sys.path
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from vault_manager import VaultManager
from bronze_logger import BronzeLogger
from config import Config


class BaseWatcherSkill(ABC):
    """Base class for all watcher skills with common functionality"""

    def __init__(self, watcher_name: str):
        self.watcher_name = watcher_name
        self.vault_manager = VaultManager()
        self.logger = BronzeLogger.get_logger(f"{watcher_name}Watcher")
        self.processed_ids: Set[str] = set()
        self._load_processed_ids()

    def _load_processed_ids(self):
        """Load previously processed IDs from tracking file"""
        tracking_file = Config.LOGS_DIR / f"{self.watcher_name.lower()}_processed.txt"
        if tracking_file.exists():
            content = tracking_file.read_text(encoding='utf-8')
            self.processed_ids = set(content.strip().split('\n')) if content.strip() else set()
            BronzeLogger.log_skill_execution(
                self.logger, f"{self.watcher_name}WatcherSkill", "load_processed_ids",
                "SUCCESS", f"Loaded {len(self.processed_ids)} processed IDs"
            )

    def _save_processed_id(self, item_id: str):
        """Save processed ID to tracking file"""
        tracking_file = Config.LOGS_DIR / f"{self.watcher_name.lower()}_processed.txt"
        with open(tracking_file, 'a', encoding='utf-8') as f:
            f.write(f"{item_id}\n")
        self.processed_ids.add(item_id)

    def is_duplicate(self, item_id: str) -> bool:
        """Check if item has already been processed"""
        return item_id in self.processed_ids

    def create_task_in_inbox(self, title: str, content: str, source: str,
                            metadata: Dict = None) -> Optional[Path]:
        """
        Create markdown task in Inbox folder

        Args:
            title: Task title
            content: Task content
            source: Source of the task (Gmail, LinkedIn, WhatsApp)
            metadata: Additional metadata

        Returns:
            Path to created task or None if error
        """
        BronzeLogger.log_skill_execution(
            self.logger, f"{self.watcher_name}WatcherSkill", "create_task_in_inbox",
            "IN_PROGRESS", f"Creating task: {title[:50]}..."
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() or c in (" ", "_") else "_" for c in title)
        safe_title = "_".join(safe_title.split())[:50]
        filename = f"{timestamp}_{source}_{safe_title}.md"

        task_markdown = self._format_task(title, content, source, metadata)

        task_path = Config.INBOX / filename

        try:
            task_path.write_text(task_markdown, encoding='utf-8')

            BronzeLogger.log_watcher_event(
                self.logger, "TASK_CREATED", filename,
                "SUCCESS", f"Created from {source}"
            )
            BronzeLogger.log_lifecycle_event(
                self.logger, filename, source, "Inbox", "SUCCESS"
            )
            BronzeLogger.log_skill_execution(
                self.logger, f"{self.watcher_name}WatcherSkill", "create_task_in_inbox",
                "SUCCESS", f"Created {filename}"
            )

            return task_path

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, f"{self.watcher_name}WatcherSkill", "create_task_in_inbox",
                "FAILED", str(e)
            )
            return None

    def _format_task(self, title: str, content: str, source: str,
                    metadata: Dict = None) -> str:
        """Format task as markdown"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        task = f"""# {title}

**Source**: {source}
**Detected**: {timestamp}
**Status**: [TODO]

## Content

{content}

## Action Items

- [ ] Review {source.lower()} content
- [ ] Determine priority
- [ ] Take appropriate action

"""

        if metadata:
            task += "## Metadata\n\n"
            for key, value in metadata.items():
                task += f"- **{key}**: {value}\n"
            task += "\n"

        task += f"#watcher #{source.lower()} #auto-generated\n"

        return task

    @abstractmethod
    def watch(self) -> int:
        """
        Watch for new items and create tasks

        Returns:
            Number of new tasks created
        """
        pass

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the service

        Returns:
            True if authentication successful, False otherwise
        """
        pass
