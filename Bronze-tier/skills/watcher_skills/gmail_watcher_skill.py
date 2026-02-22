from pathlib import Path
from typing import Dict, List, Optional
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from skills.watcher_skills.base_watcher_skill import BaseWatcherSkill
from bronze_logger import BronzeLogger
from config import Config


class GmailWatcherSkill(BaseWatcherSkill):
    """Agent skill for watching Gmail inbox and creating tasks"""

    def __init__(self):
        super().__init__("Gmail")
        self.gmail_service = None
        self.credentials_path = Config.BASE_DIR / "credentials" / "gmail_credentials.json"
        self.token_path = Config.BASE_DIR / "credentials" / "gmail_token.json"

    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build

            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

            creds = None

            # Load existing token
            if self.token_path.exists():
                creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

            # If no valid credentials, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not self.credentials_path.exists():
                        BronzeLogger.log_skill_execution(
                            self.logger, "GmailWatcherSkill", "authenticate",
                            "FAILED", f"Credentials file not found: {self.credentials_path}"
                        )
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_path), SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save credentials
                self.token_path.parent.mkdir(exist_ok=True)
                self.token_path.write_text(creds.to_json())

            self.gmail_service = build('gmail', 'v1', credentials=creds)

            BronzeLogger.log_skill_execution(
                self.logger, "GmailWatcherSkill", "authenticate",
                "SUCCESS", "Gmail API authenticated"
            )
            return True

        except ImportError as e:
            BronzeLogger.log_skill_execution(
                self.logger, "GmailWatcherSkill", "authenticate",
                "FAILED", f"Missing required library: {str(e)}"
            )
            return False
        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "GmailWatcherSkill", "authenticate",
                "FAILED", str(e)
            )
            return False

    def watch(self) -> int:
        """
        Watch Gmail inbox for unread emails and create tasks

        Returns:
            Number of new tasks created
        """
        BronzeLogger.log_skill_execution(
            self.logger, "GmailWatcherSkill", "watch",
            "IN_PROGRESS", "Checking Gmail inbox"
        )

        if not self.gmail_service:
            if not self.authenticate():
                return 0

        try:
            # Get unread messages
            results = self.gmail_service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                BronzeLogger.log_skill_execution(
                    self.logger, "GmailWatcherSkill", "watch",
                    "SUCCESS", "No unread emails found"
                )
                return 0

            tasks_created = 0

            for message in messages:
                message_id = message['id']

                # Check for duplicates
                if self.is_duplicate(message_id):
                    continue

                # Get full message details
                msg = self.gmail_service.users().messages().get(
                    userId='me',
                    id=message_id,
                    format='full'
                ).execute()

                # Extract email details
                email_data = self._extract_email_data(msg)

                # Create task
                task_path = self.create_task_in_inbox(
                    title=f"Email: {email_data['subject']}",
                    content=email_data['body'],
                    source="Gmail",
                    metadata={
                        "From": email_data['from'],
                        "Date": email_data['date'],
                        "Message ID": message_id
                    }
                )

                if task_path:
                    self._save_processed_id(message_id)
                    tasks_created += 1

            BronzeLogger.log_skill_execution(
                self.logger, "GmailWatcherSkill", "watch",
                "SUCCESS", f"Created {tasks_created} tasks from {len(messages)} unread emails"
            )

            return tasks_created

        except Exception as e:
            BronzeLogger.log_skill_execution(
                self.logger, "GmailWatcherSkill", "watch",
                "FAILED", str(e)
            )
            return 0

    def _extract_email_data(self, message: Dict) -> Dict[str, str]:
        """Extract relevant data from Gmail message"""
        import base64

        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

        # Extract body
        body = ""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')

        # Truncate long bodies
        if len(body) > 1000:
            body = body[:1000] + "\n\n[Content truncated...]"

        return {
            'subject': subject,
            'from': from_email,
            'date': date,
            'body': body or '[No text content]'
        }
