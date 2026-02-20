import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import Config
from bronze_logger import BronzeLogger


class DropsFolderHandler(FileSystemEventHandler):
    """Handles file system events in Drops folder"""

    def __init__(self):
        self.processed_files = set()
        self.logger = BronzeLogger.get_logger("Watcher", Config.WATCHER_LOG)

    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if file_path.suffix.lower() not in ['.txt', '.md', '.pdf', '.docx', '.doc']:
            BronzeLogger.log_watcher_event(
                self.logger, "FILE_DETECTED", file_path.name,
                "FAILED", "Unsupported file type"
            )
            return

        if file_path.name in self.processed_files:
            BronzeLogger.log_watcher_event(
                self.logger, "FILE_DETECTED", file_path.name,
                "FAILED", "Already processed (duplicate)"
            )
            return

        BronzeLogger.log_watcher_event(
            self.logger, "FILE_DETECTED", file_path.name,
            "SUCCESS", f"File type: {file_path.suffix}"
        )
        self._create_task_from_file(file_path)

    def _create_task_from_file(self, file_path: Path):
        """Create markdown task in Inbox from detected file"""
        try:
            BronzeLogger.log_watcher_event(
                self.logger, "TASK_CREATION", file_path.name,
                "IN_PROGRESS", "Reading file content"
            )

            content = self._read_file_content(file_path)
            task_markdown = self._format_as_task(file_path, content)

            task_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_path.stem}.md"
            task_path = Config.INBOX / task_filename

            task_path.write_text(task_markdown, encoding='utf-8')

            self.processed_files.add(file_path.name)

            BronzeLogger.log_watcher_event(
                self.logger, "TASK_CREATED", task_filename,
                "SUCCESS", f"Created from {file_path.name}"
            )
            BronzeLogger.log_lifecycle_event(
                self.logger, task_filename, "Drops", "Inbox", "SUCCESS"
            )

            file_path.unlink()

            BronzeLogger.log_watcher_event(
                self.logger, "FILE_REMOVED", file_path.name,
                "SUCCESS", "Source file deleted after processing"
            )

        except Exception as e:
            BronzeLogger.log_watcher_event(
                self.logger, "TASK_CREATION", file_path.name,
                "FAILED", str(e)
            )

    def _read_file_content(self, file_path: Path) -> str:
        """Read content from file"""
        if file_path.suffix.lower() in ['.txt', '.md']:
            return file_path.read_text(encoding='utf-8')
        elif file_path.suffix.lower() in ['.pdf', '.docx', '.doc']:
            return f"[Binary file: {file_path.name}]\nManual review required."
        else:
            return f"[Unsupported file type: {file_path.suffix}]"

    def _format_as_task(self, file_path: Path, content: str) -> str:
        """Format file content as markdown task"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        task = f"""# Task from {file_path.name}

Priority: Medium

## Description

File detected in Drops folder at {timestamp}

## Content

{content}

## Action Items

- [ ] Review file content
- [ ] Define specific action items
- [ ] Assign priority level

#watcher #auto-generated
"""
        return task


class FileWatcher:
    """Main watcher class to monitor Drops folder"""

    def __init__(self):
        self.observer = Observer()
        self.handler = DropsFolderHandler()
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Start watching the Drops folder"""
        watch_path = str(Config.DROPS)
        self.observer.schedule(self.handler, watch_path, recursive=False)
        self.observer.start()
        self.logger.info(f"Watcher started. Monitoring: {watch_path}")

    def stop(self):
        """Stop the watcher"""
        self.observer.stop()
        self.observer.join()
        self.logger.info("Watcher stopped")
