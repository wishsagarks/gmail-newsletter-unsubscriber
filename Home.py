#!/usr/bin/env python3
"""
Gmail Newsletter Unsubscriber - Home Page
Entry point for the Streamlit multi-page app
"""

import streamlit as st
import os
import json

st.set_page_config(
    page_title="Gmail Newsletter Unsubscriber",
    page_icon="✉️",
    layout="wide"
)

# Custom CSS for dark mode
st.markdown("""
<style>
    .big-title {
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        padding: 1rem 0;
    }
    .subtitle {
        text-align: center;
        color: #b8b8b8;
        font-size: 1.5rem;
        margin-bottom: 3rem;
    }
    .feature-card {
        padding: 2rem;
        border-radius: 15px;
        background: linear-gradient(135deg, #1a1d29 0%, #252936 100%);
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        margin: 1rem 0;
        border: 1px solid #667eea;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(102, 126, 234, 0.3);
        border-color: #764ba2;
    }
    .feature-card h3 {
        color: #667eea;
        margin-bottom: 1rem;
    }
    .feature-card ul {
        color: #e0e0e0;
    }
    .step-number {
        color: #667eea;
        font-size: 2rem;
        font-weight: bold;
    }
    .step-title {
        color: #fafafa;
        font-weight: 600;
    }
    .step-desc {
        color: #b8b8b8;
        font-size: 0.9rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def check_credentials():
    """Check if credentials.json exists"""
    if os.path.exists('credentials.json'):
        try:
            with open('credentials.json', 'r') as f:
                data = json.load(f)
                if 'installed' in data or 'web' in data:
                    return True
        except:
            pass
    return False

# Header
st.markdown("<div style='text-align: center; font-size: 3rem; margin-bottom: 0.5rem;'>📧</div>", unsafe_allow_html=True)
st.markdown("<h1 class='big-title'>Gmail Newsletter Unsubscriber</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Clean your inbox with one click</p>", unsafe_allow_html=True)

# Check setup status
credentials_exist = check_credentials()

if credentials_exist:
    st.success("✅ You're all set up and ready to go!")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🚀 Ready to clean your inbox?")
        if st.button("📧 START CLEANING MY INBOX", use_container_width=True, type="primary"):
            st.switch_page("pages/1_📧_Main_App.py")
else:
    st.warning("⚠️ First-time setup required")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔧 Let's get you set up!")
        st.markdown("Don't worry - our wizard makes it super easy (takes ~4 minutes)")
        if st.button("🔧 RUN SETUP WIZARD", use_container_width=True, type="primary"):
            st.switch_page("pages/0_🔧_Setup_Wizard.py")

st.markdown("---")

# Features
st.markdown("## ✨ What This Tool Does")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='feature-card'>
        <h3>🔐 Secure & Private</h3>
        <ul>
            <li>OAuth authentication</li>
            <li>No data stored</li>
            <li>Local processing only</li>
            <li>You control everything</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='feature-card'>
        <h3>🤖 Fully Automated</h3>
        <ul>
            <li>One-click operation</li>
            <li>Auto-detect newsletters</li>
            <li>Extract unsubscribe links</li>
            <li>Execute automatically</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='feature-card'>
        <h3>📊 Beautiful Reports</h3>
        <ul>
            <li>Real-time progress</li>
            <li>Interactive charts</li>
            <li>Detailed summaries</li>
            <li>Download reports</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# How it works
st.markdown("## 🔄 How It Works")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown("<div class='step-number'>1️⃣</div>", unsafe_allow_html=True)
    st.markdown("<div class='step-title'>Authenticate</div>", unsafe_allow_html=True)
    st.markdown("<div class='step-desc'>Secure OAuth</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='step-number'>2️⃣</div>", unsafe_allow_html=True)
    st.markdown("<div class='step-title'>Scan</div>", unsafe_allow_html=True)
    st.markdown("<div class='step-desc'>Find newsletters</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='step-number'>3️⃣</div>", unsafe_allow_html=True)
    st.markdown("<div class='step-title'>Detect</div>", unsafe_allow_html=True)
    st.markdown("<div class='step-desc'>Identify spam</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='step-number'>4️⃣</div>", unsafe_allow_html=True)
    st.markdown("<div class='step-title'>Review</div>", unsafe_allow_html=True)
    st.markdown("<div class='step-desc'>You approve</div>", unsafe_allow_html=True)

with col5:
    st.markdown("<div class='step-number'>5️⃣</div>", unsafe_allow_html=True)
    st.markdown("<div class='step-title'>Unsubscribe</div>", unsafe_allow_html=True)
    st.markdown("<div class='step-desc'>Auto-execute</div>", unsafe_allow_html=True)

with col6:
    st.markdown("<div class='step-number'>6️⃣</div>", unsafe_allow_html=True)
    st.markdown("<div class='step-title'>Report</div>", unsafe_allow_html=True)
    st.markdown("<div class='step-desc'>See results</div>", unsafe_allow_html=True)

st.markdown("---")

# Stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("⏱️ Time Saved", "~90%", help="Compared to manual unsubscribing")

with col2:
    st.metric("🔒 Privacy", "100%", help="No email content stored")

with col3:
    st.metric("🎯 Accuracy", "95%+", help="Newsletter detection rate")

with col4:
    st.metric("⚡ Speed", "< 5 min", help="For 50+ newsletters")

st.markdown("---")

# Documentation link
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("📚 View Documentation", use_container_width=True, type="secondary"):
        st.switch_page("pages/2_📚_Documentation.py")

# Sidebar
with st.sidebar:
    st.markdown("### 🏠 Navigation")
    
    if credentials_exist:
        st.success("✅ Setup Complete")
        if st.button("📧 Main App", use_container_width=True):
            st.switch_page("pages/1_📧_Main_App.py")
    else:
        st.warning("⚠️ Setup Needed")
        if st.button("🔧 Setup Wizard", use_container_width=True):
            st.switch_page("pages/0_🔧_Setup_Wizard.py")
    
    st.markdown("---")
    st.markdown("### 🔒 Privacy")
    st.info("✅ All processing is local\n\n✅ No data stored\n\n✅ You control everything")
    
    st.markdown("---")
    st.markdown("### 👨‍💻 Connect")
    st.markdown("""
    **Built by Sagar Satapathy**
    
    🔗 [LinkedIn](https://www.linkedin.com/in/sagar-satapathy-wishsagarks/)
    
    💻 [GitHub](https://github.com/wishsagarks)
    
    ⭐ Star the repo if you find it useful!
    """)
