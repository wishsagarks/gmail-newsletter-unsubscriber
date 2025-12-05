#!/usr/bin/env python3
"""
Gmail Newsletter Unsubscriber - Documentation
Beautiful documentation viewer
"""

import streamlit as st
import os

st.set_page_config(
    page_title="Documentation - Gmail Unsubscriber",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .doc-title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .doc-card {
        padding: 2rem;
        border-radius: 15px;
        background: linear-gradient(135deg, #1a1d29 0%, #252936 100%);
        border: 1px solid #667eea;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    .doc-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
    }
    .doc-section {
        color: #667eea;
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .doc-content {
        color: #e0e0e0;
        line-height: 1.8;
    }
    .doc-content h1, .doc-content h2, .doc-content h3 {
        color: #fafafa;
        margin-top: 1.5rem;
    }
    .doc-content code {
        background: #1a1d29;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        color: #667eea;
    }
    .doc-content pre {
        background: #1a1d29;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #667eea;
    }
    .doc-content ul, .doc-content ol {
        color: #e0e0e0;
    }
    .doc-content a {
        color: #667eea;
        text-decoration: none;
    }
    .doc-content a:hover {
        color: #764ba2;
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div style='text-align: center; font-size: 2.5rem; margin-bottom: 0.5rem;'>📚</div>", unsafe_allow_html=True)
st.markdown("<h1 class='doc-title'>Documentation</h1>", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("Home.py")
    
    st.markdown("---")
    st.markdown("### 📖 Quick Links")
    
    doc_section = st.radio(
        "Navigate to:",
        [
            "🚀 Quick Start",
            "🔧 Setup Guide",
            "📱 Streamlit UI",
            "🔒 Privacy Policy",
            "🏗️ How It Works",
            "🤝 Contributing",
            "❓ Troubleshooting"
        ],
        label_visibility="collapsed"
    )

# Main content area
if doc_section == "🚀 Quick Start":
    st.markdown("<div class='doc-section'>🚀 Quick Start Guide</div>", unsafe_allow_html=True)
    
    if os.path.exists('QUICK_START.md'):
        with open('QUICK_START.md', 'r') as f:
            content = f.read()
        st.markdown(f"<div class='doc-content'>{content}</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='doc-card'>
            <h2>⚡ The Absolute Easiest Way</h2>
            <h3>One Command:</h3>
            <pre><code>./start.sh</code></pre>
            
            <h3>What Happens:</h3>
            <ul>
                <li>✅ Checks if you're set up</li>
                <li>✅ Runs setup wizard if needed (first time only)</li>
                <li>✅ Launches the main app</li>
                <li>✅ Handles everything automatically</li>
            </ul>
            
            <h3>First Time (Setup):</h3>
            <ol>
                <li>Run: <code>./start.sh</code></li>
                <li>Setup wizard opens in browser</li>
                <li>Follow 5 easy steps (~4 minutes)</li>
                <li>Done! Main app launches</li>
            </ol>
            
            <h3>Every Time After:</h3>
            <ol>
                <li>Run: <code>./start.sh</code></li>
                <li>Main app opens immediately</li>
                <li>Click "START CLEANING MY INBOX"</li>
                <li>Relax and watch it work!</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

elif doc_section == "🔧 Setup Guide":
    st.markdown("<div class='doc-section'>🔧 Setup Guide</div>", unsafe_allow_html=True)
    
    if os.path.exists('SETUP_GUIDE.md'):
        with open('SETUP_GUIDE.md', 'r') as f:
            content = f.read()
        st.markdown(f"<div class='doc-content'>{content}</div>", unsafe_allow_html=True)
    else:
        st.info("Setup guide not found. Use the Setup Wizard in the app!")

elif doc_section == "📱 Streamlit UI":
    st.markdown("<div class='doc-section'>📱 Streamlit UI Guide</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='doc-card'>
        <h2>🎨 Beautiful One-Click Interface</h2>
        
        <h3>Features:</h3>
        <ul>
            <li>✨ One-click automation</li>
            <li>📊 Real-time progress tracking</li>
            <li>🤖 Auto-approve mode</li>
            <li>📈 Interactive charts</li>
            <li>💾 Download reports</li>
        </ul>
        
        <h3>Settings (Sidebar):</h3>
        <ul>
            <li><strong>Auto-approve:</strong> Skip manual review</li>
            <li><strong>Days to scan:</strong> 1-30 days (default: 7)</li>
            <li><strong>Max messages:</strong> 100-2000 (default: 500)</li>
            <li><strong>Confidence threshold:</strong> Detection sensitivity</li>
            <li><strong>Skip unsubscribed:</strong> Filter out history</li>
            <li><strong>Delete after unsub:</strong> Move to trash</li>
        </ul>
        
        <h3>The 6-Stage Process:</h3>
        <ol>
            <li><strong>🔐 Authentication:</strong> Secure OAuth login</li>
            <li><strong>📥 Scanning:</strong> Fetch recent emails</li>
            <li><strong>🔍 Detection:</strong> Identify newsletters</li>
            <li><strong>✅ Review:</strong> Approve senders</li>
            <li><strong>🚀 Execution:</strong> Unsubscribe automatically</li>
            <li><strong>📊 Summary:</strong> Beautiful charts & reports</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

elif doc_section == "🔒 Privacy Policy":
    st.markdown("<div class='doc-section'>🔒 Privacy Policy</div>", unsafe_allow_html=True)
    
    if os.path.exists('PRIVACY.md'):
        with open('PRIVACY.md', 'r') as f:
            content = f.read()
        st.markdown(f"<div class='doc-content'>{content}</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='doc-card'>
            <h2>🔒 Our Privacy Commitment</h2>
            
            <h3>What We Access:</h3>
            <ul>
                <li>Email headers (From, Subject, List-Unsubscribe)</li>
                <li>First 500 characters of body (for detection)</li>
                <li>Gmail labels and categories</li>
            </ul>
            
            <h3>What We DO NOT Do:</h3>
            <ul>
                <li>❌ Store full email content</li>
                <li>❌ Send data to external servers</li>
                <li>❌ Log sensitive information</li>
                <li>❌ Share with third parties</li>
            </ul>
            
            <h3>What Gets Stored:</h3>
            <ul>
                <li><strong>OAuth tokens:</strong> Local only (token.json)</li>
                <li><strong>Unsubscribe history:</strong> Just email addresses</li>
                <li><strong>Summary reports:</strong> Sender info only</li>
            </ul>
            
            <h3>Your Control:</h3>
            <ul>
                <li>✅ Review before any action</li>
                <li>✅ Revoke access anytime</li>
                <li>✅ Delete history anytime</li>
                <li>✅ Inspect all code (open source)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif doc_section == "🏗️ How It Works":
    st.markdown("<div class='doc-section'>🏗️ How It Works</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='doc-card'>
        <h2>🧠 Newsletter Detection Algorithm</h2>
        
        <h3>Scoring System (0-100%):</h3>
        <ul>
            <li><strong>40%:</strong> List-Unsubscribe header (RFC 2369)</li>
            <li><strong>20%:</strong> Gmail category labels</li>
            <li><strong>20%:</strong> Unsubscribe keywords in body</li>
            <li><strong>10%:</strong> Newsletter keywords in subject</li>
            <li><strong>10%:</strong> Bulk sender patterns</li>
        </ul>
        
        <h3>Example Detection:</h3>
        <pre><code>Email has List-Unsubscribe header: +40%
Gmail labeled CATEGORY_PROMOTIONS: +20%
Body contains "unsubscribe": +20%
Total: 80% confidence ✅ Newsletter!</code></pre>
        
        <h3>Unsubscribe Methods:</h3>
        <ol>
            <li><strong>Simple Link:</strong> HTTP GET/POST to URL</li>
            <li><strong>Mailto Link:</strong> Send unsubscribe email</li>
            <li><strong>Web Form:</strong> Manual review needed</li>
        </ol>
        
        <h3>Smart Features:</h3>
        <ul>
            <li>Groups by sender (not individual emails)</li>
            <li>Tracks unsubscribe history</li>
            <li>Filters out already processed</li>
            <li>Optional: Delete emails after unsub</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

elif doc_section == "🤝 Contributing":
    st.markdown("<div class='doc-section'>🤝 Contributing</div>", unsafe_allow_html=True)
    
    if os.path.exists('CONTRIBUTING.md'):
        with open('CONTRIBUTING.md', 'r') as f:
            content = f.read()
        st.markdown(f"<div class='doc-content'>{content}</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='doc-card'>
            <h2>🤝 How to Contribute</h2>
            
            <h3>Ways to Help:</h3>
            <ul>
                <li>🐛 Report bugs</li>
                <li>💡 Suggest features</li>
                <li>📝 Improve documentation</li>
                <li>🔧 Submit pull requests</li>
                <li>⭐ Star the project</li>
            </ul>
            
            <h3>Development Setup:</h3>
            <pre><code>git clone &lt;repo&gt;
cd gmail-newsletter-unsubscriber
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt</code></pre>
            
            <h3>Code Style:</h3>
            <ul>
                <li>Follow PEP 8</li>
                <li>Add docstrings</li>
                <li>Write tests</li>
                <li>Keep it simple</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif doc_section == "❓ Troubleshooting":
    st.markdown("<div class='doc-section'>❓ Troubleshooting</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='doc-card'>
        <h2>🔧 Common Issues & Solutions</h2>
        
        <h3>1. "Access blocked" OAuth Error</h3>
        <p><strong>Problem:</strong> App hasn't completed Google verification</p>
        <p><strong>Solution:</strong></p>
        <ol>
            <li>Go to <a href="https://console.cloud.google.com/apis/credentials/consent" target="_blank">OAuth Consent Screen</a></li>
            <li>Scroll to "Test users"</li>
            <li>Click "+ ADD USERS"</li>
            <li>Add your Gmail address</li>
            <li>Delete token.json and try again</li>
        </ol>
        
        <h3>2. "Missing credentials.json"</h3>
        <p><strong>Problem:</strong> OAuth credentials not set up</p>
        <p><strong>Solution:</strong></p>
        <ul>
            <li>Run the Setup Wizard</li>
            <li>Or follow SETUP_GUIDE.md</li>
            <li>Download credentials from Google Cloud Console</li>
        </ul>
        
        <h3>3. No Newsletters Detected</h3>
        <p><strong>Solutions:</strong></p>
        <ul>
            <li>Increase "Days to scan" (sidebar)</li>
            <li>Lower "Confidence threshold"</li>
            <li>Check you have promotional emails</li>
            <li>Disable "Skip already unsubscribed"</li>
        </ul>
        
        <h3>4. Import Errors</h3>
        <p><strong>Solution:</strong></p>
        <pre><code>source venv/bin/activate
pip install -r requirements.txt</code></pre>
        
        <h3>5. History Not Working</h3>
        <p><strong>Solutions:</strong></p>
        <ul>
            <li>Check "Skip already unsubscribed" is enabled</li>
            <li>View history in sidebar</li>
            <li>Clear history if needed</li>
            <li>Restart the app</li>
        </ul>
        
        <h3>6. Setup Wizard Issues</h3>
        <p><strong>Solutions:</strong></p>
        <ul>
            <li>Use "Start Setup From Beginning" to reset</li>
            <li>Make sure you're signed into Google</li>
            <li>Check project is selected in Cloud Console</li>
            <li>Wait a few seconds after each step</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='text-align: center; color: #b8b8b8;'>
        <p>Built for Kiro Heroes Week 2</p>
        <p>Theme: Lazy Automation</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: center; color: #b8b8b8;'>
        <p>🔒 Privacy-First Design</p>
        <p>✅ Open Source</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='text-align: center; color: #b8b8b8;'>
        <p>📧 Clean Your Inbox</p>
        <p>⚡ Save Time</p>
    </div>
    """, unsafe_allow_html=True)
