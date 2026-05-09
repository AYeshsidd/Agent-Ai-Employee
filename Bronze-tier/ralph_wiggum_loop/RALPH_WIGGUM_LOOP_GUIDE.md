# Ralph Wiggum Loop - Autonomous Task Execution System

## Overview

The **Ralph Wiggum Loop** is an autonomous multi-step task execution system for the Autonomous FTE project. It automatically detects, analyzes, and executes tasks across multiple domains (Social Media, Accounting, Email, Vault Operations) without manual intervention.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    RALPH WIGGUM LOOP                             │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Task       │────▶│   Action     │────▶│   Action     │
│   Analyzer   │     │   Planner    │     │   Executor   │
│              │     │              │     │              │
│ - Detect     │     │ - Decide     │     │ - Twitter    │
│   Type       │     │   Next       │     │ - Facebook   │
│ - Extract    │     │   Steps      │     │ - LinkedIn   │
│   Params     │     │ - Prioritize │     │ - Odoo       │
└──────────────┘     └──────────────┘     └──────────────┘
                              │                    │
                              ▼                    ▼
                     ┌──────────────┐     ┌──────────────┐
                     │   Error      │◀────│   MCP        │
                     │   Handler    │     │   Server     │
                     │              │     │              │
                     │ - Retry      │     │ - Tools      │
                     │ - Fallback   │     │ - Actions    │
                     │ - Degrade    │     └──────────────┘
                     └──────────────┘
                              │
                              ▼
                     ┌──────────────┐
                     │   Logger     │
                     │              │
                     │ - JSONL      │
                     │ - Audit      │
                     └──────────────┘
```

---

## File Structure

```
Bronze-tier/
├── ralph_wiggum_loop/           # Package
│   ├── __init__.py              # Package exports
│   ├── core.py                  # Core types and logger
│   ├── task_analyzer.py         # Task type detection
│   ├── action_executor.py       # MCP action execution
│   ├── error_handler.py         # Retry and fallback logic
│   └── loop.py                  # Main orchestrator
│
├── run_ralph_wiggum.py          # CLI runner
├── logs/
│   └── ralph_wiggum_loop.jsonl  # Execution logs
│
└── Vault/
    ├── Inbox/                   # Raw tasks
    ├── Needs_Action/            # Analyzed tasks
    └── Done/                    # Completed tasks
```

---

## Features

### 1. Automatic Task Detection
- Scans `Inbox/` and `Needs_Action/` folders
- Processes markdown task files
- Configurable scan intervals

### 2. Task Type Detection
Automatically detects task types:
- **Social Media**: Twitter, Facebook, LinkedIn posts
- **Accounting**: Invoices, Payments, Expenses (Odoo)
- **Email**: Send emails via MCP
- **Vault**: Move tasks between folders

### 3. Action Planning
- Determines required actions from task content
- Prioritizes actions based on keywords
- Extracts parameters automatically

### 4. Multi-MCP Execution
- Twitter auto-post
- Facebook auto-post
- LinkedIn auto-post
- Odoo accounting operations
- Email sending
- Vault operations

### 5. Error Handling
- Configurable retry attempts (default: 3)
- Exponential backoff (2s, 4s, 8s...)
- Error categorization (Low/Medium/High/Recoverable)
- Fallback actions for failures
- Graceful degradation

### 6. Comprehensive Logging
- JSONL format for easy parsing
- Timestamp for every step
- Status tracking (STARTED, SUCCESS, ERROR)
- Error messages captured
- Full audit trail

---

## Usage

### Quick Start

```bash
# Run continuously (scans every 60 seconds)
cd Bronze-tier
python run_ralph_wiggum.py

# Run single pass (process all tasks once)
python run_ralph_wiggum.py --single

# Process specific task
python run_ralph_wiggum.py --task "20260331_Social_Media_Product_Launch.md"

# Custom configuration
python run_ralph_wiggum.py --interval 120 --retries 5 --delay 3.0
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--single`, `-s` | Run once and exit | Continuous |
| `--interval`, `-i` | Scan interval (seconds) | 60 |
| `--task`, `-t` | Process specific task | All tasks |
| `--retries`, `-r` | Max retry attempts | 3 |
| `--delay`, `-d` | Base retry delay (seconds) | 2.0 |
| `--status` | Show status and exit | - |

### Programmatic Usage

```python
from ralph_wiggum_loop import run_loop, run_single_task
from pathlib import Path

# Run continuously
run_loop(scan_interval=60, max_retries=3)

# Run single pass
run_loop(single_pass=True)

# Process specific task
run_single_task(Path("Vault/Needs_Action/task.md"))

# Custom loop instance
from ralph_wiggum_loop import RalphWiggumLoop

loop = RalphWiggumLoop(
    max_retries=5,
    retry_delay=3.0,
    scan_interval=120
)
loop.run(single_pass=False)
```

---

## Task Format

### Social Media Task

```markdown
# Post Title

**Priority**: High

## Twitter Post

Your tweet content here (280 chars max)

#hashtags #here

## Facebook Post

Your Facebook post content (can be longer)

## Action Items

- [ ] Post to social media
```

### Odoo Invoice Task

```markdown
# Create Invoice for Client

**Priority**: High

## Odoo Operation

Create Invoice

## Invoice Details

- **Partner ID**: 1
- **Amount**: 5000.00
- **Description**: Consulting Services

## Action Items

- [ ] Create invoice in Odoo
```

### Email Task

```markdown
# Send Email to Manager

