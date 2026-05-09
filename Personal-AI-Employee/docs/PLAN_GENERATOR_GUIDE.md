# Plan Generator Skill - Silver Tier Part 3

## Overview
The Plan Generator Skill automatically creates structured `Plan.md` files from Vault tasks. It extracts metadata, action items, and generates step-by-step plans to make tasks actionable.

## Features

- **Automatic Parsing**: Extracts title, description, source, priority, tags, and action items from task markdown
- **Structured Plans**: Generates clear step-by-step plans with completion criteria
- **Smart Context**: Highlights high-priority tasks and ambiguous points needing clarification
- **Action Checklists**: Converts action items into markdown checklists
- **Source-Aware**: Adapts plan structure based on task source (Gmail, LinkedIn, WhatsApp)

## Generated Plan Structure

```markdown
# Plan for: <Task Title>

## Source
<Source>

## Task Description
<Full description>

## Priority
**High / Medium / Low**

## Step-by-Step Plan
Step 1 – Initial action
Step 2 – Next action
Step 3 – Completion criteria

## Notes / Context
- Task originated from <source>
- Priority warnings
- Clarification needs
- Relevant links

## Action Items
- [ ] Action 1
- [ ] Action 2
- [ ] Action 3

---
*Generated on: <timestamp>*
*Tags: <tags>*
```

## Usage

### Option 1: Interactive Mode

```bash
cd Bronze-tier
python run_plan_generator.py
```

Then select:
1. Choose folder (Inbox, Needs_Action, Done)
2. Select specific task or generate for all tasks

### Option 2: Test with Sample Task

```bash
cd Bronze-tier
python test_plan_generator.py
```

This creates a sample task and generates a plan to demonstrate functionality.

### Option 3: Programmatic Usage

```python
from pathlib import Path
from skills.plan_generator_skill import PlanGeneratorSkill

# Initialize skill
plan_gen = PlanGeneratorSkill()

# Generate plan for a task
task_path = Path("Vault/Inbox/my_task.md")
plan_path = plan_gen.generate_plan(task_path)

if plan_path:
    print(f"Plan generated: {plan_path}")
```

## Task Format Requirements

For best results, tasks should include:

```markdown
# Task Title

## Description
Task description here...

**Source:** Gmail / LinkedIn / WhatsApp
**Priority:** High / Medium / Low
**Tags:** tag1, tag2, tag3
**Timestamp:** 2026-02-24 10:30:00

## Action Items
- Action item 1
- Action item 2
- Action item 3
```

## Smart Features

### Priority Warnings
- High priority tasks get highlighted: "**HIGH PRIORITY** - Requires immediate attention"
- Low priority tasks noted: "Low priority - Can be scheduled for later"

### Clarification Detection
- Minimal descriptions trigger: "**CLARIFICATION NEEDED**: Task description is minimal or missing"
- Missing action items trigger: "**NOTE**: No explicit action items found - review task carefully"

### Source-Specific Plans
- **Gmail tasks**: Review email → Draft response → Follow up
- **LinkedIn tasks**: Review message → Prepare response → Respond
- **WhatsApp tasks**: Review message → Prepare action → Reply
- **Generic tasks**: Analyze requirements → Execute actions → Verify completion

### URL Extraction
Automatically extracts and lists URLs from task descriptions in Notes/Context section.

## Output Location

Plans are saved in the same folder as the source task with `_PLAN.md` suffix:
- Task: `Vault/Inbox/my_task.md`
- Plan: `Vault/Inbox/my_task_PLAN.md`

## Integration with Workflow

1. **Watchers create tasks** → Tasks land in `Vault/Inbox/`
2. **Generate plans** → Run plan generator on inbox tasks
3. **Review plans** → Check generated plans for clarity
4. **Execute tasks** → Follow step-by-step plan
5. **Move to Done** → Archive completed tasks

## Logging

All plan generation operations are logged to `logs/bronze_tier.log`:
- Skill initialization
- Plan generation start/success/failure
- File paths and metadata

## Example Output

See `Vault/Inbox/Implement_User_Authentication_Feature_PLAN.md` for a complete example of generated plan output.

## Notes

- Plans are regenerated if you run the generator again (overwrites existing `_PLAN.md` files)
- The skill does NOT modify the original task file
- Plans are standalone markdown files that can be edited manually
- Action items in plans are checkboxes for easy tracking
