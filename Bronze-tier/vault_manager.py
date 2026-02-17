from pathlib import Path
from config import Config


class VaultManager:
    """Manages Vault structure initialization"""

    @staticmethod
    def initialize():
        """Create Vault directory structure and initialize markdown files"""
        VaultManager._create_folders()
        VaultManager._initialize_markdown_files()

    @staticmethod
    def _create_folders():
        """Create all required Vault folders"""
        Config.VAULT_ROOT.mkdir(exist_ok=True)
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

### Standards
- Python 3.10+
- Pathlib for file operations
- Modular skill-based architecture
- No business logic outside skills
"""
