# Human-in-the-Loop Approval System - Silver Tier Part 5

## Overview
The Approval System adds a critical safety layer requiring explicit human approval before executing sensitive actions. This ensures controlled automation with full traceability and audit logs.

## Architecture

```
approval_system/
├── approval_logger.py      # Specialized logging for approvals
├── approval_manager.py     # Core approval workflow management
├── approval_dashboard.py   # Interactive CLI for reviewing approvals
└── __init__.py
```

## Key Features

### 1. Approval Request System
- Request approval for any MCP Server action
- Track source (manual, plan, automation)
- Store metadata (plan files, task info, priority)
- Generate unique action IDs for tracking

### 2. Interactive Dashboard
- View all pending approvals
- Review detailed action information
- Approve or reject with reasons
- Batch approval mode for multiple actions
- Real-time statistics

### 3. Comprehensive Logging
- All approval requests logged
- All decisions (approve/reject) logged
- All action executions logged
- Full audit trail with timestamps

### 4. Safe Execution
- Actions only execute after approval
- Graceful error handling
- Status tracking (pending/approved/rejected/failed)
- Persistent storage across sessions

## Usage

### Option 1: Interactive Dashboard

```bash
cd Bronze-tier
python run_approval_dashboard.py
```

**Interactive Menu:**
1. View pending approvals
2. Review specific action
3. Approve action
4. Reject action
5. Show statistics
6. Clear completed actions
7. Exit

### Option 2: Batch Approval Mode

```bash
cd Bronze-tier
python run_approval_dashboard.py batch
```

Reviews all pending approvals one by one, prompting for approve/reject/skip.

### Option 3: Quick Commands

```bash
# List pending approvals
python run_approval_dashboard.py list

# Show statistics
python run_approval_dashboard.py stats

# Show help
python run_approval_dashboard.py help
```

### Option 4: Programmatic Usage

```python
from approval_system import ApprovalManager

manager = ApprovalManager()

# Request approval
action_id = manager.request_approval(
    action_type="send_email",
    parameters={
        "to": "client@example.com",
        "subject": "Task Complete",
        "body": "Your task has been completed"
    },
    source="automation",
    metadata={"priority": "high"}
)

print(f"Approval requested: {action_id}")
print("Waiting for human approval...")

# Later, after human reviews via dashboard:
# The action will be executed automatically upon approval
```

## Workflow Examples

### Example 1: Email Requiring Approval

```python
from approval_system import ApprovalManager

manager = ApprovalManager()

# Request approval for sensitive email
action_id = manager.request_approval(
    action_type="send_email",
    parameters={
        "to": "ceo@company.com",
        "subject": "Quarterly Report",
        "body": "Please find attached the quarterly report..."
    },
    source="automation",
    metadata={
        "priority": "high",
        "requires_review": True
    }
)

# Human reviews via dashboard and approves
# Email is sent automatically after approval
```

### Example 2: Plan-Based Approval

```python
from approval_system import ApprovalManager
from pathlib import Path

manager = ApprovalManager()
plan_file = Path("Vault/Inbox/Send_Client_Update_PLAN.md")

# Request approval for action from plan
action_id = manager.request_approval(
    action_type="send_email",
    parameters={
        "to": "client@example.com",
        "subject": "Project Update",
        "body": "Your project milestone has been completed"
    },
    source="plan",
    metadata={
        "plan_file": plan_file.name,
        "action_item": "Send completion email to client"
    }
)

print(f"Action from plan requires approval: {action_id}")
```

### Example 3: Batch Notification Approval

```python
from approval_system import ApprovalManager

manager = ApprovalManager()

# Request multiple approvals
notifications = [
    {"title": "Task 1 Complete", "message": "Task 1 finished"},
    {"title": "Task 2 Complete", "message": "Task 2 finished"},
    {"title": "Task 3 Complete", "message": "Task 3 finished"}
]

action_ids = []
for notif in notifications:
    action_id = manager.request_approval(
        action_type="send_notification",
        parameters=notif,
        source="automation"
    )
    action_ids.append(action_id)

print(f"Requested {len(action_ids)} approvals")
print("Run: python run_approval_dashboard.py batch")
```

## Dashboard Interface

### Viewing Pending Approvals

```
======================================================================
  PENDING APPROVALS
======================================================================

[1] Action ID: 425dc4da
    Type: send_email
    Source: plan
    Requested: 2026-02-26 00:49:29
    Parameters:
      - to: client@example.com
      - subject: Task Complete
      - body: Your task has been completed successfully
    Metadata:
      - plan_file: Send_Update_PLAN.md
      - priority: high

[2] Action ID: f8903295
    Type: send_notification
    Source: automation
    Requested: 2026-02-26 00:50:15
    Parameters:
      - title: System Alert
      - message: Database backup completed

======================================================================
```

### Reviewing Action Details

```
======================================================================
  APPROVAL DETAILS
======================================================================

Action ID: 425dc4da
Type: send_email
Status: pending
Source: plan
Requested: 2026-02-26 00:49:29

Parameters:
{
  "to": "client@example.com",
  "subject": "Task Complete",
  "body": "Your task has been completed successfully"
}

Metadata:
{
  "plan_file": "Send_Update_PLAN.md",
  "priority": "high"
}

======================================================================
```

## Approval Logs

### Location
- **Approval decisions:** `logs/approvals.log`
- **Pending actions:** `logs/pending_approvals.json`

