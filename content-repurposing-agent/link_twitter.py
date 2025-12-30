#!/usr/bin/env python3
"""
One-Step Twitter Account Linking
Run this script to link your Twitter account in one command
"""
import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from auth.oauth_manager import oauth_manager
import subprocess

# Your Twitter credentials
TWITTER_CLIENT_ID = "YOUR_TWITTER_CLIENT_ID"
TWITTER_CLIENT_SECRET = "YOUR_TWITTER_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8501/twitter_callback"

print("=" * 70)
print("🐦 Twitter Account Linking - One-Step Setup")
print("=" * 70)

# Step 1: Generate auth URL
print("\n[1/3] Generating authorization URL...")
auth_data = oauth_manager.get_twitter_auth_url(TWITTER_CLIENT_ID, REDIRECT_URI)
auth_url = auth_data['auth_url']
state = auth_data['state']

print(f"✅ Authorization URL generated")
print(f"\n📋 State: {state}")

# Step 2: Open in browser
print("\n[2/3] Opening Twitter authorization in your browser...")
print("Please authorize the app when prompted.\n")

try:
    subprocess.run(['open', auth_url], check=True)
    print("✅ Browser opened")
except:
    print("⚠️  Could not open browser automatically")
    print(f"\nPlease open this URL manually:\n{auth_url}\n")

# Step 3: Wait for redirect URL
print("\n" + "=" * 70)
print("After authorizing, Twitter will redirect to a page that says")
print("'Page not found' - that's OK! Just copy the FULL URL from your")
print("browser's address bar and paste it below.")
print("=" * 70)

redirect_url = input("\n📋 Paste the redirect URL here: ").strip()

# Extract code and state from redirect URL
code_match = re.search(r'code=([^&]+)', redirect_url)
state_match = re.search(r'state=([^&]+)', redirect_url)

if not code_match or not state_match:
    print("\n❌ Could not extract code or state from URL!")
    print("Make sure you copied the complete redirect URL.")
    sys.exit(1)

code = code_match.group(1)
extracted_state = state_match.group(1)

print(f"\n✅ Extracted code: {code[:30]}...")
print(f"✅ Extracted state: {extracted_state[:30]}...")

# Step 4: Exchange code for token
print("\n[3/3] Exchanging authorization code for access token...")

try:
    result = oauth_manager.exchange_twitter_code(
        code=code,
        client_id=TWITTER_CLIENT_ID,
        client_secret=TWITTER_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        state=extracted_state
    )

    print("\n" + "=" * 70)
    print("🎉 SUCCESS! Your Twitter account is now linked!")
    print("=" * 70)
    print(f"\n✅ Access Token: {result['access_token'][:30]}...")
    print(f"✅ Token expires in: {result['expires_in']} seconds ({result['expires_in']//3600} hours)")
    print(f"✅ Refresh token available: {'Yes' if result.get('refresh_token') else 'No'}")

    # Verify it's saved
    if oauth_manager.is_linked('twitter'):
        print("\n✅ Account successfully saved and linked!")
        print("\nYou can now use the Streamlit app to publish to Twitter.")
    else:
        print("\n⚠️  Token received but not showing as linked. Check the logs.")

except Exception as e:
    print(f"\n❌ Failed to exchange code for token: {e}")
    print("\nThis usually means:")
    print("  - The authorization code was already used (try again)")
    print("  - The code expired (try again within 30 seconds)")
    print("  - Network/API error (check your connection)")
    sys.exit(1)

print("\n" + "=" * 70)
print("Done! Your Twitter account is ready to use.")
print("=" * 70)
