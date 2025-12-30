#!/usr/bin/env python3
"""
Simple Twitter Account Linking - Shows URL, waits for redirect
"""
import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from auth.oauth_manager import oauth_manager

# Your Twitter credentials
TWITTER_CLIENT_ID = "YOUR_TWITTER_CLIENT_ID"
TWITTER_CLIENT_SECRET = "YOUR_TWITTER_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8501/twitter_callback"

print("\n" + "=" * 70)
print("🐦 Twitter Account Linking")
print("=" * 70)

# Generate auth URL
print("\n[Step 1] Generating authorization URL...")
auth_data = oauth_manager.get_twitter_auth_url(TWITTER_CLIENT_ID, REDIRECT_URI)
auth_url = auth_data['auth_url']
state = auth_data['state']

print(f"\n✅ URL generated successfully!")
print(f"\n📋 Copy this URL and open it in your browser:\n")
print(auth_url)
print(f"\n📋 State (for reference): {state}")

print("\n" + "=" * 70)
print("Instructions:")
print("1. Copy the URL above")
print("2. Open it in your browser")
print("3. Authorize the app on Twitter")
print("4. After redirect, copy the FULL URL from your browser")
print("5. Paste it below")
print("=" * 70)

# Get redirect URL from user
redirect_url = input("\n📋 Paste the full redirect URL here: ").strip()

if not redirect_url:
    print("\n❌ No URL provided!")
    sys.exit(1)

# Extract code and state
code_match = re.search(r'code=([^&]+)', redirect_url)
state_match = re.search(r'state=([^&]+)', redirect_url)

if not code_match or not state_match:
    print("\n❌ Could not find code/state in URL!")
    print(f"You provided: {redirect_url}")
    sys.exit(1)

code = code_match.group(1)
extracted_state = state_match.group(1)

print(f"\n✅ Code: {code[:30]}...")
print(f"✅ State: {extracted_state[:30]}...")

# Exchange for token
print("\n[Step 2] Exchanging code for access token...")

try:
    result = oauth_manager.exchange_twitter_code(
        code=code,
        client_id=TWITTER_CLIENT_ID,
        client_secret=TWITTER_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        state=extracted_state
    )

    print("\n" + "=" * 70)
    print("✅ SUCCESS! Twitter account linked!")
    print("=" * 70)
    print(f"\nAccess Token: {result['access_token'][:30]}...")
    print(f"Expires in: {result['expires_in']//3600} hours")
    print(f"Refresh token: {'Yes' if result.get('refresh_token') else 'No'}")

    if oauth_manager.is_linked('twitter'):
        print("\n✅ Account is now linked and ready to use!")

    print("\n" + "=" * 70)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