### Log Format

```json
{
  "timestamp": "2026-02-26 00:49:29",
  "event": "APPROVAL_REQUESTED",
  "action_id": "425dc4da",
  "action_type": "send_email",
  "parameters": {...}
}

{
  "timestamp": "2026-02-26 00:50:15",
  "event": "APPROVAL_DECISION",
  "action_id": "425dc4da",
  "decision": "approved",
  "approved_by": "human"
}

{
  "timestamp": "2026-02-26 00:50:16",
  "event": "ACTION_EXECUTED",
  "action_id": "425dc4da",
  "action_type": "send_email",
  "result": {"status": "success", "message": "Email sent successfully"}
}
```

## Integration with Plans

### Automatic Approval Requests from Plans

When a plan contains sensitive actions, request approval before execution:

```python
from pathlib import Path
from approval_system import ApprovalManager
from vault_manager import VaultManager

vault = VaultManager()
manager = ApprovalManager()

# Read plan file
plan_path = Path("Vault/Inbox/Task_PLAN.md")
plan_content = plan_path.read_text()

# Parse action items that require approval
# (Look for email actions, notifications, etc.)

# Request approval for each sensitive action
if "send email" in plan_content.lower():
    action_id = manager.request_approval(
        action_type="send_email",
        parameters={...},
        source="plan",
        metadata={"plan_file": plan_path.name}
    )
```

## Statistics and Monitoring

### Get Statistics

```python
from approval_system import ApprovalManager

manager = ApprovalManager()
stats = manager.get_statistics()

print(f"Total: {stats['total']}")
print(f"Pending: {stats['pending']}")
print(f"Approved: {stats['approved']}")
print(f"Rejected: {stats['rejected']}")
```

### Get Approval History

```python
from approval_system import ApprovalLogger

logger = ApprovalLogger()

# Get all history
history = logger.get_approval_history()

# Get history for specific action
history = logger.get_approval_history(action_id="425dc4da")

for entry in history:
    print(f"{entry['timestamp']} - {entry['event']}")
```

## Security Features

### 1. Explicit Approval Required
- No action executes without approval
- Pending actions stored persistently
- Cannot bypass approval workflow

### 2. Audit Trail
- Every request logged
- Every decision logged
- Every execution logged
- Timestamps for all events

### 3. Rejection with Reasons
- Can reject actions with explanation
- Rejection reasons stored
- Full traceability

### 4. Metadata Tracking
- Source tracking (manual/plan/automation)
- Priority levels
- Related files and tasks
- Custom metadata support

## Error Handling

### Invalid Action ID
```python
result = manager.approve("invalid_id")
# Returns: {"status": "failed", "message": "Action invalid_id not found"}
```

### Already Processed Action
```python
result = manager.approve("already_approved_id")
# Returns: {"status": "failed", "message": "Action is not pending"}
```

### Execution Failure
```python
# If action execution fails, status is updated to "failed"
# Error is logged and stored in approval record
```

## Best Practices

### 1. Always Request Approval for Sensitive Actions
- Emails to external parties
- Notifications to stakeholders
- Data modifications
- External API calls

### 2. Provide Rich Metadata
```python
action_id = manager.request_approval(
    action_type="send_email",
    parameters={...},
    source="plan",
    metadata={
        "plan_file": "Task_PLAN.md",
        "task_file": "Task.md",
        "priority": "high",
        "requires_review": True,
        "deadline": "2026-02-28"
    }
)
```

### 3. Regular Review
- Check pending approvals daily
- Use batch mode for efficiency
- Clear completed actions periodically

### 4. Monitor Logs
- Review `logs/approvals.log` regularly
- Check for patterns in rejections
- Audit approved actions

## Testing

Run comprehensive tests:

```bash
cd Bronze-tier
python test_approval_system.py 1  # Full workflow test
python test_approval_system.py 2  # Plan integration test
python test_approval_system.py 3  # Both tests
```

**Test Coverage:**
- ✅ Request approval
- ✅ Display pending approvals
- ✅ Review specific approval
- ✅ Approve and execute action
- ✅ Reject action with reason
- ✅ Statistics tracking
- ✅ Error handling
- ✅ Logging verification

## Integration with Existing System

The approval system integrates seamlessly:

### With MCP Server
- All MCP actions can require approval
- Execution happens via MCP Server after approval
- Same error handling and logging

### With Plans
- Plans can trigger approval requests
- Metadata links actions to plans
- Traceability from plan to execution

### With Vault
- Actions can reference Vault tasks
- Metadata includes task/plan files
- Complete workflow tracking

## Command Reference

```bash
# Interactive dashboard
python run_approval_dashboard.py

# Batch approval mode
python run_approval_dashboard.py batch

# List pending
python run_approval_dashboard.py list

# Show statistics
python run_approval_dashboard.py stats

# Run tests
python test_approval_system.py 1
python test_approval_system.py 2
python test_approval_system.py 3
```

## Summary

The Human-in-the-Loop Approval System provides:

✅ **Safety** - No sensitive actions without approval
✅ **Traceability** - Complete audit trail
✅ **Flexibility** - Works with any MCP action
✅ **Integration** - Seamless with plans and vault
✅ **Usability** - Interactive and batch modes
✅ **Persistence** - Survives restarts
✅ **Logging** - Comprehensive audit logs
✅ **Error Handling** - Graceful failures

The system ensures controlled automation while maintaining human oversight for critical decisions.
