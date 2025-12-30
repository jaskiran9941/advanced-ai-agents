#!/usr/bin/env python3
"""
One-Click Twitter Account Linking
Automatically opens browser and handles callback - no manual steps!
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from auth.oauth_manager import oauth_manager
import subprocess
import time

# Twitter credentials
TWITTER_CLIENT_ID = "YOUR_TWITTER_CLIENT_ID"
REDIRECT_URI = "http://localhost:5000/twitter_callback"

print("\n" + "=" * 70)
print("🐦 One-Click Twitter Account Linking")
print("=" * 70)

# Check if callback server is running
import socket
def is_server_running(port=5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

if not is_server_running():
    print("\n⚠️  OAuth callback server is not running!")
    print("\nPlease open a new terminal and run:")
    print("   python3 oauth_callback_server.py")
    print("\nThen run this script again.")
    sys.exit(1)

print("\n✅ Callback server is running")

# Generate auth URL
print("🔗 Generating authorization URL...")
auth_data = oauth_manager.get_twitter_auth_url(TWITTER_CLIENT_ID, REDIRECT_URI)
auth_url = auth_data['auth_url']

print("✅ Authorization URL generated")
print("\n🌐 Opening Twitter in your browser...")
print("\n" + "=" * 70)
print("Just authorize the app on Twitter - everything else is automatic!")
print("=" * 70)

# Open browser
try:
    subprocess.run(['open', auth_url], check=True)
except:
    print(f"\n⚠️  Could not open browser. Please open this URL manually:")
    print(f"\n{auth_url}\n")

print("\n⏳ Waiting for you to authorize...")
print("   (After authorization, your account will be linked automatically)")

# Wait and check if account gets linked
for i in range(60):
    time.sleep(1)
    if oauth_manager.is_linked('twitter'):
        print("\n\n" + "=" * 70)
        print("🎉 SUCCESS! Your Twitter account is linked!")
        print("=" * 70)
        print("\n✅ You can now use the Streamlit app to publish to Twitter")
        print("✅ The callback server handled everything automatically")
        print("\n" + "=" * 70)
        sys.exit(0)

print("\n\n⏱️  Timeout - account was not linked within 60 seconds")
print("   This usually means:")
print("   - You didn't complete authorization")
print("   - The authorization code expired")
print("   - There was an error (check callback server logs)")
print("\nPlease try again!")
