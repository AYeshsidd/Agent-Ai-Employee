# Plan-to-Approval Integration Guide

## Problem: Why Bitcoin Email Wasn't Showing in Approvals

### Root Cause Analysis

**Issue:** Bitcoin email task existed, plan was generated, but no approval appeared in dashboard.

**Why This Happened:**

1. **Empty Task File**
   - `Bitcoin_email_task.md` was empty (0 bytes)
   - Plan Generator created generic plan with no specific actions
   - No email addresses or actionable items to parse

2. **Missing Integration**
   - Plan Generator creates plans ✓
   - Approval System manages approvals ✓
   - **BUT** no automatic bridge between them ✗

3. **Manual Approval Requests Required**
   - Approvals must be explicitly requested via code
   - Plans don't automatically create approval requests
   - Integration script needed to parse plans and request approvals

---

## Complete Workflow: Task → Plan → Approval

### Step 1: Create Proper Task File

**Requirements:**
- Task must have actual content (not empty)
- Include action items with email addresses
- Specify recipients clearly

**Example:**
```markdown
# Bitcoin Investment Update Email

## Description
Need to send an email update to the investment team about Bitcoin price movement.

**Source:** Manual
**Priority:** High
**Tags:** bitcoin, investment, email

## Action Items
- Review current Bitcoin price and market trends
- Draft email with investment recommendation
- Send email to investment team at team@company.com
- Include risk analysis and price targets
```

### Step 2: Generate Plan

```bash
cd Bronze-tier
python run_plan_generator.py
# Select the Bitcoin task
```

**Result:** Creates `Bitcoin_email_task_PLAN.md` with:
- Step-by-step plan
- Action items including email to team@company.com
- Metadata linking to original task

### Step 3: Create Approval Requests

```bash
cd Bronze-tier
python integrate_plan_approvals.py 3  # For Bitcoin plan
# OR
python integrate_plan_approvals.py 1  # For all plans in Inbox
```

**What This Does:**
- Parses plan file for email/notification actions
- Extracts email addresses from action items
- Creates approval requests in the system
- Links approvals to plan via metadata

### Step 4: Review and Approve

```bash
cd Bronze-tier
python run_approval_dashboard.py list  # View pending approvals
python run_approval_dashboard.py       # Interactive approval
```

---

## Integration Script Usage

### Script: `integrate_plan_approvals.py`

**Purpose:** Bridge between Plan Generator and Approval System

**Features:**
- Parses plan files for actionable items
- Detects email actions with recipient addresses
- Detects notification actions
- Creates approval requests automatically
- Links approvals to plans via metadata

### Usage Modes

#### Mode 1: Process All Plans in Inbox
```bash
python integrate_plan_approvals.py 1
```
- Scans all `*_PLAN.md` files in Vault/Inbox
- Creates approvals for all detected actions
- Shows summary statistics

#### Mode 2: Process Specific Plan
```bash
python integrate_plan_approvals.py 2
# Enter plan filename when prompted
```
- Process one specific plan file
- Useful for testing or selective processing

#### Mode 3: Process Bitcoin Plan (Quick Access)
```bash
python integrate_plan_approvals.py 3
```
- Specifically processes Bitcoin_email_task_PLAN.md
- Quick shortcut for your use case

---

## Action Detection Patterns

### Email Actions

**Pattern:** Action items containing:
- Keywords: "send", "email", "notify", "contact"
- Plus: "email" keyword
- Plus: Email address (any format)

**Examples Detected:**
```markdown
- [ ] Send email to team@company.com
- [ ] Email client at client@example.com with update
- [ ] Contact support@company.com via email
- [ ] Notify stakeholders by email to stakeholders@company.com
```

**Email Address Extraction:**
- Looks for any valid email address in the action text
- Format: `name@domain.com`
- Works with "to", "at", or any other preposition

### Notification Actions

**Pattern:** Action items containing:
- Keywords: "notify", "alert", "send notification", "inform"
- Excluding: Items that also mention "email"

**Examples Detected:**
```markdown
- [ ] Notify team about completion
- [ ] Send notification when task is done
- [ ] Alert stakeholders of status change
- [ ] Inform management of progress
```

---

## Approval Request Details

### What Gets Created

For each detected action, an approval request is created with:

**Email Actions:**
```json
{
  "action_type": "send_email",
  "parameters": {
    "to": "team@company.com",
    "subject": "Regarding: Bitcoin Investment Update Email",
    "body": "Action from plan: Send email to investment team..."
  },
  "source": "plan",
  "metadata": {
    "plan_file": "Bitcoin_email_task_PLAN.md",
    "task_file": "Bitcoin_email_task.md",
    "action_item": "Send email to investment team at team@company.com",
    "source": "Manual"
  }
}
```

**Notification Actions:**
```json
{
  "action_type": "send_notification",
  "parameters": {
    "title": "Action Required: Bitcoin Investment Update Email",
    "message": "Notify team about completion"
  },
  "source": "plan",
  "metadata": {
    "plan_file": "Bitcoin_email_task_PLAN.md",
    "task_file": "Bitcoin_email_task.md",
    "action_item": "Notify team about completion",
    "source": "Manual"
  }
}
```

---

## Best Practices

### 1. Create Meaningful Task Files

**Good:**
```markdown
# Client Update Email

## Description
Send weekly status update to client about project progress.

## Action Items
- Compile progress report
- Send email to client@company.com with report
- Schedule follow-up meeting
```

