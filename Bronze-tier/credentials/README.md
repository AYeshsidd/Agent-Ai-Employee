# Credentials Directory

This directory stores authentication credentials and session files for Silver Tier watchers.

## Required Files

### Gmail
- `gmail_credentials.json` - OAuth2 credentials from Google Cloud Console
- `gmail_token.json` - Auto-generated after first authentication

### LinkedIn
- `linkedin_session.json` - Auto-generated after first login

### WhatsApp
- `whatsapp_session.json` - Auto-generated after QR code scan

## Security

**IMPORTANT**: Never commit these files to git. They contain sensitive authentication data.

The `.gitignore` file should include:
```
credentials/
*.json
!credentials/README.md
```

## Setup Instructions

See `SILVER_TIER_WATCHERS.md` for detailed setup instructions for each watcher.
