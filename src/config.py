"""Configuration for Gmail Newsletter Unsubscriber."""

# Gmail API Scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'  # Optional: for mailto unsubscribes
]

# Email scanning parameters
DAYS_TO_SCAN = 7
MAX_MESSAGES = 500
GMAIL_QUERY = "category:promotions OR category:updates OR unsubscribe"

# Newsletter detection
CONFIDENCE_THRESHOLD = 0.7
NEWSLETTER_KEYWORDS = [
    'unsubscribe',
    'manage preferences',
    'update your email preferences',
    'opt out',
    'stop receiving',
    'email preferences'
]

# Unsubscribe execution
AUTO_LABEL_PROCESSED = True
LABEL_NAME = "Unsubscribed"
HTTP_TIMEOUT = 10  # seconds
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# File paths
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
OUTPUT_DIR = "output"
SUMMARY_FILE = "output/unsubscribe_summary.md"

# Whitelist (senders to never unsubscribe from)
WHITELIST_DOMAINS = [
    # Add trusted domains here, e.g.:
    # "github.com",
    # "stackoverflow.com"
]
