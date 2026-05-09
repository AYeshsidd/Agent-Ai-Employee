# Agent Skills

## TaskAnalyzerSkill

**Purpose**: Analyze markdown tasks from Inbox and extract structured information

**Input**: Raw markdown task content
**Output**: Structured task dictionary with metadata

**Capabilities**:
- Extract task title, description, priority
- Identify action items and requirements
- Categorize task type
- Estimate complexity

## VaultWriterSkill

**Purpose**: Write structured task data to vault locations

**Input**: Structured task dictionary, target location
**Output**: Formatted markdown file in specified vault folder

**Capabilities**:
- Generate structured markdown from task data
- Write to /Needs_Action, /Done folders
- Create timestamped filenames
- Maintain consistent formatting

## ReadVaultSkill

**Purpose**: Read and query tasks from Vault folders

**Input**: Folder name, search criteria
**Output**: Task data with content and metadata

**Capabilities**:
- Read all tasks from any vault folder
- Search tasks by keyword
- Read specific task by filename
- Generate task summaries
- Extract metadata from markdown

**Methods**:
- `read_all_tasks(folder)` - Read all tasks from folder
- `read_task_by_name(filename, folder)` - Read specific task
- `search_tasks(keyword, folder)` - Search by keyword
- `get_task_summary(folder)` - Get folder summary
- `extract_metadata(content)` - Parse task metadata

## WriteVaultSkill

**Purpose**: Write, update, and manage tasks in Vault folders

**Input**: Task data, target folder, updates
**Output**: Task file path or operation status

**Capabilities**:
- Create new tasks with structured format
- Update existing task metadata
- Move tasks between folders
- Mark tasks as complete
- Delete tasks
- Add action items to tasks

**Methods**:
- `create_task(title, description, folder, priority, action_items, tags)` - Create new task
- `update_task(task_path, updates)` - Update task fields
- `move_task_to_folder(task_path, target_folder)` - Move task
- `mark_task_complete(task_path)` - Mark complete and move to Done
- `delete_task(task_path)` - Delete task file
- `add_action_item(task_path, action_item)` - Add action item

## Skill Integration

All skills work together in the Bronze-tier workflow:

```
1. Watcher detects file in /Drops
2. WriteVaultSkill creates task in /Inbox
3. TaskAnalyzerSkill analyzes task
4. VaultWriterSkill writes to /Needs_Action
5. ReadVaultSkill queries tasks
6. WriteVaultSkill manages task lifecycle
7. Task moves to /Done when complete
```

## Logging

All skills log operations to:
- `vault_operations.log` - Vault read/write operations
- `watcher.log` - File system events
- Console output for real-time monitoring