**Priority**: Medium

## Email Details

- **To**: manager@company.com
- **Subject**: Weekly Update
- **Body**: Weekly progress report...

## Action Items

- [ ] Send email
```

---

## Execution Flow

```
1. Scan folders (Inbox/, Needs_Action/)
   │
   ▼
2. For each task file:
   │
   ├──▶ Read task content
   │
   ├──▶ Analyze task type
   │    └── Detect: Twitter/Facebook/Odoo/Email
   │
   ├──▶ Extract parameters
   │    └── partner_id, amount, content, etc.
   │
   ├──▶ Determine actions
   │    └── [post_twitter, move_to_done]
   │
   ├──▶ Execute actions (with retry)
   │    ├── Try action
   │    ├── If failed → retry (exponential backoff)
   │    └── If still failed → fallback action
   │
   └──▶ Log all steps
        └── JSONL format in logs/ralph_wiggum_loop.jsonl
```

---

## Error Handling

### Retry Strategy

| Attempt | Delay |
|---------|-------|
| 1 | Immediate |
| 2 | 2 seconds |
| 3 | 4 seconds |
| 4 | 8 seconds |
| 5 | 16 seconds |

### Error Categories

| Severity | Behavior |
|----------|----------|
| **Low** | Log and continue |
| **Medium** | Retry with backoff |
| **High** | Stop execution, log error |
| **Recoverable** | Continue with degraded functionality |

### Fallback Actions

| Failed Action | Fallback |
|--------------|----------|
| post_twitter | move_to_done |
| post_facebook | move_to_done |
| create_invoice | move_to_needs_action |
| send_email | move_to_needs_action |

---

## Logs

### Location
```
Bronze-tier/logs/ralph_wiggum_loop.jsonl
```

### Format
```json
{
  "timestamp": "2026-03-31T12:00:00.000000",
  "task_id": "20260331_Social_Media_Product_Launch",
  "step": "EXECUTE_post_twitter",
  "status": "SUCCESS",
  "details": {"message": "Posted to Twitter"},
  "error": null
}
```

### View Logs

```bash
# View all logs
cat logs/ralph_wiggum_loop.jsonl

# View specific task logs
grep "task_id.*Social_Media" logs/ralph_wiggum_loop.jsonl

# View errors only
grep "ERROR" logs/ralph_wiggum_loop.jsonl
```

---

## Supported Task Types

| Type | Keywords | Actions |
|------|----------|---------|
| **Twitter** | twitter, tweet, x.com | post_twitter |
| **Facebook** | facebook, fb, meta | post_facebook |
| **LinkedIn** | linkedin, professional | post_linkedin |
| **Invoice** | invoice, bill, billing | create_invoice |
| **Payment** | payment, paid, received | register_payment |
| **Expense** | expense, reimbursement | create_expense |
| **Email** | email, send, mail | send_email |

---

## Testing

### Test with Sample Tasks

```bash
# Sample tasks are in Vault/Needs_Action/
# - 20260331_Social_Media_Product_Launch.md
# - 20260331_Create_Invoice_ABC_Corp.md

# Run single pass
python run_ralph_wiggum.py --single

# Check logs
cat logs/ralph_wiggum_loop.jsonl
```

### Test Specific Task

```bash
python run_ralph_wiggum.py --task "20260331_Social_Media_Product_Launch.md"
```

---

## Extensibility

### Add New Task Type

1. Add to `TaskType` enum in `core.py`
2. Add keywords to `type_keywords` in `task_analyzer.py`
3. Add handler to `ActionExecutor` in `action_executor.py`
4. Add to `handlers` dict in `_get_handler()`

### Add New Action

1. Add to `TaskAction` enum in `core.py`
2. Add keywords to `action_keywords` in `task_analyzer.py`
3. Add handler method to `ActionExecutor`
4. Add to `handlers` dict

### Add New MCP Integration

1. Create MCP module (follow existing pattern)
2. Add handler in `action_executor.py`
3. Add task type detection in `task_analyzer.py`

---

## Best Practices

### Task Creation
- Use clear, descriptive titles
- Include relevant keywords for type detection
- Specify parameters explicitly (Partner ID, Amount, etc.)
- Use sections (## Twitter Post, ## Facebook Post)

### Error Handling
- Set appropriate retry count (3-5 recommended)
- Monitor logs for recurring errors
- Use fallback actions for non-critical tasks

### Performance
- Set scan interval based on task volume
- Use single-pass mode for batch processing
- Monitor log file size

---

## Troubleshooting

### Task Not Detected
- Check file is in `Inbox/` or `Needs_Action/`
- Ensure file has `.md` extension
- Check task has recognizable keywords

### Action Fails Repeatedly
- Check logs for error details
- Verify MCP server is running
- Check credentials are valid
- Increase retry count if transient errors

### High Error Rate
- Review error patterns in logs
- Adjust retry delay for rate-limited APIs
- Check network connectivity
- Verify Odoo/social media access

---

## Summary

✅ **Autonomous Execution** - No manual intervention needed
✅ **Multi-MCP Support** - Twitter, Facebook, LinkedIn, Odoo, Email
✅ **Error Handling** - Retries, fallbacks, graceful degradation
✅ **Comprehensive Logging** - Full audit trail in JSONL
✅ **Extensible** - Easy to add new task types and actions
✅ **Production Ready** - Tested with sample tasks

**The Ralph Wiggum Loop is ready for production use!** 🚀
