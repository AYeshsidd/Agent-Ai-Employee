# Silver Tier - Multi-Channel Watchers

## Overview

Silver Tier extends Bronze Tier with three additional watcher skills that monitor external communication channels and automatically create tasks in the Vault.

## Architecture

```
Bronze-tier/
├── skills/
│   └── watcher_skills/
│       ├── __init__.py
│       ├── base_watcher_skill.py      # Base class for all watchers
│       ├── gmail_watcher_skill.py     # Gmail inbox monitoring
│       ├── linkedin_watcher_skill.py  # LinkedIn messages monitoring
│       └── whatsapp_watcher_skill.py  # WhatsApp Web monitoring
├── run_multi_watcher.py               # Multi-channel watcher runner
└── credentials/                       # API credentials (not in git)
    ├── gmail_credentials.json
    ├── gmail_token.json
    ├── linkedin_session.json
    └── whatsapp_session.json
```

## Watcher Skills

### 1. GmailWatcherSkill

**Purpose**: Monitor Gmail inbox for unread emails and create tasks

**Features**:
- OAuth2 authentication with Gmail API
- Detects unread emails
- Extracts subject, sender, date, and body
- Prevents duplicate task creation
- Automatic token refresh

**Setup**:
1. Enable Gmail API in Google Cloud Console
2. Download OAuth2 credentials as `gmail_credentials.json`
3. Place in `Bronze-tier/credentials/` folder
4. First run will open browser for authentication
5. Token saved automatically for future use

**Task Format**:
```markdown
# Email: [Subject]

**Source**: Gmail
**Detected**: 2026-02-19 10:30:00
**Status**: [TODO]

## Content

[Email body content]

## Action Items

- [ ] Review gmail content
- [ ] Determine priority
- [ ] Take appropriate action

## Metadata

- **From**: sender@example.com
- **Date**: Wed, 19 Feb 2026 10:25:00
- **Message ID**: abc123xyz

#watcher #gmail #auto-generated
```

### 2. LinkedInWatcherSkill

**Purpose**: Monitor LinkedIn messages and notifications

**Features**:
- Playwright-based web automation
- Session persistence (no repeated logins)
- Detects unread message conversations
- Extracts sender, message preview, timestamp
- Prevents duplicate task creation

**Setup**:
1. Install Playwright browsers: `playwright install chromium`
2. First run will open browser for manual login
3. Session saved automatically for future use
4. Browser runs in non-headless mode for authentication

**Task Format**:
```markdown
# LinkedIn Message: [Sender Name]

**Source**: LinkedIn
**Detected**: 2026-02-19 10:30:00
**Status**: [TODO]

## Content

[Message preview]

## Action Items

- [ ] Review linkedin content
- [ ] Determine priority
- [ ] Take appropriate action

## Metadata

- **Sender**: John Doe
- **Timestamp**: 2h ago

#watcher #linkedin #auto-generated
```

### 3. WhatsAppWatcherSkill

**Purpose**: Monitor WhatsApp Web for unread messages

**Features**:
- Playwright-based web automation
- QR code authentication (first time)
- Session persistence
- Detects unread chats
- Extracts contact, message preview, unread count
- Prevents duplicate task creation

**Setup**:
1. Install Playwright browsers: `playwright install chromium`
2. First run will open browser with QR code
3. Scan QR code with WhatsApp mobile app
4. Session saved automatically for future use

**Task Format**:
```markdown
# WhatsApp Message: [Contact Name]

**Source**: WhatsApp
**Detected**: 2026-02-19 10:30:00
**Status**: [TODO]

## Content

[Last message preview]

## Action Items

- [ ] Review whatsapp content
- [ ] Determine priority
- [ ] Take appropriate action

## Metadata

- **Contact**: Jane Smith
- **Unread Count**: 3
- **Timestamp**: 10:25

#watcher #whatsapp #auto-generated
```

## Base Watcher Architecture

All watchers inherit from `BaseWatcherSkill` which provides:

- **Duplicate Prevention**: Tracks processed items in `logs/[watcher]_processed.txt`
- **Task Creation**: Standardized markdown task format
- **Logging**: Comprehensive logging to `logs/bronze_tier.log`
- **Lifecycle Tracking**: Logs transitions from source → Inbox
- **Abstract Methods**: `watch()` and `authenticate()` must be implemented

## Usage

### Running All Watchers

