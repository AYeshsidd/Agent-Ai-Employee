# Silver Tier Part 6: Windows Task Scheduler Setup

## Overview

Automated scheduling for Bronze-tier autonomous task management system using Windows Task Scheduler.

**Components:**
1. Gmail Watcher (every 5 minutes)
2. LinkedIn Watcher (every 10 minutes)
3. MCP Approval Check (every 3 minutes)
4. LinkedIn Auto Post (daily at 9 AM)

---

## Prerequisites

✅ Python installed and accessible via PATH
✅ All Bronze-tier dependencies installed
✅ Working directory: `D:\Autonomus-fte\Bronze-tier`
✅ All credentials configured (Gmail, LinkedIn)

---

## Wrapper Scripts Created

All scripts include:
- File-based lock mechanism (prevents overlapping executions)
- Proper error handling and logging
- Stale lock detection and cleanup
- Silent exit if already running

**Files:**
- `scheduled_gmail_watcher.py`
- `scheduled_linkedin_watcher.py`
- `scheduled_approval_check.py`
- `scheduled_linkedin_auto_post.py`

---

## Task Scheduler Configuration

### Task 1: Gmail Watcher (Every 5 Minutes)

**Open Task Scheduler:**
1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click "Create Basic Task" in right panel

**Basic Task Settings:**
- **Name:** `Bronze-Gmail-Watcher`
- **Description:** `Monitors Gmail inbox every 5 minutes and creates tasks in Vault`

**Trigger:**
- **Type:** Daily
- **Start:** Today at 12:00 AM
- **Recur every:** 1 day
- **Repeat task every:** 5 minutes
- **For a duration of:** 1 day
- ✅ Enabled

**Action:**
- **Action:** Start a program
- **Program/script:** `python`
- **Add arguments:** `scheduled_gmail_watcher.py`
- **Start in:** `D:\Autonomus-fte\Bronze-tier`

**Conditions:**
- ❌ Start the task only if the computer is on AC power (uncheck)
- ❌ Stop if the computer switches to battery power (uncheck)
- ✅ Wake the computer to run this task (optional)

**Settings:**
- ✅ Allow task to be run on demand
- ✅ Run task as soon as possible after a scheduled start is missed
- ❌ Stop the task if it runs longer than: (uncheck - lock handles this)
- **If the running task does not end when requested:** Do not start a new instance

---

### Task 2: LinkedIn Watcher (Every 10 Minutes)

**Basic Task Settings:**
- **Name:** `Bronze-LinkedIn-Watcher`
- **Description:** `Monitors LinkedIn messages every 10 minutes and creates tasks in Vault`

**Trigger:**
- **Type:** Daily
- **Start:** Today at 12:00 AM
- **Recur every:** 1 day
- **Repeat task every:** 10 minutes
- **For a duration of:** 1 day
- ✅ Enabled

**Action:**
- **Program/script:** `python`
- **Add arguments:** `scheduled_linkedin_watcher.py`
- **Start in:** `D:\Autonomus-fte\Bronze-tier`

**Conditions:**
- ❌ Start the task only if the computer is on AC power (uncheck)
- ❌ Stop if the computer switches to battery power (uncheck)

**Settings:**
- ✅ Allow task to be run on demand
- ✅ Run task as soon as possible after a scheduled start is missed
- **If the running task does not end when requested:** Do not start a new instance

---

### Task 3: MCP Approval Check (Every 3 Minutes)

**Basic Task Settings:**
- **Name:** `Bronze-Approval-Check`
- **Description:** `Checks for pending MCP approvals every 3 minutes`

**Trigger:**
- **Type:** Daily
- **Start:** Today at 12:00 AM
- **Recur every:** 1 day
- **Repeat task every:** 3 minutes
- **For a duration of:** 1 day
- ✅ Enabled

**Action:**
- **Program/script:** `python`
- **Add arguments:** `scheduled_approval_check.py`
- **Start in:** `D:\Autonomus-fte\Bronze-tier`

