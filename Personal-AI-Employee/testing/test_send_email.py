#!/usr/bin/env python3
"""Test MCP Server - Send Real Email"""
import sys
from pathlib import Path

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from mcp_server import get_server
import json


def main():
    print("\n" + "=" * 70)
    print("  MCP SERVER - SEND TEST EMAIL")
    print("=" * 70)

    # Get recipient email from command line
    if len(sys.argv) < 2:
        print("\n[ERROR] Usage: python test_send_email.py <recipient_email>")
        print("[EXAMPLE] python test_send_email.py user@example.com")
        return

    recipient = sys.argv[1].strip()

    if not recipient or '@' not in recipient:
        print("[ERROR] Invalid email address")
        return

    print("\n[INFO] This will send a real test email via Gmail")
    print("[INFO] Make sure you have gmail_credentials.json configured")
    print(f"[INFO] Recipient: {recipient}")

    # Initialize MCP server
    print("\n[STEP 1] Initializing MCP Server...")
    server = get_server()
    print("[OK] MCP Server initialized")

    # Prepare email
    email_params = {
        "to": recipient,
        "subject": "Test Email from MCP Server",
        "body": """Hello!

This is a test email sent from the MCP Server (Silver Tier Part 4).

The MCP Server is working correctly and can send emails via Gmail API.

Features tested:
- Gmail API integration
- OAuth2 authentication
- Email composition and sending

If you received this email, the MCP Server is fully functional!

---
Sent via MCP Server
Autonomous FTE System - Silver Tier
"""
    }

    print("\n[STEP 2] Sending email...")
    print(f"  To: {email_params['to']}")
    print(f"  Subject: {email_params['subject']}")
    print()

    # Send email
    result = server.call_tool("send_email", email_params)

    # Display result
    print("\n[RESULT]")
    print(json.dumps(result, indent=2))

    if result.get("status") == "success":
        print("\n[SUCCESS] Email sent successfully!")
        print(f"[INFO] Check {recipient} inbox")
    else:
        print("\n[FAILED] Email sending failed")
        print(f"[ERROR] {result.get('message')}")

        # Provide troubleshooting
        if "authentication failed" in result.get('message', '').lower():
            print("\n[TROUBLESHOOTING]")
            print("Gmail authentication failed. This usually means:")
            print("1. OAuth token needs 'gmail.send' scope")
            print("2. Current token only has 'gmail.readonly' scope")
            print()
            print("To fix:")
            print("1. Go to Google Cloud Console")
            print("2. Update OAuth consent screen to include 'gmail.send' scope")
            print("3. Delete credentials/gmail_token.json")
            print("4. Run this script again to re-authenticate")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
