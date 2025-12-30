"""
Test Twitter OAuth Token Exchange
Tests the second part of the OAuth flow - exchanging code for token
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

if len(sys.argv) != 3:
    print("Usage: python3 test_twitter_oauth_exchange.py <CODE> <STATE>")
    print("\nExample:")
    print("  python3 test_twitter_oauth_exchange.py 'abc123...' 'xyz789...'")
    sys.exit(1)

code = sys.argv[1]
state = sys.argv[2]

from auth.oauth_manager import oauth_manager

# Your Twitter credentials
TWITTER_CLIENT_ID = "YOUR_TWITTER_CLIENT_ID"
TWITTER_CLIENT_SECRET = "YOUR_TWITTER_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8501/twitter_callback"

print("=" * 70)
print("Twitter OAuth Token Exchange Test")
print("=" * 70)

# Check if state is stored
print("\n[Step 1] Checking stored state...")
stored_state = oauth_manager.state_storage.get('twitter')
if stored_state:
    print("✅ Stored state found")
    print(f"   - Stored state: {stored_state['state'][:20]}...")
    print(f"   - Provided state: {state[:20]}...")
    print(f"   - States match: {stored_state['state'] == state}")
    print(f"   - Code verifier available: {bool(stored_state.get('code_verifier'))}")
else:
    print("❌ No stored state found!")
    sys.exit(1)

# Attempt token exchange
print("\n[Step 2] Attempting token exchange...")
try:
    result = oauth_manager.exchange_twitter_code(
        code=code,
        client_id=TWITTER_CLIENT_ID,
        client_secret=TWITTER_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        state=state
    )
    print("✅ Token exchange SUCCESSFUL!")
    print(f"\nToken data:")
    print(f"   - Access token: {result['access_token'][:20]}...")
    print(f"   - Refresh token: {result.get('refresh_token', 'N/A')[:20]}...")
    print(f"   - Expires in: {result['expires_in']} seconds")
    print(f"   - Platform: {result['platform']}")

    # Verify token was saved
    saved_token = oauth_manager.get_token('twitter')
    if saved_token:
        print("\n✅ Token saved successfully")
        print(f"   - Is linked: {oauth_manager.is_linked('twitter')}")
    else:
        print("\n❌ Token NOT saved")

except Exception as e:
    print(f"❌ Token exchange FAILED!")
    print(f"\nError: {e}")
    print(f"\nError type: {type(e).__name__}")

    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "=" * 70)