**Conditions:**
- ❌ Start the task only if the computer is on AC power (uncheck)
- ❌ Stop if the computer switches to battery power (uncheck)

**Settings:**
- ✅ Allow task to be run on demand
- ✅ Run task as soon as possible after a scheduled start is missed
- **If the running task does not end when requested:** Do not start a new instance

---

### Task 4: LinkedIn Auto Post (Daily at 9 AM)

**Basic Task Settings:**
- **Name:** `Bronze-LinkedIn-Auto-Post`
- **Description:** `Posts content from Vault/Needs_Action to LinkedIn daily at 9 AM`

**Trigger:**
- **Type:** Daily
- **Start:** Today at 9:00 AM
- **Recur every:** 1 day
- ✅ Enabled

**Action:**
- **Program/script:** `python`
- **Add arguments:** `scheduled_linkedin_auto_post.py`
- **Start in:** `D:\Autonomus-fte\Bronze-tier`

**Conditions:**
- ❌ Start the task only if the computer is on AC power (uncheck)
- ❌ Stop if the computer switches to battery power (uncheck)
- ✅ Wake the computer to run this task (optional)

**Settings:**
- ✅ Allow task to be run on demand
- ✅ Run task as soon as possible after a scheduled start is missed
- **If the running task does not end when requested:** Do not start a new instance

---

## Quick Setup via PowerShell (Alternative Method)

If you prefer command-line setup, use these PowerShell commands (run as Administrator):

```powershell
# Task 1: Gmail Watcher (every 5 minutes)
$action = New-ScheduledTaskAction -Execute "python" -Argument "scheduled_gmail_watcher.py" -WorkingDirectory "D:\Autonomus-fte\Bronze-tier"
$trigger = New-ScheduledTaskTrigger -Daily -At "12:00AM" -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 1)
Register-ScheduledTask -TaskName "Bronze-Gmail-Watcher" -Action $action -Trigger $trigger -Description "Monitors Gmail inbox every 5 minutes"

# Task 2: LinkedIn Watcher (every 10 minutes)
$action = New-ScheduledTaskAction -Execute "python" -Argument "scheduled_linkedin_watcher.py" -WorkingDirectory "D:\Autonomus-fte\Bronze-tier"
$trigger = New-ScheduledTaskTrigger -Daily -At "12:00AM" -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetitionDuration (New-TimeSpan -Days 1)
Register-ScheduledTask -TaskName "Bronze-LinkedIn-Watcher" -Action $action -Trigger $trigger -Description "Monitors LinkedIn messages every 10 minutes"

# Task 3: Approval Check (every 3 minutes)
$action = New-ScheduledTaskAction -Execute "python" -Argument "scheduled_approval_check.py" -WorkingDirectory "D:\Autonomus-fte\Bronze-tier"
$trigger = New-ScheduledTaskTrigger -Daily -At "12:00AM" -RepetitionInterval (New-TimeSpan -Minutes 3) -RepetitionDuration (New-TimeSpan -Days 1)
Register-ScheduledTask -TaskName "Bronze-Approval-Check" -Action $action -Trigger $trigger -Description "Checks for pending MCP approvals every 3 minutes"

# Task 4: LinkedIn Auto Post (daily at 9 AM)
$action = New-ScheduledTaskAction -Execute "python" -Argument "scheduled_linkedin_auto_post.py" -WorkingDirectory "D:\Autonomus-fte\Bronze-tier"
$trigger = New-ScheduledTaskTrigger -Daily -At "9:00AM"
Register-ScheduledTask -TaskName "Bronze-LinkedIn-Auto-Post" -Action $action -Trigger $trigger -Description "Posts content from Vault to LinkedIn daily at 9 AM"
```

---

## Verification Checklist

### Step 1: Test Scripts Manually

Before scheduling, test each script manually:

```bash
cd D:\Autonomus-fte\Bronze-tier

# Test Gmail Watcher
python scheduled_gmail_watcher.py

# Test LinkedIn Watcher
python scheduled_linkedin_watcher.py

# Test Approval Check
python scheduled_approval_check.py

# Test LinkedIn Auto Post
python scheduled_linkedin_auto_post.py
```

