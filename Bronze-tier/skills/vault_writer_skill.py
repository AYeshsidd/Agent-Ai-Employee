from pathlib import Path
from datetime import datetime
from typing import Dict
from config import Config


class VaultWriterSkill:
    """Agent skill for writing structured tasks to vault"""

    def __init__(self):
        self.needs_action = Config.NEEDS_ACTION
        self.done = Config.DONE

    def write_to_needs_action(self, task_data: Dict) -> Path:
        """
        Write analyzed task to Needs_Action folder

        Args:
            task_data: Structured task dictionary from TaskAnalyzerSkill

        Returns:
            Path to created file
        """
        filename = self._generate_filename(task_data["title"])
        filepath = self.needs_action / filename

        content = self._format_task(task_data)
        filepath.write_text(content, encoding="utf-8")

        return filepath

    def write_to_done(self, task_data: Dict) -> Path:
        """
        Write completed task to Done folder

        Args:
            task_data: Structured task dictionary

        Returns:
            Path to created file
        """
        filename = self._generate_filename(task_data["title"])
        filepath = self.done / filename

        content = self._format_task(task_data, completed=True)
        filepath.write_text(content, encoding="utf-8")

        return filepath

    def _generate_filename(self, title: str) -> str:
        """Generate timestamped filename from title"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() or c in (" ", "_") else "_" for c in title)
        safe_title = "_".join(safe_title.split())[:50]
        return f"{timestamp}_{safe_title}.md"

    def _format_task(self, task_data: Dict, completed: bool = False) -> str:
        """Format task data as structured markdown"""
        status = "[DONE]" if completed else "[TODO]"

        content = f"""# {task_data['title']}

**Status**: {status}
**Priority**: {self._format_priority(task_data['priority'])}
**Complexity**: {task_data['complexity'].capitalize()}
**Analyzed**: {task_data['analyzed_at']}
**Source**: {task_data['source_file']}

## Description

{task_data['description']}

## Action Items

"""

        if task_data['action_items']:
            for item in task_data['action_items']:
                content += f"- [ ] {item}\n"
        else:
            content += "- [ ] Review and define action items\n"

        if task_data['tags']:
            content += f"\n## Tags\n\n{' '.join(f'#{tag}' for tag in task_data['tags'])}\n"

        content += f"\n---\n\n## Raw Content\n\n{task_data['raw_content']}\n"

        return content

    def _format_priority(self, priority: int) -> str:
        """Format priority as visual indicator"""
        priority_map = {
            5: "Urgent (5)",
            4: "High (4)",
            3: "Medium (3)",
            2: "Low (2)",
            1: "Minimal (1)"
        }
        return priority_map.get(priority, "Medium (3)")
