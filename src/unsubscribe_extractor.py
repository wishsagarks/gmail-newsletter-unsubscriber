"""Extract unsubscribe links and mechanisms from emails."""

import re
from typing import Dict, Optional, List
from urllib.parse import urlparse
from bs4 import BeautifulSoup


class UnsubscribeExtractor:
    """Extracts unsubscribe mechanisms from email messages."""
    
    UNSUBSCRIBE_PATTERNS = [
        r'unsubscribe',
        r'opt[- ]?out',
        r'manage\s+preferences',
        r'email\s+preferences',
        r'update\s+preferences',
        r'stop\s+receiving'
    ]
    
    def extract(self, headers: Dict, body: str) -> Dict:
        """
        Extract unsubscribe mechanism from email.
        
        Args:
            headers: Email headers dict
            body: Email body (HTML or text)
        
        Returns:
            Dict with unsubscribe_type, url, confidence
        """
        # Priority 1: List-Unsubscribe header (RFC 2369)
        list_unsub = headers.get('list-unsubscribe', '')
        if list_unsub:
            result = self._parse_list_unsubscribe(list_unsub)
            if result:
                return result
        
        # Priority 2: HTML links in body
        if '<' in body and '>' in body:  # Likely HTML
            result = self._extract_from_html(body)
            if result:
                return result
        
        # Priority 3: Plain text URLs
        result = self._extract_from_text(body)
        if result:
            return result
        
        return {
            'unsubscribe_type': 'missing',
            'url': None,
            'confidence': 0.0
        }
    
    def _parse_list_unsubscribe(self, header_value: str) -> Optional[Dict]:
        """Parse List-Unsubscribe header."""
        # Format: <mailto:unsub@example.com>, <https://example.com/unsub>
        urls = re.findall(r'<([^>]+)>', header_value)
        
        for url in urls:
            if url.startswith('http://') or url.startswith('https://'):
                return {
                    'unsubscribe_type': 'simple_link',
                    'url': url,
                    'confidence': 0.95
                }
            elif url.startswith('mailto:'):
                return {
                    'unsubscribe_type': 'mailto_link',
                    'url': url,
                    'confidence': 0.90
                }
        
        return None
    
    def _extract_from_html(self, body: str) -> Optional[Dict]:
        """Extract unsubscribe link from HTML body."""
        try:
            soup = BeautifulSoup(body, 'html.parser')
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text().lower().strip()
                
                # Check if link text matches unsubscribe patterns
                for pattern in self.UNSUBSCRIBE_PATTERNS:
                    if re.search(pattern, text, re.IGNORECASE):
                        if href.startswith('http://') or href.startswith('https://'):
                            # Check if it's a simple link or requires login
                            unsub_type = self._classify_link(href, text)
                            return {
                                'unsubscribe_type': unsub_type,
                                'url': href,
                                'confidence': 0.85
                            }
                        elif href.startswith('mailto:'):
                            return {
                                'unsubscribe_type': 'mailto_link',
                                'url': href,
                                'confidence': 0.80
                            }
        
        except Exception as e:
            print(f"  Warning: Error parsing HTML: {e}")
        
        return None
    
    def _extract_from_text(self, body: str) -> Optional[Dict]:
        """Extract unsubscribe URL from plain text."""
        # Look for URLs near unsubscribe keywords
        lines = body.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if line contains unsubscribe keyword
            if any(re.search(pattern, line_lower) for pattern in self.UNSUBSCRIBE_PATTERNS):
                # Look for URL in this line or next few lines
                search_lines = lines[i:min(i+3, len(lines))]
                for search_line in search_lines:
                    urls = re.findall(r'https?://[^\s<>"]+', search_line)
                    if urls:
                        return {
                            'unsubscribe_type': 'simple_link',
                            'url': urls[0],
                            'confidence': 0.70
                        }
        
        return None
    
    def _classify_link(self, url: str, link_text: str) -> str:
        """
        Classify unsubscribe link type.
        
        Returns:
            'simple_link' or 'web_form'
        """
        url_lower = url.lower()
        text_lower = link_text.lower()
        
        # Indicators of web form / login required
        form_indicators = [
            'login',
            'signin',
            'account',
            'settings',
            'preferences',
            'manage'
        ]
        
        # Check URL path
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        if any(indicator in path for indicator in form_indicators):
            if 'unsubscribe' not in path:
                return 'web_form'
        
        # Check link text
        if any(indicator in text_lower for indicator in ['manage', 'preferences', 'settings']):
            if 'unsubscribe' not in text_lower:
                return 'web_form'
        
        return 'simple_link'