**Expected Output:**
- `[START]` timestamp
- Script execution logs
- `[SUCCESS]` or `[FAILED]` status
- `[END]` timestamp

### Step 2: Verify Lock Files

After running scripts, check for lock files:

```bash
dir logs\*.lock
```

**Expected:**
- Lock files created during execution
- Lock files removed after completion
- If lock exists, check age (should be recent if running)

### Step 3: Test Task Scheduler Execution

1. Open Task Scheduler (`taskschd.msc`)
2. Find your task in Task Scheduler Library
3. Right-click → Run
4. Check "Last Run Result" column (should be `0x0` for success)
5. Check "Last Run Time" (should be recent)

### Step 4: Monitor Logs

Check execution logs:

```bash
# View recent logs
type logs\bronze_tier.log | findstr /C:"Scheduled"

# Check for errors
type logs\bronze_tier.log | findstr /C:"FAILED"
```

### Step 5: Verify Task Creation

After Gmail/LinkedIn watchers run:

```bash
# Check Vault inbox
dir Vault\Inbox\*.md

# Check for new tasks
dir Vault\Inbox\*Gmail*.md
dir Vault\Inbox\*LinkedIn*.md
```

---

## Troubleshooting

### Issue 1: Task Shows "Running" But Nothing Happens

**Symptoms:**
- Task Scheduler shows task as "Running"
- No output in logs
- Lock file exists

**Causes:**
- Python not in PATH
- Working directory incorrect
- Script has syntax error

**Solutions:**

1. **Verify Python PATH:**
   ```bash
   where python
   ```
   Should show Python executable path.

2. **Use Full Python Path:**
   Instead of `python`, use full path:
   ```
   C:\Users\YourUser\AppData\Local\Programs\Python\Python313\python.exe
   ```

3. **Check Task History:**
   - Task Scheduler → View → Show Task History
   - Look for error codes

### Issue 2: Lock File Prevents Execution

**Symptoms:**
- Script exits immediately with `[SKIP]` message
- Lock file exists in `logs/` folder

**Solution:**

```bash
# Remove stale locks
del logs\*.lock

# Or wait for stale lock timeout (varies by script)
```

### Issue 3: Authentication Fails in Scheduled Task

**Symptoms:**
- Manual execution works
- Scheduled execution fails with auth error

**Causes:**
- Credentials not accessible to Task Scheduler user
- Browser profile not accessible

**Solutions:**

1. **Run task as your user account:**
   - Task Scheduler → Task Properties → General tab
   - "When running the task, use the following user account:" → Your account
   - ✅ "Run whether user is logged on or not"
   - Enter your password

2. **Check credential files:**
   ```bash
   dir credentials\*.json
   ```
   Ensure files exist and are readable.

### Issue 4: Browser Opens But Task Fails

**Symptoms:**
- Browser window opens
- Task fails after timeout
- Works manually

**Causes:**
- Task Scheduler runs in Session 0 (no GUI)
- Browser needs interactive session

**Solutions:**

1. **Run only when user is logged on:**
   - Task Properties → General tab
   - ✅ "Run only when user is logged on"

2. **For LinkedIn/WhatsApp (browser-based):**
   - These tasks require active user session
   - Schedule during hours when you're logged in

### Issue 5: Multiple Instances Running

**Symptoms:**
- Multiple lock files
- Duplicate task creation
- High CPU usage

**Solution:**

1. **Verify task settings:**
   - Task Properties → Settings tab
   - "If the task is already running:" → "Do not start a new instance"

2. **Check lock mechanism:**
   ```bash
   # View lock files with timestamps
   dir /TC logs\*.lock
   ```

---

## Best Practices

### 1. Staggered Scheduling

Avoid all tasks running simultaneously:

