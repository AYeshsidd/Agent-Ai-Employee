# Silver Tier Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd Bronze-tier
pip install -r requirements.txt
playwright install chromium
```

### 2. Setup Gmail Watcher (Optional)

**Step 1**: Enable Gmail API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials as JSON

**Step 2**: Configure
```bash
# Place credentials file
cp ~/Downloads/credentials.json Bronze-tier/credentials/gmail_credentials.json
```

**Step 3**: First Run
```bash
python run_multi_watcher.py
# Browser will open for Gmail authentication
# Authorize the app
# Token saved automatically
```

### 3. Setup LinkedIn Watcher (Optional)

**Step 1**: First Run
```bash
python run_multi_watcher.py
# Browser will open to LinkedIn
# Login manually
# Session saved automatically
```

**Step 2**: Subsequent Runs
- No login required
- Session persists until expired

### 4. Setup WhatsApp Watcher (Optional)

**Step 1**: First Run
```bash
python run_multi_watcher.py
# Browser will open with QR code
# Scan with WhatsApp mobile app
# Session saved automatically
```

**Step 2**: Subsequent Runs
- No QR code required
- Session persists

## Usage

### Run All Watchers

```bash
cd Bronze-tier
python run_multi_watcher.py
```

Output:
```
======================================================================
  Silver Tier - Multi-Channel Watcher
======================================================================

Active watchers: gmail, linkedin, whatsapp
Check interval: 300 seconds

Press Ctrl+C to stop

======================================================================
  Watch Cycle #1
======================================================================

[GMAIL] Checking for new items...
[GMAIL] Created 2 new task(s)

[LINKEDIN] Checking for new items...
[LINKEDIN] No new items

[WHATSAPP] Checking for new items...
[WHATSAPP] Created 1 new task(s)

[SUMMARY] Cycle #1 complete: 3 total task(s) created

Waiting 300 seconds until next check...
```

### Configure Watchers

Edit `run_multi_watcher.py`:

```python
# Enable/disable specific watchers
watcher.initialize_watchers(
    enable_gmail=True,      # Set to False to disable
    enable_linkedin=False,  # Set to False to disable
    enable_whatsapp=True    # Set to False to disable
)

# Change check interval (seconds)
watcher.run(interval_seconds=600)  # Check every 10 minutes
```

### Process Created Tasks

After watchers create tasks in Inbox:

```bash
# Run Bronze Tier processor
python main.py
```

This will:
1. Read tasks from Inbox
2. Analyze with TaskAnalyzerSkill
3. Move to Needs_Action with structured format

## Complete Workflow

```
┌─────────────────────────────────────────────────────────┐
│                   Silver Tier Watchers                  │
├─────────────────────────────────────────────────────────┤
│  Gmail    │  LinkedIn  │  WhatsApp  │  File System     │
│  (API)    │ (Playwright)│ (Playwright)│  (watchdog)     │
└─────┬───────────┬──────────┬──────────────┬────────────┘
      │           │          │              │
      └───────────┴──────────┴──────────────┘
                      ↓
              ┌──────────────┐
              │ Vault/Inbox  │
              └──────┬───────┘
                     ↓
              ┌──────────────┐
              │   main.py    │
              │ (Analyzer)   │
              └──────┬───────┘
                     ↓
         ┌─────────────────────┐
         │ Vault/Needs_Action  │
         └──────────┬──────────┘
                    ↓
         ┌─────────────────────┐
         │    Vault/Done       │
         └─────────────────────┘
```

## Troubleshooting

### Gmail: "Credentials not found"
```bash
# Verify file exists
ls Bronze-tier/credentials/gmail_credentials.json

# If missing, download from Google Cloud Console
```

### LinkedIn/WhatsApp: "Session expired"
```bash
# Delete session file
rm Bronze-tier/credentials/linkedin_session.json
rm Bronze-tier/credentials/whatsapp_session.json

# Re-run and login again
python run_multi_watcher.py
```

### Playwright: "Browser not found"
```bash
# Install Playwright browsers
playwright install chromium
```

### No tasks created
```bash
# Check logs
tail -f Bronze-tier/logs/bronze_tier.log

# Verify authentication
# Check for unread items in source platform
```

## File Structure

```
Bronze-tier/
├── credentials/              # Authentication files (not in git)
│   ├── README.md
│   ├── gmail_credentials.json
│   ├── gmail_token.json
│   ├── linkedin_session.json
│   └── whatsapp_session.json
├── logs/
│   ├── bronze_tier.log       # All activity
│   ├── gmail_processed.txt   # Duplicate tracking
│   ├── linkedin_processed.txt
│   └── whatsapp_processed.txt
├── skills/
│   └── watcher_skills/
│       ├── base_watcher_skill.py
│       ├── gmail_watcher_skill.py
│       ├── linkedin_watcher_skill.py
│       └── whatsapp_watcher_skill.py
├── Vault/
│   ├── Inbox/               # Tasks created by watchers
│   ├── Needs_Action/        # Analyzed tasks
│   └── Done/                # Completed tasks
├── run_multi_watcher.py     # Silver Tier runner
└── main.py                  # Bronze Tier processor
```

## Security Best Practices

1. **Never commit credentials**
   - `.gitignore` protects credential files
   - Verify before committing: `git status`

2. **Rotate tokens regularly**
   - Delete token files periodically
   - Re-authenticate to get fresh tokens

3. **Use separate Google project**
   - Don't use production credentials
   - Create dedicated project for automation

4. **Monitor logs**
   - Check for authentication failures
   - Review created tasks regularly

5. **Limit API access**
   - Gmail: Read-only scope
   - LinkedIn/WhatsApp: Manual login only

## Performance Tips

1. **Adjust check interval**
   - Default: 5 minutes (300 seconds)
   - Increase for less frequent checks
   - Decrease for more responsive monitoring

2. **Disable unused watchers**
   - Only enable watchers you need
   - Reduces resource usage

3. **Limit message count**
   - Gmail: `maxResults=10` in code
   - LinkedIn/WhatsApp: Process first 10 unread

4. **Run in background**
   ```bash
   # Linux/Mac
   nohup python run_multi_watcher.py > watcher.out 2>&1 &

   # Windows
   start /B python run_multi_watcher.py
   ```

## Integration with Bronze Tier

Silver Tier is fully compatible with Bronze Tier:

- ✓ Uses same Vault structure
- ✓ Uses same logging system
- ✓ Uses same VaultManager
- ✓ Tasks compatible with Bronze Tier processor
- ✓ No breaking changes to Bronze Tier

Run both simultaneously:
```bash
# Terminal 1: Silver Tier watchers
python run_multi_watcher.py

# Terminal 2: Bronze Tier file watcher
python run_watcher.py

# Terminal 3: Process inbox periodically
watch -n 300 python main.py  # Every 5 minutes
```

## Next Steps

After Silver Tier Part 1:
- **Part 2**: Dashboard and web interface
- **Part 3**: Advanced filtering and routing
- **Part 4**: Notification system
- **Gold Tier**: AI-powered task prioritization
