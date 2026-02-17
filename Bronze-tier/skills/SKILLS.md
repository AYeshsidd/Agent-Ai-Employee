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
