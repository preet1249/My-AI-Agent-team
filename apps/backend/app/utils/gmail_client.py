"""
Gmail API Client for sending and receiving emails
Uses OAuth2 for authentication
"""
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict, Any
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class GmailClient:
    """
    Gmail API client wrapper
    - Send emails
    - Read emails
    - Set up push notifications
    """

    def __init__(self, credentials_json: Optional[str] = None):
        """
        Initialize Gmail client

        Args:
            credentials_json: Optional OAuth2 credentials JSON
        """
        self.credentials_json = credentials_json or settings.GMAIL_CREDENTIALS_JSON
        self.service = None

    def authenticate(self):
        """
        Authenticate with Gmail API using OAuth2

        For production, use service account or user OAuth2 flow
        """
        try:
            from googleapiclient.discovery import build
            from google.oauth2 import service_account
            import json

            # Parse credentials
            creds_dict = json.loads(self.credentials_json)

            # Create credentials from service account
            credentials = service_account.Credentials.from_service_account_info(
                creds_dict,
                scopes=['https://www.googleapis.com/auth/gmail.send',
                       'https://www.googleapis.com/auth/gmail.readonly']
            )

            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=credentials)

            logger.info("Gmail API authenticated successfully")
            return True

        except Exception as e:
            logger.error(f"Gmail authentication failed: {e}")
            return False

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> Optional[str]:
        """
        Send email via Gmail API

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (text or HTML)
            html: Whether body is HTML

        Returns:
            Message ID if successful, None otherwise
        """
        if not self.service:
            logger.error("Gmail service not authenticated")
            return None

        try:
            # Create message
            if html:
                message = MIMEMultipart('alternative')
                message.attach(MIMEText(body, 'html'))
            else:
                message = MIMEText(body)

            message['to'] = to_email
            message['subject'] = subject

            # Encode message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send via API
            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            message_id = result['id']
            logger.info(f"Email sent to {to_email}, message_id: {message_id}")

            return message_id

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return None

    def get_messages(
        self,
        max_results: int = 10,
        query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of messages from Gmail

        Args:
            max_results: Maximum number of messages to return
            query: Gmail search query (e.g., "is:unread")

        Returns:
            List of message dicts
        """
        if not self.service:
            logger.error("Gmail service not authenticated")
            return []

        try:
            # List messages
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()

            messages = results.get('messages', [])

            # Get full message details
            full_messages = []
            for msg in messages:
                msg_detail = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                full_messages.append(msg_detail)

            logger.info(f"Retrieved {len(full_messages)} messages from Gmail")
            return full_messages

        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []

    def setup_push_notifications(self, webhook_url: str, topic_name: str):
        """
        Set up Gmail push notifications via Pub/Sub

        Args:
            webhook_url: URL to receive notifications
            topic_name: Pub/Sub topic name

        Returns:
            True if successful
        """
        if not self.service:
            logger.error("Gmail service not authenticated")
            return False

        try:
            # Watch for new messages
            request = {
                'labelIds': ['INBOX'],
                'topicName': topic_name
            }

            result = self.service.users().watch(
                userId='me',
                body=request
            ).execute()

            logger.info(f"Gmail push notifications set up: {result}")
            return True

        except Exception as e:
            logger.error(f"Failed to setup push notifications: {e}")
            return False

    def parse_email_content(self, message: dict) -> Dict[str, Any]:
        """
        Parse Gmail API message into readable format

        Args:
            message: Gmail API message object

        Returns:
            Dict with from, to, subject, body
        """
        headers = message.get('payload', {}).get('headers', [])

        # Extract headers
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
        to_email = next((h['value'] for h in headers if h['name'] == 'To'), '')
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')

        # Extract body
        payload = message.get('payload', {})
        parts = payload.get('parts', [])

        body = ''
        if parts:
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode()
                    break
        else:
            # Single part message
            body_data = payload.get('body', {}).get('data', '')
            if body_data:
                body = base64.urlsafe_b64decode(body_data).decode()

        return {
            'from': from_email,
            'to': to_email,
            'subject': subject,
            'body': body,
            'message_id': message['id'],
            'thread_id': message.get('threadId', '')
        }


# Global instance (will need credentials to authenticate)
gmail_client = GmailClient()
