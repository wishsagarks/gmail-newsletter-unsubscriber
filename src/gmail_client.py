"""Gmail API client wrapper."""

import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from typing import List, Dict, Optional

from config import DAYS_TO_SCAN, MAX_MESSAGES, GMAIL_QUERY


class GmailClient:
    """Wrapper for Gmail API operations."""
    
    def __init__(self, service):
        self.service = service
    
    def fetch_recent_messages(self, days: int = DAYS_TO_SCAN, max_results: int = MAX_MESSAGES) -> List[Dict]:
        """
        Fetch recent messages matching newsletter criteria.
        
        Args:
            days: Number of days to look back
            max_results: Maximum messages to fetch
        
        Returns:
            List of message metadata dicts
        """
        # Calculate date for query
        after_date = datetime.now() - timedelta(days=days)
        date_str = after_date.strftime('%Y/%m/%d')
        
        query = f"{GMAIL_QUERY} after:{date_str}"
        
        print(f"Fetching messages from last {days} days...")
        print(f"Query: {query}\n")
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            print(f"✓ Found {len(messages)} messages to analyze\n")
            return messages
        
        except Exception as e:
            print(f"✗ Error fetching messages: {e}")
            return []
    
    def get_message_details(self, message_id: str) -> Optional[Dict]:
        """
        Get full message details including headers and body.
        
        Args:
            message_id: Gmail message ID
        
        Returns:
            Message details dict or None
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            return message
        except Exception as e:
            print(f"✗ Error fetching message {message_id}: {e}")
            return None
    
    def get_header(self, message: Dict, header_name: str) -> Optional[str]:
        """Extract specific header from message."""
        headers = message.get('payload', {}).get('headers', [])
        for header in headers:
            if header['name'].lower() == header_name.lower():
                return header['value']
        return None
    
    def get_body(self, message: Dict) -> str:
        """
        Extract message body (text or HTML).
        
        Returns:
            Decoded message body
        """
        payload = message.get('payload', {})
        
        # Try to get body from parts
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/html':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif part['mimeType'] == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        # Try direct body
        data = payload.get('body', {}).get('data', '')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        return ""
    
    def add_label(self, message_id: str, label_name: str):
        """Add a label to a message."""
        try:
            # Get or create label
            labels = self.service.users().labels().list(userId='me').execute()
            label_id = None
            
            for label in labels.get('labels', []):
                if label['name'] == label_name:
                    label_id = label['id']
                    break
            
            if not label_id:
                # Create label
                label_object = {
                    'name': label_name,
                    'labelListVisibility': 'labelShow',
                    'messageListVisibility': 'show'
                }
                created_label = self.service.users().labels().create(
                    userId='me',
                    body=label_object
                ).execute()
                label_id = created_label['id']
            
            # Add label to message
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
        
        except Exception as e:
            print(f"✗ Error adding label: {e}")
    
    def send_email(self, to: str, subject: str, body: str):
        """
        Send an email (for mailto: unsubscribes).
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
        """
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            print(f"✓ Sent unsubscribe email to {to}")
        
        except Exception as e:
            print(f"✗ Error sending email to {to}: {e}")
