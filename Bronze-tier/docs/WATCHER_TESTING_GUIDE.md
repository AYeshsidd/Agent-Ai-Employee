# Silver Tier Watchers - Individual Testing Guide

## Overview

This guide provides step-by-step instructions for testing each watcher individually: Gmail, LinkedIn, and WhatsApp.

## Prerequisites

### General Requirements

```bash
cd Bronze-tier

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for LinkedIn and WhatsApp)
playwright install chromium
```

### Watcher-Specific Requirements

**Gmail Watcher:**
- Google Cloud Console account
- Gmail API enabled
- OAuth2 credentials (Desktop app)

**LinkedIn Watcher:**
- LinkedIn account
- Playwright installed

**WhatsApp Watcher:**
- WhatsApp account
- WhatsApp mobile app
- Playwright installed

---

## Test 1: Gmail Watcher

### Setup (First Time Only)

1. **Enable Gmail API**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it

2. **Create OAuth2 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Desktop app"
   - Name: "Gmail Watcher"
   - Click "Create"

3. **Download Credentials**
   - Click the download icon next to your credential
   - Save as `gmail_credentials.json`
   - Move to `Bronze-tier/credentials/gmail_credentials.json`

### Run Test

```bash
cd Bronze-tier
python test_gmail_watcher.py
```

### Expected Output

```
======================================================================
  GMAIL WATCHER - INDIVIDUAL TEST
======================================================================

[STEP 1] Initializing Gmail Watcher...
[OK] Gmail Watcher initialized

[STEP 2] Authenticating with Gmail...
[INFO] This will open a browser for OAuth2 authentication
[INFO] Make sure you have gmail_credentials.json in credentials/ folder
```

**First Run:**
- Browser opens automatically
- Login to your Google account
- Grant permissions to the app
- Token saved to `credentials/gmail_token.json`

**Subsequent Runs:**
- Uses saved token (no browser)
- Automatic authentication

```
[SUCCESS] Gmail authentication successful!

[STEP 3] Checking for unread emails...

[RESULT] Created 2 task(s) from unread emails

[SUCCESS] Gmail watcher is working!
[INFO] Check Vault/Inbox/ for created tasks

======================================================================
```

### Verify Results

```bash
# Check created tasks
ls Vault/Inbox/*Gmail*.md

# View a task
cat Vault/Inbox/[timestamp]_Gmail_[subject].md
```

### Troubleshooting

**"Credentials file not found"**
- Verify file exists: `ls credentials/gmail_credentials.json`
- Check file path is correct
- Re-download from Google Cloud Console

**"Authentication failed"**
- Delete token: `rm credentials/gmail_token.json`
- Run test again
- Make sure Gmail API is enabled

**"No unread emails found"**
- This is normal if inbox is empty
- Send yourself a test email
- Run test again

---

## Test 2: LinkedIn Watcher

### Setup (First Time Only)

1. **Install Playwright**
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Prepare LinkedIn Account**
   - Have your LinkedIn credentials ready
   - Make sure account is active
   - Have some unread messages (optional, for testing)

### Run Test

```bash
cd Bronze-tier
python test_linkedin_watcher.py
```

### Expected Output

```
======================================================================
  LINKEDIN WATCHER - INDIVIDUAL TEST
======================================================================

[STEP 1] Initializing LinkedIn Watcher...
[OK] LinkedIn Watcher initialized

[STEP 2] Authenticating with LinkedIn...
[INFO] This will open a browser window
[INFO] If not logged in, you'll need to login manually
[INFO] Session will be saved for future use

Press Enter to continue...
```

**Press Enter** - Browser opens

**First Run:**
- Browser opens to LinkedIn login page
- Login manually with your credentials
- Complete any security checks (2FA, etc.)
- Wait for redirect to feed/messaging
- Session saved to `credentials/linkedin_session.json`

**Subsequent Runs:**
- Browser opens already logged in
- No manual login required

```
[SUCCESS] LinkedIn authentication successful!

[STEP 3] Checking for unread LinkedIn messages...
[INFO] This may take a few seconds...

[RESULT] Created 1 task(s) from LinkedIn messages

[SUCCESS] LinkedIn watcher is working!
[INFO] Check Vault/Inbox/ for created tasks

[STEP 4] Closing browser...
[OK] Browser closed

======================================================================
```

### Verify Results

```bash
# Check created tasks
ls Vault/Inbox/*LinkedIn*.md

# View a task
cat Vault/Inbox/[timestamp]_LinkedIn_Message_[sender].md
```

### Troubleshooting

**"Playwright not installed"**
```bash
pip install playwright
playwright install chromium
```

**"Session expired"**
```bash
# Delete session and re-authenticate
rm credentials/linkedin_session.json
python test_linkedin_watcher.py
```

**"Could not find message elements"**
- LinkedIn UI may have changed
- Check logs: `tail -f logs/bronze_tier.log`
- Session may be expired - delete and retry

**"No unread messages found"**
- This is normal if no unread messages
- Send yourself a test message
- Run test again

