# Company Handbook

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