**Bad:**
```markdown
# Email Task

(empty file or minimal content)
```

### 2. Include Email Addresses in Action Items

**Good:**
```markdown
- [ ] Send email to team@company.com
- [ ] Email results to stakeholders@company.com
- [ ] Contact support at support@company.com
```

**Bad:**
```markdown
- [ ] Send email to team
- [ ] Email the results
- [ ] Contact support
```

### 3. Use Clear Action Verbs

**Detected Keywords:**
- send, email, notify, contact (for emails)
- notify, alert, inform (for notifications)

### 4. Regular Workflow

1. **Create task** with proper content
2. **Generate plan** using Plan Generator
3. **Create approvals** using integration script
4. **Review approvals** in dashboard
5. **Approve/reject** as needed
6. **Actions execute** automatically after approval

---

## Troubleshooting

### Issue: No Approvals Created

**Symptoms:**
```
[INFO] No actions requiring approval found in plan
```

**Causes:**
1. Task file is empty or has minimal content
2. Action items don't include email addresses
3. Action items don't use detected keywords

**Solution:**
1. Check task file has actual content
2. Ensure action items include email addresses
3. Use keywords: "send email to user@example.com"
4. Regenerate plan after fixing task
5. Run integration script again

### Issue: Wrong Email Address Detected

**Symptoms:**
- Approval shows unexpected recipient
- Multiple email addresses in action item

**Solution:**
- Integration script extracts first email address found
- Be specific: "Send email to primary@company.com"
- Avoid multiple emails in one action item
- Split into separate action items if needed

### Issue: Approval Shows Generic Content

**Symptoms:**
- Subject: "Regarding: Task Name"
- Body: "Action from plan: ..."

**Solution:**
- This is expected behavior for auto-generated approvals
- Edit the approval parameters before approving
- Or manually create approval with specific content:
  ```python
  from approval_system import ApprovalManager

  manager = ApprovalManager()
  manager.request_approval(
      action_type="send_email",
      parameters={
          "to": "team@company.com",
          "subject": "Bitcoin Investment Analysis",
          "body": "Detailed email content here..."
      }
  )
  ```

---

## Complete Example: Bitcoin Email Workflow

### 1. Create Task
```bash
# File: Vault/Inbox/Bitcoin_email_task.md
```
```markdown
# Bitcoin Investment Update Email

## Description
Send email update about Bitcoin price movement to investment team.

**Priority:** High
**Tags:** bitcoin, investment, email

## Action Items
- Review current Bitcoin price trends
- Draft investment recommendation
- Send email to team@company.com with analysis
- Include risk assessment
```

### 2. Generate Plan
```bash
python run_plan_generator.py
# Select Bitcoin task
```

**Result:** `Bitcoin_email_task_PLAN.md` created with action items

### 3. Create Approval
```bash
python integrate_plan_approvals.py 3
```

**Output:**
```
[INFO] Found 1 action(s) requiring approval
[1] Requesting approval for: Send email to team@company.com...
    Action ID: 1bc07340
```

### 4. Review Approval
```bash
python run_approval_dashboard.py list
```

**Shows:**
```
[10] Action ID: 1bc07340
     Type: send_email
     Source: plan
     To: team@company.com
     Subject: Regarding: Bitcoin Investment Update Email
     Metadata:
       - plan_file: Bitcoin_email_task_PLAN.md
       - task_file: Bitcoin_email_task.md
```

### 5. Approve and Execute
```bash
python run_approval_dashboard.py
# Select option 3 (Approve action)
# Enter action ID: 1bc07340
# Confirm approval
```

**Result:** Email sent via MCP Server to team@company.com

---

## Integration with Existing Workflow

### Automated Workflow

```python
# Example: Automated plan-to-approval pipeline

from pathlib import Path
from skills.plan_generator_skill import PlanGeneratorSkill
from integrate_plan_approvals import PlanApprovalIntegration

# 1. Generate plans for all inbox tasks
plan_gen = PlanGeneratorSkill()
inbox = Path("Vault/Inbox")

for task_file in inbox.glob("*.md"):
    if not task_file.name.endswith("_PLAN.md"):
        plan_gen.generate_plan(task_file)

# 2. Create approvals for all plans
integration = PlanApprovalIntegration()
stats = integration.process_inbox_plans()

print(f"Plans processed: {stats['plans_processed']}")
print(f"Approvals requested: {stats['approvals_requested']}")
```

### Manual Workflow

1. **Gmail Watcher** creates task from email
2. **Manually review** task in Vault/Inbox
3. **Generate plan** for task
4. **Run integration script** to create approvals
5. **Review approvals** in dashboard
6. **Approve** to execute actions

---

## Summary

### Problem
- Bitcoin email task existed but approval didn't show in dashboard
- Root cause: Empty task file + missing integration

### Solution
1. Created proper task file with content and email address
2. Regenerated plan from proper task
3. Created integration script to parse plans and request approvals
4. Approval now appears in dashboard

### Files Created
- `integrate_plan_approvals.py` - Integration script
- `Bitcoin_email_task.md` - Proper task file
- `Bitcoin_email_task_PLAN.md` - Regenerated plan

### Current Status
✅ Bitcoin email approval showing in dashboard (Action ID: 1bc07340)
✅ Integration script working for all plans
✅ Complete workflow documented

### Next Steps
1. Review pending approval in dashboard
2. Approve to send email via MCP Server
3. Use integration script for future plans
4. Follow best practices for task creation
