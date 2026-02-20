from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import re
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from bronze_logger import BronzeLogger


class TaskAnalyzerSkill:
    """Agent skill for analyzing markdown tasks"""

    def __init__(self):
        self.priority_keywords = {
            "urgent": 5,
            "high": 4,
            "medium": 3,
            "low": 2,
            "normal": 3
        }
        self.logger = BronzeLogger.get_logger("TaskAnalyzerSkill")

    def analyze(self, task_content: str, source_file: Path) -> Dict:
        """
        Analyze task content and extract structured information

        Args:
            task_content: Raw markdown content
            source_file: Path to source file

        Returns:
            Structured task dictionary
        """
        BronzeLogger.log_skill_execution(
            self.logger, "TaskAnalyzerSkill", f"analyze({source_file.name})",
            "IN_PROGRESS", "Extracting task metadata"
        )

        result = {
            "title": self._extract_title(task_content),
            "description": self._extract_description(task_content),
            "priority": self._extract_priority(task_content),
            "action_items": self._extract_action_items(task_content),
            "tags": self._extract_tags(task_content),
            "complexity": self._estimate_complexity(task_content),
            "source_file": source_file.name,
            "analyzed_at": datetime.now().isoformat(),
            "raw_content": task_content
        }

        BronzeLogger.log_skill_execution(
            self.logger, "TaskAnalyzerSkill", f"analyze({source_file.name})",
            "SUCCESS", f"Extracted: priority={result['priority']}, complexity={result['complexity']}, actions={len(result['action_items'])}"
        )

        return result

    def _extract_title(self, content: str) -> str:
        """Extract title from markdown (first # heading or first line)"""
        lines = content.strip().split("\n")
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()
        return lines[0][:100] if lines else "Untitled Task"

    def _extract_description(self, content: str) -> str:
        """Extract description (content after title, before action items)"""
        lines = content.strip().split("\n")
        desc_lines = []
        skip_first = False

        for line in lines:
            if line.startswith("# ") and not skip_first:
                skip_first = True
                continue
            if line.startswith("## Action Items") or line.startswith("## Tasks"):
                break
            if line.strip():
                desc_lines.append(line)

        return "\n".join(desc_lines).strip()

    def _extract_priority(self, content: str) -> int:
        """Extract priority from content (1-5 scale)"""
        content_lower = content.lower()
        for keyword, priority in self.priority_keywords.items():
            if keyword in content_lower:
                return priority
        return 3

    def _extract_action_items(self, content: str) -> List[str]:
        """Extract action items (lines starting with -, *, or checkboxes)"""
        action_items = []
        lines = content.split("\n")

        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("- ", "* ", "- [ ]", "- [x]")):
                item = re.sub(r"^[-*]\s*(\[[ x]\]\s*)?", "", stripped)
                action_items.append(item)

        return action_items

    def _extract_tags(self, content: str) -> List[str]:
        """Extract hashtags from content"""
        return list(set(re.findall(r"#(\w+)", content)))

    def _estimate_complexity(self, content: str) -> str:
        """Estimate task complexity based on content length and action items"""
        word_count = len(content.split())
        action_count = len(self._extract_action_items(content))

        if word_count > 500 or action_count > 10:
            return "high"
        elif word_count > 200 or action_count > 5:
            return "medium"
        else:
            return "low"
