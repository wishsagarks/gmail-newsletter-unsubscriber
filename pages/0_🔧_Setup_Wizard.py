#!/usr/bin/env python3
"""
Gmail Newsletter Unsubscriber - Setup Wizard
Interactive guide for non-technical users
"""

import streamlit as st
import webbrowser
import os
import json
import time
from pathlib import Path

st.set_page_config(
    page_title="Setup Wizard - Gmail Unsubscriber",
    page_icon="🔧",
    layout="wide"
)

# Custom CSS for dark mode
st.markdown("""
<style>
    .big-title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .step-card {
        padding: 2rem;
        border-radius: 15px;
        background: linear-gradient(135deg, #1a1d29 0%, #252936 100%);
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        margin: 1rem 0;
        border: 1px solid #667eea;
    }
    .step-card h2, .step-card h3 {
        color: #fafafa;
    }
    .step-card p, .step-card ul, .step-card li {
        color: #e0e0e0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #1a3a1a 0%, #2d4a2d 100%);
        border: 2px solid #28a745;
        margin: 1rem 0;
        color: #90ee90;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #3a3a1a 0%, #4a4a2d 100%);
        border: 2px solid #ffc107;
        margin: 1rem 0;
        color: #ffd700;
    }
    .info-box {
        padding: 1rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #1a2a3a 0%, #2d3a4a 100%);
        border: 2px solid #17a2b8;
        margin: 1rem 0;
        color: #87ceeb;
    }
    .code-box {
        background: #1a1d29;
        padding: 1rem;
        border-radius: 5px;
        font-family: monospace;
        margin: 0.5rem 0;
        color: #667eea;
        border-left: 3px solid #667eea;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'setup_step' not in st.session_state:
    st.session_state.setup_step = 0
if 'project_created' not in st.session_state:
    st.session_state.project_created = False
if 'api_enabled' not in st.session_state:
    st.session_state.api_enabled = False
if 'credentials_created' not in st.session_state:
    st.session_state.credentials_created = False
if 'test_user_added' not in st.session_state:
    st.session_state.test_user_added = False

def check_credentials_file():
    """Check if credentials.json exists and is valid"""
    if os.path.exists('credentials.json'):
        try:
            with open('credentials.json', 'r') as f:
                data = json.load(f)
                # Check if it has the required structure
                if 'installed' in data or 'web' in data:
                    return True, data
        except:
            pass
    return False, None

def show_progress():
    """Show setup progress"""
    steps = [
        ("🌐 Google Account", st.session_state.setup_step >= 1),
        ("📁 Create Project", st.session_state.project_created),
        ("🔌 Enable API", st.session_state.api_enabled),
        ("🔑 Get Credentials", st.session_state.credentials_created),
        ("👤 Add Test User", st.session_state.test_user_added),
        ("✅ Complete", st.session_state.setup_step >= 6)
    ]
    
    cols = st.columns(len(steps))
    for i, (col, (label, completed)) in enumerate(zip(cols, steps)):
        with col:
            if completed:
                st.markdown(f"### ✅")
                st.markdown(f"**{label}**")
            elif i == st.session_state.setup_step:
                st.markdown(f"### ⏳")
                st.markdown(f"**{label}**")
            else:
                st.markdown(f"### ⚪")
                st.markdown(f"{label}")
    
    st.markdown("---")

# Main UI
st.markdown("<div style='text-align: center; font-size: 2.5rem; margin-bottom: 0.5rem;'>🔧</div>", unsafe_allow_html=True)
st.markdown("<h1 class='big-title'>Setup Wizard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>Let's get you set up in 5 easy steps!</p>", unsafe_allow_html=True)
st.markdown("---")

# Check if already set up
creds_exist, creds_data = check_credentials_file()
token_exists = os.path.exists('token.json')

# If both credentials and token exist, user is fully set up
if creds_exist and token_exists and st.session_state.setup_step < 6:
    st.success("🎉 Setup Complete! You're ready to go!")
    st.info("✅ Credentials configured\n\n✅ Test user added (token exists)\n\n✅ Ready to clean your inbox!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Go to Main App", use_container_width=True, type="primary"):
            st.switch_page("pages/1_📧_Main_App.py")
    with col2:
        if st.button("🔄 Start Setup From Beginning", use_container_width=True):
            # Delete credentials and token files
            if os.path.exists('credentials.json'):
                os.remove('credentials.json')
            if os.path.exists('token.json'):
                os.remove('token.json')
            
            # Reset all state
            st.session_state.setup_step = 0
            st.session_state.project_created = False
            st.session_state.api_enabled = False
            st.session_state.credentials_created = False
            st.session_state.test_user_added = False
            st.success("✅ Credentials deleted. Starting fresh!")
            time.sleep(1)
            st.rerun()
    st.stop()

# If only credentials exist (no token), need to add test user
elif creds_exist and not token_exists and st.session_state.setup_step < 4:
    st.success("🎉 Credentials file detected!")
    st.warning("⚠️ **Important:** You still need to add yourself as a test user to prevent OAuth errors!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👤 Continue to Add Test User", use_container_width=True, type="primary"):
            st.session_state.credentials_created = True
            st.session_state.setup_step = 5
            st.rerun()
    with col2:
        if st.button("🔄 Start Setup From Beginning", use_container_width=True):
            # Delete credentials and token files
            if os.path.exists('credentials.json'):
                os.remove('credentials.json')
            if os.path.exists('token.json'):
                os.remove('token.json')
            
            # Reset all state
            st.session_state.setup_step = 0
            st.session_state.project_created = False
            st.session_state.api_enabled = False
            st.session_state.credentials_created = False
            st.session_state.test_user_added = False
            st.success("✅ Credentials deleted. Starting fresh!")
            time.sleep(1)
            st.rerun()
    st.stop()

show_progress()

# Step 0: Welcome
if st.session_state.setup_step == 0:
    st.markdown("""
    <div class='step-card'>
        <h2>👋 Welcome!</h2>
        <p style='font-size: 1.1rem;'>
            This wizard will help you set up Gmail access in just a few minutes.
        </p>
        <p><strong>What you'll need:</strong></p>
        <ul style='font-size: 1.1rem;'>
            <li>✅ A Google account (Gmail)</li>
            <li>✅ 5 minutes of your time</li>
            <li>✅ A web browser (already open!)</li>
        </ul>
        <p><strong>What we'll do:</strong></p>
        <ul style='font-size: 1.1rem;'>
            <li>🌐 Open Google Cloud Console for you</li>
            <li>📝 Guide you through each click</li>
            <li>✅ Verify each step is complete</li>
            <li>🎉 Get you ready to clean your inbox!</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    st.markdown("**🔒 Privacy Note:** You're setting up YOUR OWN credentials. No one else has access to your Gmail.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Let's Get Started!", use_container_width=True, type="primary"):
            st.session_state.setup_step = 1
            st.rerun()

# Step 1: Google Cloud Console Access
elif st.session_state.setup_step == 1:
    st.markdown("""
    <div class='step-card'>
        <h2>🌐 Step 1: Access Google Cloud Console</h2>
        <p style='font-size: 1.1rem;'>
            First, we need to open Google Cloud Console. This is where Google manages API access.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### What to do:")
    st.markdown("""
    1. Click the button below to open Google Cloud Console
    2. Sign in with your Google account (if not already signed in)
    3. Come back here and click "Next"
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🌐 Open Google Cloud Console", use_container_width=True, type="primary"):
            webbrowser.open("https://console.cloud.google.com/")
            st.success("✅ Opened in your browser!")
            time.sleep(1)
    
    with col2:
        if st.button("➡️ Next Step", use_container_width=True):
            st.session_state.setup_step = 2
            st.rerun()
    
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    st.markdown("**💡 Tip:** Keep this wizard open in one tab and Google Cloud Console in another.")
    st.markdown("</div>", unsafe_allow_html=True)

# Step 2: Create Project
elif st.session_state.setup_step == 2:
    st.markdown("""
    <div class='step-card'>
        <h2>📁 Step 2: Create a Project</h2>
        <p style='font-size: 1.1rem;'>
            Projects organize your Google Cloud resources. Let's create one for this app.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### What to do:")
    
    with st.expander("📖 Detailed Instructions (Click to expand)", expanded=True):
        st.markdown("""
        1. **Click the button below** to open the New Project page
        2. In the "Project name" field, type: `Gmail Unsubscriber`
        3. Click the blue **"CREATE"** button
        4. Wait a few seconds for the project to be created
        5. Come back here and click "I Created the Project"
        """)
        
        st.image("https://via.placeholder.com/800x400/667eea/ffffff?text=Screenshot+would+go+here", 
                 caption="Example: Creating a new project")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📁 Open 'New Project' Page", use_container_width=True, type="primary"):
            webbrowser.open("https://console.cloud.google.com/projectcreate")
            st.success("✅ Opened in your browser!")
    
    with col2:
        if st.button("✅ I Created the Project", use_container_width=True):
            st.session_state.project_created = True
            st.session_state.setup_step = 3
            st.rerun()
    
    st.markdown("<div class='warning-box'>", unsafe_allow_html=True)
    st.markdown("**⚠️ Important:** Make sure to select your new project from the dropdown at the top of the page!")
    st.markdown("</div>", unsafe_allow_html=True)

# Step 3: Enable Gmail API
elif st.session_state.setup_step == 3:
    st.markdown("""
    <div class='step-card'>
        <h2>🔌 Step 3: Enable Gmail API</h2>
        <p style='font-size: 1.1rem;'>
            Now we need to enable the Gmail API so the app can access your emails.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### What to do:")
    
    with st.expander("📖 Detailed Instructions (Click to expand)", expanded=True):
        st.markdown("""
        1. **Click the button below** to open the Gmail API page
        2. Make sure your project is selected (top of page)
        3. Click the blue **"ENABLE"** button
        4. Wait a few seconds for it to enable
        5. Come back here and click "I Enabled the API"
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔌 Open Gmail API Page", use_container_width=True, type="primary"):
            webbrowser.open("https://console.cloud.google.com/apis/library/gmail.googleapis.com")
            st.success("✅ Opened in your browser!")
    
    with col2:
        if st.button("✅ I Enabled the API", use_container_width=True):
            st.session_state.api_enabled = True
            st.session_state.setup_step = 4
            st.rerun()
    
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    st.markdown("**💡 Tip:** The button might say 'MANAGE' if the API is already enabled. That's fine!")
    st.markdown("</div>", unsafe_allow_html=True)

# Step 4: Create Credentials
elif st.session_state.setup_step == 4:
    st.markdown("""
    <div class='step-card'>
        <h2>🔑 Step 4: Create OAuth Credentials</h2>
        <p style='font-size: 1.1rem;'>
            Almost there! Now we need to create credentials so the app can authenticate.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### What to do:")
    
    with st.expander("📖 Detailed Instructions (Click to expand)", expanded=True):
        st.markdown("""
        **Part A: Configure OAuth Consent Screen**
        1. Click "Configure OAuth Consent Screen" button below
        2. Choose **"External"** user type
        3. Click **"CREATE"**
        4. Fill in required fields:
           - App name: `Gmail Unsubscriber`
           - User support email: Your email
           - Developer contact: Your email
        5. Click **"SAVE AND CONTINUE"** (3 times to skip through screens)
        6. Click **"BACK TO DASHBOARD"**
        
        **Part B: Create Credentials**
        1. Click "Create Credentials" button below
        2. Click **"CREATE CREDENTIALS"** → **"OAuth client ID"**
        3. Application type: Choose **"Desktop app"**
        4. Name: `Desktop Client`
        5. Click **"CREATE"**
        6. Click **"DOWNLOAD JSON"** on the popup
        7. Save the file as `credentials.json` in this project folder
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔐 Configure OAuth Consent", use_container_width=True):
            webbrowser.open("https://console.cloud.google.com/apis/credentials/consent")
            st.success("✅ Opened in your browser!")
    
    with col2:
        if st.button("🔑 Create Credentials", use_container_width=True):
            webbrowser.open("https://console.cloud.google.com/apis/credentials")
            st.success("✅ Opened in your browser!")
    
    st.markdown("---")
    st.markdown("### 📥 Upload Your Credentials File")
    
    uploaded_file = st.file_uploader(
        "After downloading, upload the JSON file here:",
        type=['json'],
        help="This is the file you downloaded from Google Cloud Console"
    )
    
    if uploaded_file is not None:
        try:
            # Read and validate the file
            content = uploaded_file.read()
            data = json.loads(content)
            
            # Check if it's valid
            if 'installed' in data or 'web' in data:
                # Save to credentials.json
                with open('credentials.json', 'wb') as f:
                    f.write(content)
                
                st.success("✅ Credentials file saved successfully!")
                
                time.sleep(1)
                st.session_state.credentials_created = True
                st.session_state.setup_step = 5
                st.rerun()
            else:
                st.error("❌ This doesn't look like a valid credentials file. Please download the correct file.")
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
    
    st.markdown("<div class='warning-box'>", unsafe_allow_html=True)
    st.markdown("**⚠️ Important:** The file MUST be named exactly `credentials.json` (or upload it above)")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Manual verification option
    st.markdown("---")
    if st.button("✅ I Saved credentials.json Manually", use_container_width=True):
        creds_exist, _ = check_credentials_file()
        if creds_exist:
            st.success("✅ Credentials file detected!")
            st.session_state.credentials_created = True
            st.session_state.setup_step = 5
            st.rerun()
        else:
            st.error("❌ credentials.json not found. Please upload it above or save it in the project folder.")

# Step 5: Add Test User (IMPORTANT!)
elif st.session_state.setup_step == 5:
    st.markdown("""
    <div class='step-card'>
        <h2>👤 Step 5: Add Yourself as Test User</h2>
        <p style='font-size: 1.1rem;'>
            <strong>⚠️ IMPORTANT:</strong> This step prevents the "Access blocked" error!
        </p>
        <p style='font-size: 1.1rem;'>
            Your app is in Testing mode, so you need to add your email as an authorized test user.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### What to do:")
    
    with st.expander("📖 Detailed Instructions (Click to expand)", expanded=True):
        st.markdown("""
        1. **Click the button below** to open OAuth Consent Screen
        2. Scroll down to the **"Test users"** section
        3. Click **"+ ADD USERS"** button
        4. Enter your Gmail address (the one you want to scan)
        5. Click **"SAVE"**
        6. Come back here and click "I Added Myself"
        
        **Why this matters:**
        - Without this, you'll get "Access blocked" error
        - Your app is in Testing mode (which is good for privacy!)
        - Only test users can authenticate
        - This takes 30 seconds and prevents errors!
        """)
        
        st.warning("**💡 Pro Tip:** Add any other Gmail accounts you want to use with this tool!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👤 Open OAuth Consent Screen", use_container_width=True, type="primary"):
            webbrowser.open("https://console.cloud.google.com/apis/credentials/consent")
            st.success("✅ Opened in your browser!")
            st.info("Look for the 'Test users' section and click '+ ADD USERS'")
    
    with col2:
        if st.button("✅ I Added Myself as Test User", use_container_width=True):
            st.session_state.test_user_added = True
            st.session_state.setup_step = 6
            st.rerun()
    
    st.markdown("<div class='warning-box'>", unsafe_allow_html=True)
    st.markdown("""
    **⚠️ Don't Skip This Step!**
    
    If you skip this, you'll see: "Access blocked: App has not completed Google verification"
    
    Just add your email as a test user and you're good to go!
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Step 6: Complete
elif st.session_state.setup_step == 6:
    st.balloons()
    
    st.markdown("""
    <div class='success-box'>
        <h2 style='text-align: center;'>🎉 Setup Complete!</h2>
        <p style='text-align: center; font-size: 1.2rem;'>
            You're all set! Your credentials are configured and ready to use.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ✅ What's Been Set Up:")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - ✅ Google Cloud Project created
        - ✅ Gmail API enabled
        - ✅ OAuth credentials configured
        - ✅ credentials.json file saved
        """)
    
    with col2:
        st.markdown("""
        - ✅ Ready to authenticate
        - ✅ Ready to scan emails
        - ✅ Ready to unsubscribe
        - ✅ Privacy protected
        """)
    
    st.markdown("---")
    st.markdown("### 🚀 Next Steps:")
    
    st.markdown("""
    <div class='info-box'>
        <h3>Option 1: Use the Streamlit App (Recommended)</h3>
        <p>Beautiful UI with one-click automation</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎨 Launch Streamlit App", use_container_width=True, type="primary"):
            st.switch_page("pages/1_📧_Main_App.py")
    
    st.markdown("""
    <div class='info-box'>
        <h3>Option 2: Use Command Line</h3>
        <p>For terminal lovers</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.code("python src/main.py", language="bash")
    
    st.markdown("---")
    st.markdown("### 📚 Helpful Resources:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📖 Documentation**
        - [README.md](README.md)
        - [Setup Guide](SETUP_GUIDE.md)
        - [Privacy Policy](PRIVACY.md)
        """)
    
    with col2:
        st.markdown("""
        **🔧 Configuration**
        - Edit `src/config.py`
        - Adjust scan settings
        - Customize behavior
        """)
    
    with col3:
        st.markdown("""
        **🆘 Need Help?**
        - Check troubleshooting
        - Review setup guide
        - Open an issue
        """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👤 Go Back to Add Test User", use_container_width=True):
            st.session_state.setup_step = 5
            st.rerun()
    with col2:
        if st.button("🔄 Run Setup Again", use_container_width=True):
            # Delete credentials and token files
            if os.path.exists('credentials.json'):
                os.remove('credentials.json')
            if os.path.exists('token.json'):
                os.remove('token.json')
            
            # Reset all state
            st.session_state.setup_step = 0
            st.session_state.project_created = False
            st.session_state.api_enabled = False
            st.session_state.credentials_created = False
            st.session_state.test_user_added = False
            st.success("✅ Credentials deleted. Starting fresh!")
            time.sleep(1)
            st.rerun()

# Sidebar
with st.sidebar:
    st.markdown("### 🔧 Setup Wizard")
    st.markdown(f"**Current Step:** {st.session_state.setup_step + 1}/6")
    
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("Home.py")
    
    st.markdown("---")
    st.markdown("### ❓ Need Help?")
    
    with st.expander("🎥 Video Tutorial"):
        st.markdown("Coming soon! For now, follow the step-by-step instructions.")
    
    with st.expander("📝 Text Guide"):
        st.markdown("See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed written instructions.")
    
    with st.expander("🐛 Troubleshooting"):
        st.markdown("""
        **Common Issues:**
        
        1. **Can't create project**
           - Make sure you're signed in
           - Try a different project name
        
        2. **Can't enable API**
           - Make sure project is selected
           - Wait a few seconds and refresh
        
        3. **Can't download credentials**
           - Make sure OAuth consent is configured
           - Choose "Desktop app" type
        """)
    
    st.markdown("---")
    st.markdown("### 🔒 Privacy")
    st.info("These credentials are YOURS. They stay on YOUR computer. No one else has access.")
