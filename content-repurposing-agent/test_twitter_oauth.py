"""
Test Twitter OAuth Flow
Tests the PKCE implementation and OAuth flow mechanics
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from auth.oauth_manager import oauth_manager

# Your Twitter credentials
TWITTER_CLIENT_ID = "YOUR_TWITTER_CLIENT_ID"
TWITTER_CLIENT_SECRET = "YOUR_TWITTER_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8501/twitter_callback"

print("=" * 70)
print("Twitter OAuth PKCE Flow Test")
print("=" * 70)

# Step 1: Generate auth URL
print("\n[Step 1] Generating Twitter authorization URL...")
try:
    auth_data = oauth_manager.get_twitter_auth_url(TWITTER_CLIENT_ID, REDIRECT_URI)
    print(f"✅ Auth URL generated successfully")
    print(f"\nState: {auth_data['state']}")
    print(f"\nFull Auth URL:\n{auth_data['auth_url']}\n")

    # Check if state was saved
    saved_state = oauth_manager.state_storage.get('twitter')
    if saved_state:
        print(f"✅ State saved to storage")
        print(f"   - State: {saved_state['state'][:20]}...")
        print(f"   - Code Verifier: {saved_state['code_verifier'][:20]}...")
    else:
        print("❌ State NOT saved to storage!")

except Exception as e:
    print(f"❌ Failed to generate auth URL: {e}")
    sys.exit(1)

# Step 2: Verify state persistence (reload oauth_manager)
print("\n[Step 2] Testing state persistence...")
from auth.oauth_manager import OAuthManager
new_manager = OAuthManager()
reloaded_state = new_manager.state_storage.get('twitter')

if reloaded_state and reloaded_state['state'] == auth_data['state']:
    print("✅ State persisted correctly across reload")
    print(f"   - State matches: {reloaded_state['state'] == auth_data['state']}")
    print(f"   - Code verifier available: {bool(reloaded_state.get('code_verifier'))}")
else:
    print("❌ State NOT persisted correctly!")
    if reloaded_state:
        print(f"   States match: {reloaded_state.get('state') == auth_data['state']}")
    else:
        print("   No state found after reload")

# Step 3: Instructions for manual testing
print("\n" + "=" * 70)
print("MANUAL TESTING STEPS")
print("=" * 70)
print("""
1. Copy the auth URL above and paste it in your browser
2. Authorize the app on Twitter
3. After redirect, copy the 'code' and 'state' from the URL
4. Run this command to test token exchange:

   python3 test_twitter_oauth_exchange.py <CODE> <STATE>

""")

print("=" * 70)
print("PKCE Parameters Check")
print("=" * 70)

# Verify PKCE parameters are in the URL
auth_url = auth_data['auth_url']
if "code_challenge=" in auth_url and "code_challenge_method=S256" in auth_url:
    print("✅ PKCE parameters present in auth URL")
    # Extract code_challenge
    import re
    challenge_match = re.search(r'code_challenge=([^&]+)', auth_url)
    if challenge_match:
        code_challenge = challenge_match.group(1)
        print(f"   - Code Challenge: {code_challenge[:30]}...")
        print(f"   - Challenge Method: S256")

        # Verify it's not the placeholder "challenge"
        if code_challenge == "challenge":
            print("   ❌ WARNING: Using placeholder 'challenge' instead of real hash!")
        else:
            print("   ✅ Using computed code challenge (not placeholder)")
else:
    print("❌ PKCE parameters MISSING from auth URL!")

print("\n" + "=" * 70)
