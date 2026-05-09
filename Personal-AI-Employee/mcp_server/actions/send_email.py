#!/usr/bin/env python3
"""Send Email Action - MCP Server"""
from pathlib import Path
from typing import Dict
import sys

# Add Bronze-tier to path to access existing Gmail auth
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import Config


class SendEmailAction:
    """Action to send emails using existing Gmail credentials"""

    def __init__(self):
        self.credentials_file = Config.BASE_DIR / "credentials" / "gmail_credentials.json"
        self.token_file = Config.BASE_DIR / "credentials" / "gmail_token.json"
        self.service = None

    def authenticate(self) -> bool:
        """Authenticate with Gmail API using existing credentials"""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build

            # Combined scopes for both reading and sending emails
            SCOPES = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.send'
            ]

            creds = None

            # Load existing token
            if self.token_file.exists():
                creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)

            # Refresh or create new token
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not self.credentials_file.exists():
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file), SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save token
                self.token_file.parent.mkdir(exist_ok=True)
                self.token_file.write_text(creds.to_json())

            self.service = build('gmail', 'v1', credentials=creds)
            return True

        except Exception as e:
            print(f"[ERROR] Gmail authentication failed: {str(e)}")
            return False

    def execute(self, params: Dict[str, str]) -> Dict[str, str]:
        """
        Send email via Gmail API

        Args:
            params: Dictionary with 'to', 'subject', 'body'

        Returns:
            Dictionary with 'status' and 'message'
        """
        # Validate input
        if not params.get('to'):
            return {"status": "failed", "message": "Missing 'to' field"}

        if not params.get('subject'):
            return {"status": "failed", "message": "Missing 'subject' field"}

        if not params.get('body'):
            return {"status": "failed", "message": "Missing 'body' field"}

        try:
            # Authenticate if not already done
            if not self.service:
                if not self.authenticate():
                    return {
                        "status": "failed",
                        "message": "Gmail authentication failed"
                    }

            # Create email message
            from email.mime.text import MIMEText
            import base64

            message = MIMEText(params['body'])
            message['to'] = params['to']
            message['subject'] = params['subject']

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send email
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            return {
                "status": "success",
                "message": f"Email sent successfully (ID: {send_message['id']})"
            }

        except Exception as e:
            return {
                "status": "failed",
                "message": f"Failed to send email: {str(e)}"
            }


if __name__ == "__main__":
    # Quick test
    action = SendEmailAction()
    print("Send Email Action initialized")
