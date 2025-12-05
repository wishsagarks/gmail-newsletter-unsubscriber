"""Newsletter detection logic."""

import re
from typing import Dict, Tuple
from config import NEWSLETTER_KEYWORDS, CONFIDENCE_THRESHOLD


class NewsletterDetector:
    """Detects if an email is a newsletter/promotional message."""
    
    def __init__(self):
        self.keywords = NEWSLETTER_KEYWORDS
    
    def is_newsletter(self, message: Dict, headers: Dict, body_snippet: str) -> Tuple[bool, float]:
        """
        Determine if a message is a newsletter.
        
        Args:
            message: Gmail message object
            headers: Parsed headers dict
            body_snippet: Small snippet of body text
        
        Returns:
            (is_newsletter, confidence_score)
        """
        score = 0.0
        max_score = 0.0
        
        # Check for List-Unsubscribe header (strong signal)
        max_score += 0.4
        if headers.get('list-unsubscribe'):
            score += 0.4
        
        # Check Gmail labels
        max_score += 0.2
        labels = message.get('labelIds', [])
        if 'CATEGORY_PROMOTIONS' in labels or 'CATEGORY_UPDATES' in labels:
            score += 0.2
        
        # Check for unsubscribe keywords in subject
        max_score += 0.1
        subject = headers.get('subject', '').lower()
        if any(keyword in subject for keyword in ['newsletter', 'digest', 'weekly', 'update']):
            score += 0.1
        
        # Check for unsubscribe keywords in body snippet
        max_score += 0.2
        body_lower = body_snippet.lower()
        keyword_matches = sum(1 for keyword in self.keywords if keyword in body_lower)
        if keyword_matches > 0:
            score += min(0.2, keyword_matches * 0.05)
        
        # Check for bulk sender patterns
        max_score += 0.1
        from_header = headers.get('from', '').lower()
        bulk_patterns = ['no-reply', 'noreply', 'newsletter', 'marketing', 'promo']
        if any(pattern in from_header for pattern in bulk_patterns):
            score += 0.1
        
        # Normalize score
        confidence = score / max_score if max_score > 0 else 0.0
        is_newsletter = confidence >= CONFIDENCE_THRESHOLD
        
        return is_newsletter, confidence
    
    def extract_sender_info(self, from_header: str) -> Dict[str, str]:
        """
        Parse sender information from From header.
        
        Args:
            from_header: Email From header value
        
        Returns:
            Dict with display_name, email, domain
        """
        # Pattern: "Display Name <email@domain.com>" or just "email@domain.com"
        match = re.match(r'^(?:"?([^"<]+)"?\s*)?<?([^>]+@[^>]+)>?$', from_header)
        
        if match:
            display_name = (match.group(1) or '').strip()
            email = match.group(2).strip()
            domain = email.split('@')[-1] if '@' in email else ''
            
            return {
                'display_name': display_name or email,
                'email': email,
                'domain': domain
            }
        
        return {
            'display_name': from_header,
            'email': from_header,
            'domain': ''
        }
