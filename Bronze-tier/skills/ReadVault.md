# ReadVault Skill

## Purpose
Read and query tasks from Vault folders with advanced search and filtering capabilities.

## Capabilities

### 1. Read All Tasks
Read all tasks from a specified folder (Inbox, Needs_Action, Done).

**Input**: Folder name
**Output**: List of task dictionaries with filename, path, and content

### 2. Read Task by Name
Retrieve a specific task by its filename.

**Input**: Filename and folder name
**Output**: Task dictionary or None if not found

### 3. Search Tasks
Search for tasks containing specific keywords in their content.

**Input**: Search keyword and folder name
**Output**: List of matching tasks

### 4. Get Task Summary
Generate a summary of all tasks in a folder with preview text.

**Input**: Folder name
**Output**: Summary dictionary with count and task previews

### 5. Extract Metadata
Parse task markdown and extract structured metadata (title, status, priority, complexity, source).

**Input**: Task content (markdown string)
**Output**: Metadata dictionary

## Usage Examples

```python
from skills import ReadVaultSkill

# Initialize skill
reader = ReadVaultSkill()

# Read all tasks from Needs_Action
tasks = reader.read_all_tasks("needs_action")

# Search for specific tasks
auth_tasks = reader.search_tasks("authentication", "needs_action")

# Get task summary
summary = reader.get_task_summary("inbox")

# Read specific task
task = reader.read_task_by_name("20260219_task.md", "needs_action")

# Extract metadata
metadata = reader.extract_metadata(task["content"])
```

## Integration

- Works with VaultManager for file operations
- Logs all read operations for debugging
- Compatible with watcher-generated tasks
- Returns structured data for AI processing

## Error Handling

- Returns empty list if folder is invalid
- Returns None if task not found
- Logs all errors with context
- Gracefully handles file read failures
