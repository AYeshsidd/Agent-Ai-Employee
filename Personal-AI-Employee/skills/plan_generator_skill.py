#!/usr/bin/env python3
"""Plan Generator Skill - Silver Tier Part 3"""
from pathlib import Path
from typing import Dict, Optional
import sys
import re
from datetime import datetime

# Ensure project root is in sys.path
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from bronze_logger import BronzeLogger
from config import Config


class PlanGeneratorSkill:
    """Agent skill for generating structured Plan.md from Vault tasks"""

    def __init__(self):
        self.logger = BronzeLogger.get_logger("PlanGeneratorSkill")
        BronzeLogger.log_skill_execution(
            self.logger, "PlanGeneratorSkill", "__init__",
            "SUCCESS", "Plan Generator Skill initialized"
        )

    def generate_plan(self, task_file_path: Path) -> Optional[Path]:
        """
        Generate a structured Plan.md from a Vault task

        Args:
            task_file_path: Path to the task markdown file

        Returns:
            Path to generated Plan.md file, or None if failed
        """
        BronzeLogger.log_skill_execution(
            self.logger, "PlanGeneratorSkill", "generate_plan",
            "IN_PROGRESS", f"Generating plan for: {task_file_path.name}"
        )

        try:
            # Read task file
            if not task_file_path.exists():
                BronzeLogger.log_skill_execution(
                    self.logger, "PlanGeneratorSkill", "generate_plan",
                    "FAILED", f"Task file not found: {task_file_path}"
                )
                return None

            task_content = task_file_path.read_text(encoding='utf-8')

            # Parse task metadata
            task_data = self._parse_task(task_content, task_file_path.stem)

            # Generate plan content
            plan_content = self._create_plan_content(task_data)

            # Save Plan.md
            plan_file_path = task_file_path.parent / f"{task_file_path.stem}_PLAN.md"
            plan_file_path.write_text(plan_content, encoding='utf-8')

            BronzeLogger.log_skill_execution(
                self.logger, "PlanGeneratorSkill", "generate_plan",
                "SUCCESS", f"Plan generated: {plan_file_path.name}"
            )

            return plan_file_path

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "PlanGeneratorSkill", "generate_plan",
                "FAILED", str(e)
            )
            return None

    def _parse_task(self, content: str, filename: str) -> Dict[str, str]:
        """Parse task markdown and extract metadata"""
        data = {
            'title': filename.replace('_', ' ').title(),
            'description': '',
            'source': 'Unknown',
            'priority': 'Medium',
            'tags': [],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action_items': []
        }

        lines = content.split('\n')
        current_section = None

        for line in lines:
            line_stripped = line.strip()

            # Extract title (first # heading)
            if line_stripped.startswith('# ') and not data.get('title_extracted'):
                data['title'] = line_stripped[2:].strip()
                data['title_extracted'] = True
                continue

            # Extract metadata sections
            if line_stripped.startswith('**Source:**'):
                data['source'] = line_stripped.replace('**Source:**', '').strip()
                continue

            if line_stripped.startswith('**Priority:**'):
                data['priority'] = line_stripped.replace('**Priority:**', '').strip()
                continue

            if line_stripped.startswith('**Tags:**'):
                tags_str = line_stripped.replace('**Tags:**', '').strip()
                data['tags'] = [t.strip() for t in tags_str.split(',') if t.strip()]
                continue

            if line_stripped.startswith('**Timestamp:**'):
                data['timestamp'] = line_stripped.replace('**Timestamp:**', '').strip()
                continue

            # Track sections
            if line_stripped == '## Description':
                current_section = 'description'
                continue
            elif line_stripped == '## Action Items':
                current_section = 'action_items'
                continue
            elif line_stripped.startswith('## '):
                current_section = None

            # Extract description
            if current_section == 'description' and line_stripped:
                data['description'] += line_stripped + ' '

            # Extract action items from Action Items section
            if current_section == 'action_items' and line_stripped:
                # Match lines starting with -, *, or digit followed by . or )
                if re.match(r'^[-*]\s+', line_stripped) or re.match(r'^\d+[\.\)]\s+', line_stripped):
                    action = re.sub(r'^[-*]\s+', '', line_stripped)
                    action = re.sub(r'^\d+[\.\)]\s+', '', action)
                    if action and len(action) > 3:
                        data['action_items'].append(action)

        data['description'] = data['description'].strip()

        return data

    def _create_plan_content(self, task_data: Dict[str, str]) -> str:
        """Create structured Plan.md content"""

        # Generate step-by-step plan from action items or description
        steps = self._generate_steps(task_data)

        # Extract notes/context
        notes = self._extract_notes(task_data)

        # Format action items
        action_items = task_data.get('action_items', [])
        if not action_items:
            action_items = self._extract_action_items_from_description(task_data['description'])

        plan_content = f"""# Plan for: {task_data['title']}

## Source
{task_data['source']}

## Task Description
{task_data['description'] if task_data['description'] else 'No description provided'}

## Priority
**{task_data['priority']}**

## Step-by-Step Plan

{steps}

## Notes / Context
{notes}

## Action Items
{self._format_action_items(action_items)}

---
*Generated on: {task_data['timestamp']}*
*Tags: {', '.join(task_data['tags']) if task_data['tags'] else 'None'}*
"""

        return plan_content

    def _generate_steps(self, task_data: Dict[str, str]) -> str:
        """Generate step-by-step plan from task data"""
        action_items = task_data.get('action_items', [])
        description = task_data['description']

        if action_items:
            # Use action items as steps
            steps = []
            for i, action in enumerate(action_items[:5], 1):  # Limit to 5 steps
                steps.append(f"**Step {i}** – {action}")
            return '\n\n'.join(steps)
        else:
            # Generate generic steps based on source
            source = task_data['source'].lower()

            if 'gmail' in source or 'email' in source:
                return """**Step 1** – Review email content and identify key requirements

**Step 2** – Draft response or take necessary action

**Step 3** – Follow up and mark as complete"""

            elif 'linkedin' in source:
                return """**Step 1** – Review LinkedIn message and sender profile

**Step 2** – Prepare appropriate response or action

**Step 3** – Respond and update task status"""

            elif 'whatsapp' in source:
                return """**Step 1** – Review WhatsApp message and context

**Step 2** – Prepare response or take required action

**Step 3** – Reply and close task"""

            else:
                return """**Step 1** – Analyze task requirements and gather information

**Step 2** – Execute primary action items

**Step 3** – Verify completion and document results"""

    def _extract_notes(self, task_data: Dict[str, str]) -> str:
        """Extract notes and context from task data"""
        notes = []

        # Add source-specific context
        source = task_data['source']
        if source != 'Unknown':
            notes.append(f"- Task originated from {source}")

        # Add priority context
        priority = task_data['priority']
        if priority == 'High':
            notes.append("- **HIGH PRIORITY** - Requires immediate attention")
        elif priority == 'Low':
            notes.append("- Low priority - Can be scheduled for later")

        # Check for ambiguous points
        if not task_data['description'] or len(task_data['description']) < 20:
            notes.append("- **CLARIFICATION NEEDED**: Task description is minimal or missing")

        if not task_data.get('action_items'):
            notes.append("- **NOTE**: No explicit action items found - review task carefully")

        # Extract URLs from description
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                          task_data['description'])
        if urls:
            notes.append(f"- Relevant links: {', '.join(urls)}")

        return '\n'.join(notes) if notes else "No additional context available"

    def _extract_action_items_from_description(self, description: str) -> list:
        """Extract potential action items from description"""
        if not description:
            return ["Review task requirements", "Take appropriate action", "Mark as complete"]

        # Look for action verbs
        action_verbs = ['review', 'respond', 'send', 'create', 'update', 'check', 'verify',
                        'contact', 'schedule', 'prepare', 'analyze', 'implement']

        sentences = re.split(r'[.!?]', description)
        action_items = []

        for sentence in sentences:
            sentence = sentence.strip().lower()
            if any(verb in sentence for verb in action_verbs):
                action_items.append(sentence.capitalize())

        if not action_items:
            action_items = [
                "Review task description carefully",
                "Identify key requirements and deliverables",
                "Execute necessary actions",
                "Verify completion criteria"
            ]

        return action_items[:5]  # Limit to 5 items

    def _format_action_items(self, action_items: list) -> str:
        """Format action items as markdown checklist"""
        if not action_items:
            return "- [ ] Review and complete task"

        formatted = []
        for item in action_items:
            formatted.append(f"- [ ] {item}")

        return '\n'.join(formatted)


if __name__ == "__main__":
    # Quick test
    skill = PlanGeneratorSkill()
    print("Plan Generator Skill initialized successfully")
