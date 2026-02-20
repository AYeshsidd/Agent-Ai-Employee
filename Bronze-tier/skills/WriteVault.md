# WriteVault Skill

## Purpose
Write, update, and manage tasks in Vault folders with full CRUD operations.

## Capabilities

### 1. Create Task
Create a new task with structured markdown format in any vault folder.

**Input**: Title, description, folder, priority, action items, tags
**Output**: Path to created task file

### 2. Update Task
Update existing task metadata (status, priority, complexity).

**Input**: Task path and updates dictionary
**Output**: Boolean success status

### 3. Move Task to Folder
Move task between vault folders (Inbox → Needs_Action → Done).

**Input**: Task path and target folder name
**Output**: New task path or None if error

### 4. Mark Task Complete
Mark task as complete and automatically move to Done folder.

**Input**: Task path
**Output**: New path in Done folder

### 5. Delete Task
Permanently delete a task file.

**Input**: Task path
**Output**: Boolean success status

### 6. Add Action Item
Add a new action item to an existing task.

**Input**: Task path and action item text
**Output**: Boolean success status

## Usage Examples

```python
from skills import WriteVaultSkill
from pathlib import Path

# Initialize skill
writer = WriteVaultSkill()

# Create new task
task_path = writer.create_task(
    title="Implement API endpoint",
    description="Create REST API for user management",
    folder="inbox",
    priority="High",
    action_items=[
        "Design API schema",
        "Implement endpoints",
        "Write tests"
    ],
    tags=["api", "backend"]
)

# Update task status
writer.update_task(task_path, {"status": "[IN PROGRESS]"})

# Add action item
writer.add_action_item(task_path, "Add API documentation")

# Move to Needs_Action
new_path = writer.move_task_to_folder(task_path, "needs_action")

# Mark complete when done
done_path = writer.mark_task_complete(new_path)

# Delete task if needed
writer.delete_task(task_path)
```

## Task Format

All tasks are created with consistent markdown structure:

```markdown
# Task Title

**Status**: [TODO]
**Priority**: Medium
**Created**: 2026-02-19T03:30:00

## Description

Task description here

## Action Items

- [ ] Action item 1
- [ ] Action item 2

## Tags

#tag1 #tag2
```

## Integration

- Works with VaultManager for safe file operations
- Logs all write operations for audit trail
- Compatible with TaskAnalyzerSkill output
- Maintains consistent markdown formatting
- Supports watcher-generated task format

## Error Handling

- Returns None if folder is invalid
- Returns False if update/delete fails
- Logs all errors with context
- Validates task path before operations
- Gracefully handles file write failures

## Workflow Integration

```
Drops → Inbox → Needs_Action → Done
  ↓       ↓          ↓           ↓
Watch  Create    Update      Complete
```

## Logging

All operations are logged to `vault_operations.log`:
- Task creation with filename and folder
- Task updates with changed fields
- Task moves between folders
- Task deletions
- All errors with stack traces
