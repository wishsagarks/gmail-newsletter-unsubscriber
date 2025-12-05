"""Execute unsubscribe actions."""

import requests
from typing import Dict
from urllib.parse import urlparse, parse_qs
from config import HTTP_TIMEOUT, USER_AGENT


class UnsubscribeExecutor:
    """Executes unsubscribe actions."""
    
    def __init__(self, gmail_client):
        self.gmail_client = gmail_client
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
    
    def execute(self, sender_info: Dict) -> Dict:
        """
        Execute unsubscribe action for a sender.
        
        Args:
            sender_info: Dict with unsubscribe_type, url, email, etc.
        
        Returns:
            Dict with success status and message
        """
        unsub_type = sender_info.get('unsubscribe_type')
        url = sender_info.get('unsubscribe_url')
        
        if unsub_type == 'simple_link':
            return self._execute_http_unsubscribe(url)
        
        elif unsub_type == 'mailto_link':
            return self._execute_mailto_unsubscribe(url, sender_info)
        
        elif unsub_type == 'web_form':
            return {
                'success': False,
                'action': 'manual_review',
                'message': 'Requires login or web form - manual review needed'
            }
        
        else:
            return {
                'success': False,
                'action': 'skipped',
                'message': 'No valid unsubscribe mechanism found'
            }
    
    def _execute_http_unsubscribe(self, url: str) -> Dict:
        """Execute HTTP-based unsubscribe."""
        try:
            # Try GET first (most common)
            response = self.session.get(url, timeout=HTTP_TIMEOUT, allow_redirects=True)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'action': 'http_get',
                    'message': f'Successfully accessed unsubscribe link (HTTP {response.status_code})'
                }
            
            # Some sites require POST
            elif response.status_code == 405:  # Method Not Allowed
                response = self.session.post(url, timeout=HTTP_TIMEOUT, allow_redirects=True)
                if response.status_code == 200:
                    return {
                        'success': True,
                        'action': 'http_post',
                        'message': f'Successfully posted to unsubscribe link (HTTP {response.status_code})'
                    }
            
            return {
                'success': False,
                'action': 'http_failed',
                'message': f'HTTP request failed with status {response.status_code}'
            }
        
        except requests.Timeout:
            return {
                'success': False,
                'action': 'timeout',
                'message': 'Request timed out'
            }
        
        except Exception as e:
            return {
                'success': False,
                'action': 'error',
                'message': f'Error: {str(e)}'
            }
    
    def _execute_mailto_unsubscribe(self, mailto_url: str, sender_info: Dict) -> Dict:
        """Execute mailto-based unsubscribe."""
        try:
            # Parse mailto URL
            # Format: mailto:unsub@example.com?subject=unsubscribe&body=...
            if not mailto_url.startswith('mailto:'):
                return {
                    'success': False,
                    'action': 'invalid_mailto',
                    'message': 'Invalid mailto URL'
                }
            
            # Extract email and parameters
            mailto_url = mailto_url[7:]  # Remove 'mailto:'
            parts = mailto_url.split('?')
            to_email = parts[0]
            
            subject = 'Unsubscribe'
            body = 'Please unsubscribe me from this mailing list.'
            
            if len(parts) > 1:
                params = parse_qs(parts[1])
                subject = params.get('subject', [subject])[0]
                body = params.get('body', [body])[0]
            
            # Send unsubscribe email via Gmail API
            self.gmail_client.send_email(to_email, subject, body)
            
            return {
                'success': True,
                'action': 'mailto_sent',
                'message': f'Sent unsubscribe email to {to_email}'
            }
        
        except Exception as e:
            return {
                'success': False,
                'action': 'mailto_failed',
                'message': f'Failed to send email: {str(e)}'
            }
