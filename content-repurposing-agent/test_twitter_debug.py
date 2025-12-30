"""
Debug Twitter OAuth - Shows exactly what's being sent
"""
import sys
import hashlib
import base64
import requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from auth.oauth_manager import oauth_manager

# Your Twitter credentials
TWITTER_CLIENT_ID = "YOUR_TWITTER_CLIENT_ID"
TWITTER_CLIENT_SECRET = "YOUR_TWITTER_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8501/twitter_callback"

if len(sys.argv) != 3:
    print("Usage: python3 test_twitter_debug.py <CODE> <STATE>")
    sys.exit(1)

code = sys.argv[1]
state = sys.argv[2]

print("=" * 70)
print("Twitter OAuth Debug - Detailed Request Analysis")
print("=" * 70)

# Get stored state
stored_state = oauth_manager.state_storage.get('twitter', {})
if not stored_state:
    print("❌ No stored state! Run test_twitter_oauth.py first")
    sys.exit(1)

print("\n[State Verification]")
print(f"Stored state: {stored_state['state']}")
print(f"Provided state: {state}")
print(f"Match: {stored_state['state'] == state}")

if stored_state['state'] != state:
    print("\n❌ State mismatch! This could be the problem.")
    print("Make sure you're using the state from the SAME auth URL generation")
    sys.exit(1)

code_verifier = stored_state['code_verifier']
print(f"\nCode verifier: {code_verifier}")

# Verify code_challenge matches
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode('ascii')).digest()
).decode('ascii').rstrip('=')
print(f"Code challenge (recomputed): {code_challenge}")

print("\n" + "=" * 70)
print("[Token Exchange Request Details]")
print("=" * 70)

request_data = {
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": REDIRECT_URI,
    "code_verifier": code_verifier
}

print("\nEndpoint: https://api.twitter.com/2/oauth2/token")
print("\nMethod: POST")
print("\nHeaders:")
print(f"  Content-Type: application/x-www-form-urlencoded")
print(f"  Authorization: Basic (client_id:client_secret)")

print("\nRequest Body:")
for key, value in request_data.items():
    if key == "code" or key == "code_verifier":
        print(f"  {key}: {value[:30]}...")
    else:
        print(f"  {key}: {value}")

print("\n" + "=" * 70)
print("[Making Request to Twitter]")
print("=" * 70)

try:
    response = requests.post(
        "https://api.twitter.com/2/oauth2/token",
        data=request_data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        auth=(TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET)
    )

    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")

    print(f"\nResponse Body:")
    print(response.text)

    if response.status_code == 200:
        print("\n✅ SUCCESS! Token exchange worked!")
        token_data = response.json()
        print(f"\nAccess Token: {token_data.get('access_token', 'N/A')[:30]}...")
        print(f"Token Type: {token_data.get('token_type', 'N/A')}")
        print(f"Expires In: {token_data.get('expires_in', 'N/A')} seconds")
        print(f"Refresh Token: {token_data.get('refresh_token', 'N/A')[:30] if token_data.get('refresh_token') else 'N/A'}...")
    else:
        print(f"\n❌ FAILED with status {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error: {error_data}")
        except:
            print(f"Error (raw): {response.text}")

except Exception as e:
    print(f"\n❌ Exception occurred: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
