"""
Account Linking Page - One-Click OAuth Integration

Allows users to connect their social media accounts with simple one-click buttons
"""
import streamlit as st
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from auth.oauth_manager import oauth_manager
from utils.oauth_helpers import (
    link_twitter_account, link_linkedin_account,
    get_oauth_status, reset_oauth_status
)

st.set_page_config(
    page_title="Account Linking",
    page_icon="🔗",
    layout="wide"
)

st.title("🔗 Link Your Social Media Accounts")
st.markdown("""
Connect your social media accounts with **one click** - no manual copy/pasting required!
Your credentials are stored securely and only used for posting content.
""")

# Display currently linked accounts
st.header("Connected Accounts")

linked_platforms = oauth_manager.get_all_linked_platforms()

if linked_platforms:
    cols = st.columns(min(len(linked_platforms), 4))
    for i, (platform, data) in enumerate(linked_platforms.items()):
        with cols[i % 4]:
            st.success(f"✅ {platform.title()}")
            st.caption(f"Linked: {data['linked_at'][:10]}")
            if st.button(f"Unlink", key=f"unlink_{platform}"):
                if oauth_manager.unlink_platform(platform):
                    st.success(f"{platform.title()} unlinked!")
                    st.rerun()
else:
    st.info("No accounts linked yet. Link your accounts below to enable publishing.")

st.divider()

# Account linking sections
st.header("Link New Accounts")

st.info("""
💡 **How it works:**
1. Enter your app credentials below
2. Click "Link Account" button
3. Authorize in the browser that opens
4. Done! Your account will be linked automatically
""")

# Create tabs for each platform
tabs = st.tabs(["🐦 Twitter/X", "🔵 LinkedIn"])

# ============================================================================
# TWITTER/X - ONE-CLICK LINKING
# ============================================================================
with tabs[0]:
    st.subheader("Twitter/X Account Linking")

    if oauth_manager.is_linked('twitter'):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success("✅ Twitter account is linked and active!")
            token_data = oauth_manager.get_token('twitter')
            if token_data:
                st.caption(f"Linked at: {token_data.get('linked_at', 'N/A')[:19]}")
        with col2:
            if st.button("🔄 Relink", key="relink_twitter"):
                oauth_manager.unlink_platform('twitter')
                reset_oauth_status('twitter')
                st.rerun()
    else:
        st.markdown("""
        **Connect your Twitter account to publish tweets automatically.**

        📋 **Setup Instructions:**
        1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
        2. Create an app and enable OAuth 2.0
        3. Set redirect URI to: `http://localhost:5000/twitter_callback`
        4. Copy your Client ID and Client Secret
        5. Enter them below and click "Link Account"
        """)

        with st.form("twitter_link_form"):
            st.text_input("Client ID", key="twitter_client_id", type="password")
            st.text_input("Client Secret", key="twitter_client_secret", type="password")

            submitted = st.form_submit_button("🔗 Link Twitter Account", type="primary", use_container_width=True)

            if submitted:
                if not st.session_state.twitter_client_id or not st.session_state.twitter_client_secret:
                    st.error("Please enter both Client ID and Secret")
                else:
                    with st.spinner("Starting OAuth flow..."):
                        success, auth_url, error = link_twitter_account(
                            st.session_state.twitter_client_id,
                            st.session_state.twitter_client_secret
                        )

                    if success:
                        st.session_state['twitter_auth_started'] = True
                        st.session_state['twitter_auth_time'] = time.time()
                        st.success("✅ Browser opened! Please authorize the app.")
                    else:
                        st.error(f"Failed: {error}")

        # Check OAuth status if auth was started
        if st.session_state.get('twitter_auth_started'):
            status = get_oauth_status('twitter')

            if status['success']:
                st.session_state['twitter_auth_started'] = False
                st.success("🎉 Twitter account linked successfully!")
                time.sleep(1)
                st.rerun()
            elif status['error']:
                st.session_state['twitter_auth_started'] = False
                st.error(f"❌ Authorization failed: {status['error']}")
                reset_oauth_status('twitter')
            elif status['in_progress']:
                elapsed = int(time.time() - st.session_state.get('twitter_auth_time', time.time()))
                if elapsed > 60:
                    st.session_state['twitter_auth_started'] = False
                    st.warning("⏱️ Timeout. Please try again.")
                    reset_oauth_status('twitter')
                else:
                    with st.spinner(f"Waiting for authorization... ({60 - elapsed}s)"):
                        time.sleep(2)
                        st.rerun()

# ============================================================================
# LINKEDIN - ONE-CLICK LINKING
# ============================================================================
with tabs[1]:
    st.subheader("LinkedIn Account Linking")

    if oauth_manager.is_linked('linkedin'):
        st.success("✅ LinkedIn account is linked!")
    else:
        st.markdown("""
        **Connect your LinkedIn account to publish posts automatically.**

        📋 **Setup Instructions:**
        1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
        2. Create an app and go to "Products" tab
        3. Request access to "Share on LinkedIn" and "Sign In with LinkedIn using OpenID Connect"
        4. Go to "Auth" tab, add redirect URI: `http://localhost:5000/linkedin_callback`
        5. Required permissions will be: `w_member_social`, `openid`, `profile`
        6. Copy your Client ID and Client Secret from "Auth" tab
        7. Enter them below and click "Link Account"

        ⚠️ **Note:** LinkedIn may require review before granting "Share on LinkedIn" product access.
        """)

        with st.form("linkedin_link_form"):
            linkedin_client_id = st.text_input("LinkedIn Client ID", type="password", key="linkedin_cid")
            linkedin_client_secret = st.text_input("LinkedIn Client Secret", type="password", key="linkedin_csecret")

            submitted = st.form_submit_button("🔗 Link LinkedIn Account", type="primary", use_container_width=True)

            if submitted:
                if not linkedin_client_id or not linkedin_client_secret:
                    st.error("Please enter both Client ID and Secret")
                else:
                    with st.spinner("Starting OAuth flow..."):
                        success, auth_url, error = link_linkedin_account(linkedin_client_id, linkedin_client_secret)

                        if success:
                            st.session_state['linkedin_auth_started'] = True
                            st.session_state['linkedin_auth_time'] = time.time()
                            st.success("✅ Browser opened! Please authorize the app.")
                        else:
                            st.error(f"Failed: {error}")

        # Check OAuth status
        if st.session_state.get('linkedin_auth_started'):
            status = get_oauth_status('linkedin')

            if status['success']:
                st.session_state['linkedin_auth_started'] = False
                st.success("🎉 LinkedIn account linked!")
                time.sleep(1)
                st.rerun()
            elif status['error']:
                st.session_state['linkedin_auth_started'] = False
                st.error(f"❌ Failed: {status['error']}")
                reset_oauth_status('linkedin')
            elif status['in_progress']:
                elapsed = int(time.time() - st.session_state.get('linkedin_auth_time', time.time()))
                if elapsed > 60:
                    st.session_state['linkedin_auth_started'] = False
                    st.warning("⏱️ Timeout")
                    reset_oauth_status('linkedin')
                else:
                    with st.spinner(f"Waiting... ({60 - elapsed}s)"):
                        time.sleep(2)
                        st.rerun()

# Footer
st.divider()
st.caption("""
**Security Notes:**
- Credentials are stored locally and encrypted
- OAuth tokens are only used for posting
- You can unlink accounts anytime
- OAuth callback server runs on localhost:5000
""")
