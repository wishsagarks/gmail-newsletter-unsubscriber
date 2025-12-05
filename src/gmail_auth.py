"""Gmail OAuth authentication handler."""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import SCOPES, CREDENTIALS_FILE, TOKEN_FILE


class GmailAuthenticator:
    """Handles Gmail OAuth 2.0 authentication."""
    
    def __init__(self):
        self.creds = None
        self.service = None
    
    def authenticate(self, silent=False):
        """
        Authenticate with Gmail API using OAuth 2.0.
        
        Args:
            silent: If True, skip all terminal prompts (for Streamlit/GUI mode)
        
        Returns:
            Google API service object for Gmail
        """
        # Check if token.json exists with valid credentials
        if os.path.exists(TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        # If credentials are invalid or don't exist, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("Refreshing expired credentials...")
                self.creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"Missing {CREDENTIALS_FILE}. Please download OAuth credentials "
                        "from Google Cloud Console and save as credentials.json"
                    )
                
                # Only show terminal prompts if NOT in silent mode (CLI mode)
                if not silent:
                    print("\n" + "="*60)
                    print("GMAIL AUTHENTICATION REQUIRED")
                    print("="*60)
                    print("\nThis automation needs permission to access your Gmail.")
                    print("\nPermissions requested:")
                    print("  • Read emails (to detect newsletters)")
                    print("  • Modify labels (to mark processed emails)")
                    print("  • Send emails (optional, for mailto: unsubscribes)")
                    print("\nPrivacy guarantee:")
                    print("  • Email content is only processed in memory")
                    print("  • No email data is stored on disk")
                    print("  • Tokens stay on your local machine")
                    print("\nYour browser will open for Google OAuth consent...")
                    print("="*60 + "\n")
                    
                    input("Press Enter to continue...")
                
                # Create OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES
                )
                # Run local server for OAuth - browser opens automatically
                # No user interaction needed - just complete auth in browser
                self.creds = flow.run_local_server(port=0, open_browser=True)
            
            # Save credentials for future runs
            with open(TOKEN_FILE, 'w') as token:
                token.write(self.creds.to_json())
            
            # Only print if NOT in silent mode
            if not silent:
                print(f"✓ Credentials saved to {TOKEN_FILE}")
        
        # Build Gmail API service
        self.service = build('gmail', 'v1', credentials=self.creds)
        
        # Only print if NOT in silent mode
        if not silent:
            print("✓ Successfully authenticated with Gmail API\n")
        
        return self.service
    
    def get_service(self):
        """Get authenticated Gmail service (authenticate if needed)."""
        if not self.service:
            self.authenticate()
        return self.service