---

## Test 3: WhatsApp Watcher

### Setup (First Time Only)

1. **Install Playwright**
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Prepare WhatsApp**
   - Have your phone with WhatsApp installed
   - Make sure phone has internet connection
   - Have some unread messages (optional, for testing)

### Run Test

```bash
cd Bronze-tier
python test_whatsapp_watcher.py
```

### Expected Output

```
======================================================================
  WHATSAPP WATCHER - INDIVIDUAL TEST
======================================================================

[STEP 1] Initializing WhatsApp Watcher...
[OK] WhatsApp Watcher initialized

[STEP 2] Authenticating with WhatsApp Web...
[INFO] This will open a browser window with WhatsApp Web
[INFO] If not logged in, you'll see a QR code
[INFO] Scan the QR code with your WhatsApp mobile app
[INFO] Session will be saved for future use

Press Enter to continue...
```

**Press Enter** - Browser opens

**First Run:**
- Browser opens to WhatsApp Web
- QR code displayed
- Open WhatsApp on your phone
- Go to Settings > Linked Devices
- Tap "Link a Device"
- Scan the QR code
- Wait for chats to load
- Session saved to `credentials/whatsapp_session.json`

**Subsequent Runs:**
- Browser opens already logged in
- No QR code required

```
[SUCCESS] WhatsApp Web authentication successful!

[STEP 3] Checking for unread WhatsApp messages...
[INFO] This may take a few seconds...

[RESULT] Created 3 task(s) from WhatsApp messages

[SUCCESS] WhatsApp watcher is working!
[INFO] Check Vault/Inbox/ for created tasks

[STEP 4] Closing browser...
[OK] Browser closed

======================================================================
```

### Verify Results

```bash
# Check created tasks
ls Vault/Inbox/*WhatsApp*.md

# View a task
cat Vault/Inbox/[timestamp]_WhatsApp_Message_[contact].md
```

### Troubleshooting

**"Playwright not installed"**
```bash
pip install playwright
playwright install chromium
```

**"QR code not appearing"**
- Wait 10-15 seconds for page to load
- Refresh browser manually
- Check internet connection

**"Session expired"**
```bash
# Delete session and re-authenticate
rm credentials/whatsapp_session.json
python test_whatsapp_watcher.py
```

**"Could not find chat elements"**
- WhatsApp Web UI may have changed
- Check logs: `tail -f logs/bronze_tier.log`
- Session may be expired - delete and retry

**"No unread messages found"**
- This is normal if no unread messages
- Send yourself a test message
- Run test again

---

## Testing Summary

### Quick Test Commands

```bash
# Test Gmail
python test_gmail_watcher.py

# Test LinkedIn
python test_linkedin_watcher.py

# Test WhatsApp
python test_whatsapp_watcher.py
```

### Expected Files After Testing

```
Bronze-tier/
├── credentials/
│   ├── gmail_credentials.json      # You provide
│   ├── gmail_token.json            # Auto-generated
│   ├── linkedin_session.json       # Auto-generated
│   └── whatsapp_session.json       # Auto-generated
├── logs/
│   ├── bronze_tier.log             # All activity
│   ├── gmail_processed.txt         # Duplicate tracking
│   ├── linkedin_processed.txt      # Duplicate tracking
│   └── whatsapp_processed.txt      # Duplicate tracking
└── Vault/
    └── Inbox/
        ├── [timestamp]_Gmail_[subject].md
        ├── [timestamp]_LinkedIn_Message_[sender].md
        └── [timestamp]_WhatsApp_Message_[contact].md
```

### Verification Checklist

After testing each watcher:

- [ ] Watcher initialized successfully
- [ ] Authentication completed
- [ ] Browser opened (LinkedIn/WhatsApp)
- [ ] Session saved to credentials/
- [ ] Tasks created in Vault/Inbox/
- [ ] Duplicate tracking file created in logs/
- [ ] Activity logged to logs/bronze_tier.log
- [ ] Browser closed properly (LinkedIn/WhatsApp)

### Common Issues

**All Watchers:**
- Check logs: `tail -f logs/bronze_tier.log`
- Verify credentials directory exists
- Check internet connection

**Gmail:**
- Verify Gmail API is enabled
- Check OAuth2 credentials are correct
- Delete token and re-authenticate if issues

**LinkedIn/WhatsApp:**
- Verify Playwright is installed
- Check browsers are installed: `playwright install chromium`
- Delete session files if authentication fails
- UI changes may break selectors - check logs

### Next Steps

After successful individual testing:

1. **Run All Watchers Together**
   ```bash
   python run_multi_watcher.py
   ```

2. **Process Created Tasks**
   ```bash
   python main.py
   ```

3. **Check Results**
   ```bash
   ls Vault/Needs_Action/
   ```

---

## Support

For issues:
1. Check logs: `logs/bronze_tier.log`
2. Review troubleshooting sections above
3. Verify all prerequisites are met
4. Test with fresh credentials/sessions