- **Approval Check:** Every 3 minutes (00:00, 00:03, 00:06, ...)
- **Gmail Watcher:** Every 5 minutes (00:00, 00:05, 00:10, ...)
- **LinkedIn Watcher:** Every 10 minutes (00:00, 00:10, 00:20, ...)
- **LinkedIn Auto Post:** Once daily at 9:00 AM

### 2. Monitor Resource Usage

Check system resources periodically:

```bash
# Check running Python processes
tasklist | findstr python

# Check CPU usage
wmic cpu get loadpercentage
```

### 3. Log Rotation

Prevent log files from growing too large:

```bash
# Archive old logs monthly
move logs\bronze_tier.log logs\bronze_tier_%date:~-4,4%%date:~-7,2%.log
```

### 4. Credential Refresh

OAuth tokens expire. Monitor for auth failures:

```bash
# Check for auth errors
type logs\bronze_tier.log | findstr /C:"authentication failed"
```

If found, re-authenticate manually:

```bash
python test_gmail_watcher.py
python test_linkedin_watcher.py
```

### 5. Disable During Maintenance

When updating code:

```bash
# Disable all Bronze tasks
schtasks /Change /TN "Bronze-Gmail-Watcher" /DISABLE
schtasks /Change /TN "Bronze-LinkedIn-Watcher" /DISABLE
schtasks /Change /TN "Bronze-Approval-Check" /DISABLE
schtasks /Change /TN "Bronze-LinkedIn-Auto-Post" /DISABLE

# After updates, re-enable
schtasks /Change /TN "Bronze-Gmail-Watcher" /ENABLE
schtasks /Change /TN "Bronze-LinkedIn-Watcher" /ENABLE
schtasks /Change /TN "Bronze-Approval-Check" /ENABLE
schtasks /Change /TN "Bronze-LinkedIn-Auto-Post" /ENABLE
```

---

## Production Deployment Checklist

### Pre-Deployment

- [ ] All wrapper scripts tested manually
- [ ] Lock mechanism verified
- [ ] Credentials configured and working
- [ ] Log directory exists (`logs/`)
- [ ] Vault directories exist (`Vault/Inbox`, `Vault/Needs_Action`, `Vault/Done`)

### Deployment

- [ ] Task 1 (Gmail Watcher) created and enabled
- [ ] Task 2 (LinkedIn Watcher) created and enabled
- [ ] Task 3 (Approval Check) created and enabled
- [ ] Task 4 (LinkedIn Auto Post) created and enabled
- [ ] All tasks tested via "Run" in Task Scheduler
- [ ] "Last Run Result" shows success (0x0)

### Post-Deployment Monitoring (First 24 Hours)

- [ ] Check logs every 2 hours for errors
- [ ] Verify tasks are creating Vault items
- [ ] Monitor lock files (should be created/removed properly)
- [ ] Check system resource usage
- [ ] Verify no duplicate executions

### Weekly Maintenance

- [ ] Review logs for authentication failures
- [ ] Check Vault for task accumulation
- [ ] Verify approval system working
- [ ] Archive old logs
- [ ] Update credentials if needed

---

## Summary

### What Was Implemented

✅ 4 wrapper scripts with lock protection
✅ Windows Task Scheduler configuration
✅ Comprehensive troubleshooting guide
✅ Best practices documentation
✅ Production deployment checklist

### Scheduled Tasks

| Task | Frequency | Purpose |
|------|-----------|---------|
| Gmail Watcher | Every 5 min | Monitor inbox, create tasks |
| LinkedIn Watcher | Every 10 min | Monitor messages, create tasks |
| Approval Check | Every 3 min | Check pending approvals |
| LinkedIn Auto Post | Daily 9 AM | Post from Vault to LinkedIn |

### Key Features

- **Lock Protection:** Prevents overlapping executions
- **Stale Lock Detection:** Auto-cleanup of old locks
- **Error Handling:** Comprehensive logging
- **Silent Failures:** No popup errors
- **Production-Safe:** Tested and documented

### Status

✅ Silver Tier Part 6 Complete
✅ Ready for production deployment
✅ Fully documented with troubleshooting
