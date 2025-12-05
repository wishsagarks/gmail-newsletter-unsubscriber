#!/usr/bin/env python3
"""
Gmail Newsletter Unsubscriber - Streamlit UI
One-click automation with beautiful progress tracking
"""

import streamlit as st
import time
import os
import sys
from datetime import datetime
from collections import defaultdict
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.gmail_auth import GmailAuthenticator
from src.gmail_client import GmailClient
from src.newsletter_detector import NewsletterDetector
from src.unsubscribe_extractor import UnsubscribeExtractor
from src.unsubscribe_executor import UnsubscribeExecutor
from src.report_generator import ReportGenerator
from src.config import AUTO_LABEL_PROCESSED, LABEL_NAME, DAYS_TO_SCAN, MAX_MESSAGES
from src.automation_scheduler import AutomationScheduler
from src.automation_ui import render_automation_reminder, render_automation_settings, render_automation_stats, render_first_run_setup

# Page config
st.set_page_config(
    page_title="Gmail Newsletter Unsubscriber",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark mode
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #b8b8b8;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .process-card {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        background: linear-gradient(135deg, #1a1d29 0%, #252936 100%);
        border: 1px solid #667eea;
    }
    .success-card {
        background: linear-gradient(135deg, #1a3a1a 0%, #2d4a2d 100%);
        border-left-color: #28a745;
        border-color: #28a745;
    }
    .warning-card {
        background: linear-gradient(135deg, #3a3a1a 0%, #4a4a2d 100%);
        border-left-color: #ffc107;
        border-color: #ffc107;
    }
    .info-card {
        background: linear-gradient(135deg, #1a2a3a 0%, #2d3a4a 100%);
        border-left-color: #17a2b8;
        border-color: #17a2b8;
    }
    .process-card h3 {
        color: #fafafa;
    }
    .process-card p, .process-card ul, .process-card li {
        color: #e0e0e0;
    }
    .sender-card {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        background: linear-gradient(135deg, #1a1d29 0%, #252936 100%);
        border: 1px solid #667eea;
        transition: all 0.3s;
    }
    .sender-card:hover {
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
        transform: translateY(-2px);
        border-color: #764ba2;
    }
    .metric-card {
        text-align: center;
        padding: 1rem;
        border-radius: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        color: white;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'process_stage' not in st.session_state:
    st.session_state.process_stage = 0
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'senders_list' not in st.session_state:
    st.session_state.senders_list = []
if 'selected_senders' not in st.session_state:
    st.session_state.selected_senders = {}
if 'execution_results' not in st.session_state:
    st.session_state.execution_results = []
if 'auto_mode' not in st.session_state:
    st.session_state.auto_mode = False
if 'gmail_service' not in st.session_state:
    st.session_state.gmail_service = None
if 'scheduler' not in st.session_state:
    st.session_state.scheduler = AutomationScheduler()

# Load unsubscribed senders history
def load_unsubscribed_history():
    """Load list of previously unsubscribed sender emails"""
    history_file = 'output/unsubscribed_history.txt'
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_unsubscribed_sender(email):
    """Save a sender email to the unsubscribed history"""
    history_file = 'output/unsubscribed_history.txt'
    os.makedirs('output', exist_ok=True)
    with open(history_file, 'a') as f:
        f.write(f"{email}\n")

def show_progress_bar(stage, total_stages=6):
    """Show beautiful progress bar"""
    progress = stage / total_stages
    
    stages = [
        "🔐 Authentication",
        "📥 Scanning Emails", 
        "🔍 Detecting Newsletters",
        "✅ Review & Approve",
        "🚀 Unsubscribing",
        "📊 Summary Report"
    ]
    
    # Progress bar
    st.progress(progress)
    
    # Stage indicators
    cols = st.columns(total_stages)
    for i, col in enumerate(cols):
        with col:
            if i < stage:
                st.markdown(f"✅ **{stages[i].split()[1]}**")
            elif i == stage:
                st.markdown(f"⏳ **{stages[i].split()[1]}**")
            else:
                st.markdown(f"⚪ {stages[i].split()[1]}")

def authenticate_gmail():
    """Handle Gmail authentication"""
    try:
        # Check if credentials exist
        if not os.path.exists('credentials.json'):
            st.error("❌ Missing credentials.json file!")
            st.warning("""
            **Setup Required:** You need to configure Google Cloud credentials first.
            
            Don't worry - we have an easy setup wizard that will guide you through every step!
            """)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔧 Run Setup Wizard", use_container_width=True, type="primary"):
                    st.info("Please run: `./run_setup.sh` or `streamlit run setup_wizard.py`")
                    st.code("./run_setup.sh", language="bash")
            
            with st.expander("📖 Manual Setup Instructions"):
                st.markdown("""
                1. Go to [Google Cloud Console](https://console.cloud.google.com/)
                2. Enable Gmail API
                3. Create OAuth 2.0 credentials (Desktop app)
                4. Download and save as `credentials.json`
                
                See SETUP_GUIDE.md for detailed instructions.
                """)
            return None
        
        # Check if already authenticated (token exists and valid)
        if os.path.exists('token.json'):
            try:
                with st.spinner("🔐 Verifying existing credentials..."):
                    authenticator = GmailAuthenticator()
                    service = authenticator.authenticate(silent=True)
                    st.session_state.authenticated = True
                    st.session_state.gmail_service = service
                    st.success("✅ Authentication successful!")
                    return service
            except Exception as e:
                # Token invalid, need to re-authenticate
                st.warning("⚠️ Existing credentials expired, re-authenticating...")
                if os.path.exists('token.json'):
                    os.remove('token.json')
        
        # Need new authentication
        st.info("""
        ### 🔐 Gmail Authentication Required
        
        **What happens next:**
        1. Click the button below
        2. Your browser will open automatically
        3. Sign in with your Google account
        4. Grant permissions to the app
        5. Return here - the app will continue automatically!
        
        **Privacy guarantee:**
        - ✅ All processing happens locally
        - ✅ No email content stored
        - ✅ Tokens stay on your machine
        """)
        
        if st.button("🚀 Open Google Sign-In", use_container_width=True, type="primary"):
            with st.spinner("🌐 Opening browser for authentication..."):
                # Show instructions while authenticating
                status_placeholder = st.empty()
                status_placeholder.info("""
                **Browser opened!** 
                
                👉 Complete the sign-in in your browser
                
                ⏳ Waiting for you to complete authentication...
                
                *This page will automatically continue once you're done!*
                """)
                
                try:
                    authenticator = GmailAuthenticator()
                    service = authenticator.authenticate(silent=True)  # Silent mode - no terminal prompts!
                    st.session_state.authenticated = True
                    st.session_state.gmail_service = service
                    status_placeholder.empty()
                    st.success("✅ Authentication successful! Continuing...")
                    time.sleep(1)
                    return service
                except Exception as auth_error:
                    status_placeholder.empty()
                    raise auth_error
        
        return None
    
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ Authentication failed: {error_msg}")
        
        # Check for common OAuth errors
        if "access_denied" in error_msg.lower() or "not completed the google verification" in error_msg.lower():
            st.warning("### 🔧 Quick Fix Needed!")
            st.markdown("""
            **Error:** Your app is in Testing mode and you need to add yourself as a test user.
            
            **Fix in 2 minutes:**
            1. Go to [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
            2. Scroll to "Test users" section
            3. Click "+ ADD USERS"
            4. Enter your Gmail address
            5. Click "SAVE"
            6. Come back here and try again
            
            See [FIX_OAUTH_ERROR.md](FIX_OAUTH_ERROR.md) for detailed instructions.
            """)
            
            if st.button("🔄 Try Authentication Again"):
                # Clear token and retry
                if os.path.exists('token.json'):
                    os.remove('token.json')
                st.rerun()
        
        return None

def scan_emails(service, days=DAYS_TO_SCAN, max_msgs=MAX_MESSAGES):
    """Scan emails for newsletters"""
    try:
        gmail_client = GmailClient(service)
        
        with st.spinner(f"📥 Scanning last {days} days for newsletters (max {max_msgs} messages)..."):
            messages = gmail_client.fetch_recent_messages(days=days, max_results=max_msgs)
            st.session_state.messages = messages
            
            if not messages:
                st.warning("No messages found matching criteria.")
                return []
            
            st.success(f"✅ Found {len(messages)} messages to analyze")
            return messages
    
    except Exception as e:
        st.error(f"❌ Error scanning emails: {e}")
        return []

def detect_newsletters(service, messages):
    """Detect newsletters and extract unsubscribe info"""
    try:
        gmail_client = GmailClient(service)
        detector = NewsletterDetector()
        extractor = UnsubscribeExtractor()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        senders_map = defaultdict(lambda: {
            'messages': [],
            'message_ids': [],
            'subjects': []
        })
        
        total = len(messages)
        for i, msg in enumerate(messages):
            progress = (i + 1) / total
            progress_bar.progress(progress)
            status_text.text(f"🔍 Analyzing message {i+1}/{total}...")
            
            message = gmail_client.get_message_details(msg['id'])
            if not message:
                continue
            
            # Extract headers
            from_header = gmail_client.get_header(message, 'From') or ''
            subject = gmail_client.get_header(message, 'Subject') or '(no subject)'
            list_unsub = gmail_client.get_header(message, 'List-Unsubscribe') or ''
            
            headers = {
                'from': from_header,
                'subject': subject,
                'list-unsubscribe': list_unsub
            }
            
            # Get body snippet
            body = gmail_client.get_body(message)
            body_snippet = body[:500] if body else ''
            
            # Detect if newsletter
            is_newsletter, confidence = detector.is_newsletter(message, headers, body_snippet)
            
            if is_newsletter:
                sender_info = detector.extract_sender_info(from_header)
                sender_key = sender_info['email']
                
                senders_map[sender_key]['sender_info'] = sender_info
                senders_map[sender_key]['messages'].append(message)
                senders_map[sender_key]['message_ids'].append(msg['id'])
                senders_map[sender_key]['subjects'].append(subject)
                senders_map[sender_key]['confidence'] = max(
                    senders_map[sender_key].get('confidence', 0),
                    confidence
                )
                
                if 'unsubscribe_info' not in senders_map[sender_key]:
                    unsub_info = extractor.extract(headers, body)
                    senders_map[sender_key]['unsubscribe_info'] = unsub_info
        
        progress_bar.progress(1.0)
        status_text.text(f"✅ Analysis complete!")
        
        # Prepare sender list
        senders_list = []
        for email, data in senders_map.items():
            sender_info = data['sender_info']
            unsub_info = data['unsubscribe_info']
            
            senders_list.append({
                'email': email,
                'display_name': sender_info['display_name'],
                'domain': sender_info['domain'],
                'messages_count': len(data['messages']),
                'message_ids': data['message_ids'],
                'sample_subject': data['subjects'][0] if data['subjects'] else '',
                'unsubscribe_type': unsub_info['unsubscribe_type'],
                'unsubscribe_url': unsub_info.get('url'),
                'confidence': data['confidence']
            })
        
        senders_list.sort(key=lambda x: x['messages_count'], reverse=True)
        
        st.success(f"✅ Found {len(senders_list)} unique newsletter senders")
        return senders_list
    
    except Exception as e:
        st.error(f"❌ Error detecting newsletters: {e}")
        return []

def execute_unsubscribes(service, approved_senders):
    """Execute unsubscribe actions"""
    try:
        gmail_client = GmailClient(service)
        executor = UnsubscribeExecutor(gmail_client)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()
        
        execution_results = []
        total = len(approved_senders)
        
        for i, sender in enumerate(approved_senders):
            progress = (i + 1) / total
            progress_bar.progress(progress)
            status_text.text(f"🚀 Unsubscribing {i+1}/{total}: {sender['display_name']}...")
            
            result = executor.execute(sender)
            execution_results.append({
                'sender': sender,
                'result': result
            })
            
            # Show result in real-time
            with results_container:
                if result['success']:
                    st.success(f"✅ {sender['display_name']}: {result['message']}")
                else:
                    st.warning(f"⚠️ {sender['display_name']}: {result['message']}")
            
            # Label processed messages and save to history
            if result['success']:
                # Save to unsubscribed history
                save_unsubscribed_sender(sender['email'])
                
                # Delete or label messages
                delete_after_unsub = st.session_state.get('delete_after_unsub', False)
                if delete_after_unsub:
                    # Move to trash
                    for msg_id in sender['message_ids']:
                        try:
                            gmail_client.service.users().messages().trash(
                                userId='me',
                                id=msg_id
                            ).execute()
                        except:
                            pass  # Continue even if one fails
                elif AUTO_LABEL_PROCESSED:
                    # Just label
                    for msg_id in sender['message_ids']:
                        gmail_client.add_label(msg_id, LABEL_NAME)
            
            time.sleep(0.5)  # Small delay to show progress
        
        progress_bar.progress(1.0)
        status_text.text("✅ All unsubscribe actions completed!")
        
        st.session_state.execution_results = execution_results
        return execution_results
    
    except Exception as e:
        st.error(f"❌ Error executing unsubscribes: {e}")
        return []

def show_summary(execution_results, total_scanned, senders_detected):
    """Show beautiful summary with charts"""
    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>📊 Unsubscribe Summary</h2>", unsafe_allow_html=True)
    
    # Calculate stats
    successful = [r for r in execution_results if r['result']['success']]
    failed = [r for r in execution_results if not r['result']['success']]
    manual_review = [r for r in execution_results if r['result'].get('action') == 'manual_review']
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📧 Messages Scanned", total_scanned)
    with col2:
        st.metric("📬 Newsletters Found", senders_detected)
    with col3:
        st.metric("✅ Unsubscribed", len(successful))
    with col4:
        st.metric("⚠️ Manual Review", len(manual_review))
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart of results
        fig = go.Figure(data=[go.Pie(
            labels=['Successful', 'Manual Review', 'Failed'],
            values=[len(successful), len(manual_review), len(failed) - len(manual_review)],
            marker=dict(colors=['#28a745', '#ffc107', '#dc3545']),
            hole=0.4
        )])
        fig.update_layout(
            title="Unsubscribe Results",
            height=300,
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bar chart of top senders
        if successful:
            top_senders = sorted(successful, key=lambda x: x['sender']['messages_count'], reverse=True)[:5]
            fig = go.Figure(data=[go.Bar(
                x=[s['sender']['display_name'][:20] for s in top_senders],
                y=[s['sender']['messages_count'] for s in top_senders],
                marker=dict(color='#667eea')
            )])
            fig.update_layout(
                title="Top Unsubscribed Senders (by email count)",
                xaxis_title="Sender",
                yaxis_title="Number of Emails",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Detailed results
    st.markdown("### 📋 Detailed Results")
    
    tab1, tab2, tab3 = st.tabs(["✅ Successful", "⚠️ Manual Review", "❌ Failed"])
    
    with tab1:
        if successful:
            for r in successful:
                sender = r['sender']
                result = r['result']
                with st.expander(f"✅ {sender['display_name']} ({sender['messages_count']} emails)"):
                    st.write(f"**Email:** {sender['email']}")
                    st.write(f"**Sample:** {sender['sample_subject'][:80]}...")
                    st.write(f"**Method:** {result['action']}")
                    st.write(f"**Status:** {result['message']}")
        else:
            st.info("No successful unsubscribes")
    
    with tab2:
        if manual_review:
            st.warning("These senders require manual action (login or web form):")
            for r in manual_review:
                sender = r['sender']
                with st.expander(f"⚠️ {sender['display_name']} ({sender['messages_count']} emails)"):
                    st.write(f"**Email:** {sender['email']}")
                    st.write(f"**URL:** {sender.get('unsubscribe_url', 'N/A')}")
                    st.write(f"**Action Required:** Visit the URL to unsubscribe manually")
        else:
            st.success("No manual review needed!")
    
    with tab3:
        failed_only = [r for r in failed if r['result'].get('action') != 'manual_review']
        if failed_only:
            for r in failed_only:
                sender = r['sender']
                result = r['result']
                with st.expander(f"❌ {sender['display_name']}"):
                    st.write(f"**Email:** {sender['email']}")
                    st.write(f"**Error:** {result['message']}")
        else:
            st.success("No failures!")
    
    # Download report
    st.markdown("---")
    if st.button("📥 Download Full Report", use_container_width=True):
        report_gen = ReportGenerator()
        stats = {
            'total_scanned': total_scanned,
            'senders_detected': senders_detected,
            'approved': len(execution_results),
            'skipped': 0,
            'kept': 0
        }
        report_path = report_gen.generate_summary(stats, execution_results)
        
        with open(report_path, 'r') as f:
            report_content = f.read()
        
        st.download_button(
            label="📄 Download Markdown Report",
            data=report_content,
            file_name=f"unsubscribe_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )

# Main App
def main():
    # Header
    st.markdown("<div style='text-align: center; font-size: 2.5rem; margin-bottom: 0.5rem;'>📧</div>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-header'>Gmail Newsletter Unsubscriber</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>One-click automation to clean up your inbox</p>", unsafe_allow_html=True)
    
    # Get scheduler
    scheduler = st.session_state.scheduler
    
    # Show automation reminder if due
    reminder_action = render_automation_reminder(scheduler)
    if reminder_action == "run_now":
        st.session_state.process_stage = 1
        st.rerun()
    
    # Sidebar
    with st.sidebar:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.switch_page("Home.py")
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        
        auto_approve = st.checkbox(
            "🤖 Auto-approve all newsletters",
            value=False,
            help="Automatically approve all detected newsletters for unsubscribe"
        )
        st.session_state.auto_mode = auto_approve
        
        st.markdown("---")
        st.markdown("#### 📅 Scan Settings")
        
        days_to_scan = st.slider(
            "Days to scan",
            min_value=1,
            max_value=30,
            value=7,
            step=1,
            help="How many days back to scan for newsletters"
        )
        st.session_state.days_to_scan = days_to_scan
        
        max_messages = st.slider(
            "Max messages",
            min_value=100,
            max_value=2000,
            value=500,
            step=100,
            help="Maximum number of messages to fetch"
        )
        st.session_state.max_messages = max_messages
        
        st.markdown("---")
        st.markdown("#### 🎯 Detection Settings")
        
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.5,
            max_value=1.0,
            value=0.7,
            step=0.05,
            help="Minimum confidence to classify as newsletter"
        )
        st.session_state.confidence_threshold = confidence_threshold
        
        skip_unsubscribed = st.checkbox(
            "Skip already unsubscribed",
            value=True,
            help="Don't show senders you've already unsubscribed from"
        )
        st.session_state.skip_unsubscribed = skip_unsubscribed
        
        delete_after_unsub = st.checkbox(
            "Delete emails after unsubscribe",
            value=False,
            help="Move unsubscribed emails to trash (can be recovered from Gmail trash)"
        )
        st.session_state.delete_after_unsub = delete_after_unsub
        
        # Automation settings
        render_automation_settings(scheduler)
        
        st.markdown("---")
        st.markdown("### 📊 Stats")
        if st.session_state.messages:
            st.metric("Messages Scanned", len(st.session_state.messages))
        if st.session_state.senders_list:
            st.metric("Newsletters Found", len(st.session_state.senders_list))
        
        st.markdown("---")
        st.markdown("### � Hisvtory")
        unsubscribed_history = load_unsubscribed_history()
        st.metric("Previously Unsubscribed", len(unsubscribed_history))
        
        if len(unsubscribed_history) > 0:
            with st.expander("View History"):
                for email in sorted(unsubscribed_history):
                    st.text(f"• {email}")
            
            if st.button("🗑️ Clear History", use_container_width=True):
                if os.path.exists('output/unsubscribed_history.txt'):
                    os.remove('output/unsubscribed_history.txt')
                    st.success("History cleared!")
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 🔒 Privacy")
        st.info("✅ All processing happens locally\n\n✅ No email content stored\n\n✅ You control everything")
        
        if st.button("🔄 Reset & Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Progress indicator
    if st.session_state.process_stage > 0:
        show_progress_bar(st.session_state.process_stage)
        st.markdown("---")
    
    # Stage 0: Start
    if st.session_state.process_stage == 0:
        # Show first-run setup info
        render_first_run_setup(scheduler)
        
        # Show automation stats if not first run
        if scheduler.get_last_run() is not None:
            render_automation_stats(scheduler)
            st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class='process-card info-card'>
                <h3>🚀 Ready to Clean Your Inbox?</h3>
                <p>This tool will:</p>
                <ul>
                    <li>🔐 Securely connect to your Gmail</li>
                    <li>📥 Scan for newsletter spam</li>
                    <li>🔍 Detect unsubscribe links</li>
                    <li>✅ Let you review (or auto-approve)</li>
                    <li>🚀 Unsubscribe automatically</li>
                    <li>📊 Show you a beautiful summary</li>
                </ul>
                <p><strong>Privacy guaranteed:</strong> No email content is stored!</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🎯 START CLEANING MY INBOX", key="start_btn", use_container_width=True):
                st.session_state.process_stage = 1
                st.rerun()
    
    # Stage 1: Authentication
    elif st.session_state.process_stage == 1:
        st.markdown("<div class='process-card'>", unsafe_allow_html=True)
        st.markdown("### 🔐 Step 1: Authentication")
        
        if not st.session_state.authenticated:
            service = authenticate_gmail()
            if service:
                st.success("✅ Authentication complete! Moving to next step...")
                st.session_state.process_stage = 2
                time.sleep(1.5)
                st.rerun()
        else:
            st.success("✅ Already authenticated!")
            st.session_state.process_stage = 2
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Stage 2: Scanning
    elif st.session_state.process_stage == 2:
        st.markdown("<div class='process-card'>", unsafe_allow_html=True)
        st.markdown("### 📥 Step 2: Scanning Emails")
        
        if not st.session_state.messages:
            # Get custom scan settings from sidebar
            days = st.session_state.get('days_to_scan', DAYS_TO_SCAN)
            max_msgs = st.session_state.get('max_messages', MAX_MESSAGES)
            messages = scan_emails(st.session_state.gmail_service, days, max_msgs)
            if messages:
                st.session_state.process_stage = 3
                time.sleep(1)
                st.rerun()
        else:
            st.success(f"✅ Already scanned {len(st.session_state.messages)} messages")
            st.session_state.process_stage = 3
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Stage 3: Detection
    elif st.session_state.process_stage == 3:
        st.markdown("<div class='process-card'>", unsafe_allow_html=True)
        st.markdown("### 🔍 Step 3: Detecting Newsletters")
        
        if not st.session_state.senders_list:
            senders = detect_newsletters(st.session_state.gmail_service, st.session_state.messages)
            if senders:
                # Filter out already unsubscribed if enabled
                skip_unsubscribed = st.session_state.get('skip_unsubscribed', True)
                if skip_unsubscribed:
                    unsubscribed_history = load_unsubscribed_history()
                    original_count = len(senders)
                    senders = [s for s in senders if s['email'] not in unsubscribed_history]
                    filtered_count = original_count - len(senders)
                    if filtered_count > 0:
                        st.info(f"ℹ️ Filtered out {filtered_count} sender(s) you've already unsubscribed from")
                
                # Update session state with filtered list
                st.session_state.senders_list = senders
                
                if len(senders) == 0:
                    st.success("🎉 No new newsletters found! You've already unsubscribed from everything.")
                    st.info("Click 'Reset & Start Over' to scan again or adjust settings.")
                else:
                    st.session_state.process_stage = 4
                    time.sleep(1)
                    st.rerun()
        else:
            st.success(f"✅ Already detected {len(st.session_state.senders_list)} newsletters")
            st.session_state.process_stage = 4
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Stage 4: Review & Approve
    elif st.session_state.process_stage == 4:
        st.markdown("<div class='process-card'>", unsafe_allow_html=True)
        st.markdown("### ✅ Step 4: Review & Approve")
        
        senders = st.session_state.senders_list
        
        if st.session_state.auto_mode:
            st.info("🤖 Auto-approve mode enabled - all newsletters will be unsubscribed")
            for sender in senders:
                st.session_state.selected_senders[sender['email']] = True
            
            if st.button("🚀 Proceed with Auto-Unsubscribe", use_container_width=True):
                st.session_state.process_stage = 5
                st.rerun()
        else:
            st.info(f"Found {len(senders)} newsletter senders. Review and select which ones to unsubscribe from:")
            
            # Select all / Deselect all
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Select All", use_container_width=True):
                    for sender in senders:
                        st.session_state.selected_senders[sender['email']] = True
                    st.rerun()
            with col2:
                if st.button("❌ Deselect All", use_container_width=True):
                    st.session_state.selected_senders = {}
                    st.rerun()
            
            st.markdown("---")
            
            # Show senders
            for sender in senders:
                email = sender['email']
                if email not in st.session_state.selected_senders:
                    st.session_state.selected_senders[email] = True  # Default to selected
                
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    selected = st.checkbox(
                        "Select",
                        value=st.session_state.selected_senders[email],
                        key=f"check_{email}",
                        label_visibility="collapsed"
                    )
                    st.session_state.selected_senders[email] = selected
                
                with col2:
                    with st.expander(f"{'✅' if selected else '⬜'} {sender['display_name']} ({sender['messages_count']} emails)"):
                        st.write(f"**Email:** {sender['email']}")
                        st.write(f"**Domain:** {sender['domain']}")
                        st.write(f"**Sample:** {sender['sample_subject'][:80]}...")
                        st.write(f"**Unsubscribe Type:** {sender['unsubscribe_type']}")
                        st.write(f"**Confidence:** {sender['confidence']*100:.0f}%")
                        if sender.get('unsubscribe_url'):
                            st.write(f"**URL:** {sender['unsubscribe_url'][:60]}...")
            
            st.markdown("---")
            
            selected_count = sum(1 for v in st.session_state.selected_senders.values() if v)
            
            if selected_count > 0:
                if st.button(f"🚀 Unsubscribe from {selected_count} sender(s)", use_container_width=True):
                    st.session_state.process_stage = 5
                    st.rerun()
            else:
                st.warning("Please select at least one sender to unsubscribe from")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Stage 5: Execution
    elif st.session_state.process_stage == 5:
        st.markdown("<div class='process-card'>", unsafe_allow_html=True)
        st.markdown("### 🚀 Step 5: Unsubscribing")
        
        # Get approved senders
        approved_senders = [
            s for s in st.session_state.senders_list
            if st.session_state.selected_senders.get(s['email'], False)
        ]
        
        if not st.session_state.execution_results:
            results = execute_unsubscribes(st.session_state.gmail_service, approved_senders)
            if results:
                st.session_state.process_stage = 6
                time.sleep(2)
                st.rerun()
        else:
            st.success("✅ Unsubscribe actions completed!")
            st.session_state.process_stage = 6
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Stage 6: Summary
    elif st.session_state.process_stage == 6:
        st.balloons()
        
        # Record this run in automation scheduler
        successful_count = sum(1 for r in st.session_state.execution_results if r['result']['success'])
        scheduler.record_run(successful_count)
        
        show_summary(
            st.session_state.execution_results,
            len(st.session_state.messages),
            len(st.session_state.senders_list)
        )
        
        # Show automation stats after completion
        st.markdown("---")
        render_automation_stats(scheduler)
        
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Start Another Cleanup", use_container_width=True):
                # Keep scheduler but reset other state
                saved_scheduler = st.session_state.scheduler
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state.scheduler = saved_scheduler
                st.rerun()

if __name__ == "__main__":
    main()