```bash
cd Bronze-tier
python run_multi_watcher.py
```

This will:
1. Initialize all three watchers
2. Authenticate with each service (if needed)
3. Check for new items every 5 minutes
4. Create tasks in Vault/Inbox
5. Log all activity

### Running Individual Watchers

```python
from skills.watcher_skills import GmailWatcherSkill

# Initialize
watcher = GmailWatcherSkill()

# Authenticate
if watcher.authenticate():
    # Watch for new items
    tasks_created = watcher.watch()
    print(f"Created {tasks_created} tasks")
```

### Configuration

Edit `run_multi_watcher.py` to enable/disable specific watchers:

```python
watcher.initialize_watchers(
    enable_gmail=True,      # Enable/disable Gmail
    enable_linkedin=False,  # Enable/disable LinkedIn
    enable_whatsapp=True    # Enable/disable WhatsApp
)
```

Change check interval (default: 300 seconds):

```python
watcher.run(interval_seconds=600)  # Check every 10 minutes
```

## Integration with Bronze Tier

Silver Tier watchers integrate seamlessly with Bronze Tier:

1. **Tasks Created in Inbox**: All watchers write to `Vault/Inbox/`
2. **Bronze Processing**: Run `main.py` to analyze and move to `Needs_Action/`
3. **Logging**: All activity logged to existing Bronze Tier logs
4. **Vault Manager**: Uses existing `vault_manager.py` for file operations
5. **No Breaking Changes**: Bronze Tier functionality remains unchanged

## Complete Workflow

```
Gmail/LinkedIn/WhatsApp → Inbox → Needs_Action → Done
         ↓                  ↓           ↓          ↓
   Multi-Watcher      TaskAnalyzer  Process   Complete
```

## Duplicate Prevention

Each watcher maintains a tracking file:
- `logs/gmail_processed.txt` - Gmail message IDs
- `logs/linkedin_processed.txt` - LinkedIn conversation IDs
- `logs/whatsapp_processed.txt` - WhatsApp chat IDs

Items are only processed once, even across multiple runs.

## Error Handling

- **Authentication Failures**: Logged and watcher skipped
- **Network Errors**: Logged and retry on next cycle
- **Missing Credentials**: Clear error message with setup instructions
- **Browser Crashes**: Logged and browser restarted on next cycle

## Logging

All watcher activity is logged to `logs/bronze_tier.log`:

```
2026-02-19 10:30:00 - GmailWatcher - INFO - [SKILL] GmailWatcherSkill | Operation: watch | Status: SUCCESS | Details: Created 3 tasks from 5 unread emails
2026-02-19 10:30:15 - LinkedInWatcher - INFO - [WATCHER] Event: TASK_CREATED | File: 20260219_103015_LinkedIn_Message.md | Status: SUCCESS
2026-02-19 10:30:30 - WhatsAppWatcher - INFO - [LIFECYCLE] Task: 20260219_103030_WhatsApp_Contact.md | Transition: WhatsApp -> Inbox | Status: SUCCESS
```

## Dependencies

```
google-api-python-client  # Gmail API
google-auth-httplib2      # Gmail OAuth2
google-auth-oauthlib      # Gmail OAuth2
playwright                # LinkedIn & WhatsApp automation
```

Install with:
```bash
pip install -r requirements.txt
playwright install chromium
```

## Security Notes

- **Credentials**: Never commit credentials to git
- **Sessions**: Session files contain authentication tokens
- **Tokens**: Gmail tokens auto-refresh, no password storage
- **Browser**: Playwright runs in visible mode for security
- **Logs**: Sensitive data not logged (only metadata)

## Troubleshooting

### Gmail Authentication Failed
- Verify `gmail_credentials.json` exists
- Check Google Cloud Console API is enabled
- Delete `gmail_token.json` and re-authenticate

### LinkedIn/WhatsApp Session Expired
- Delete session file: `linkedin_session.json` or `whatsapp_session.json`
- Re-run watcher and login manually

### Playwright Not Found
```bash
pip install playwright
playwright install chromium
```

### No Tasks Created
- Check logs: `logs/bronze_tier.log`
- Verify authentication successful
- Check for unread items in source platform

## Next Steps (Silver Tier Part 2)

- Dashboard for monitoring watcher status
- Web interface for task management
- Advanced filtering and routing rules
- Notification system for urgent tasks
