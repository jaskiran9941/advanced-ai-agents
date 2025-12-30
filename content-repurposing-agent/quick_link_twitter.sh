#!/bin/bash

# Quick Twitter Account Linking
# This script will open the browser and show you where to paste the URL

echo "========================================================================"
echo "🐦 Quick Twitter Account Linking"
echo "========================================================================"
echo ""

# Generate auth URL and capture it
python3 << 'PYTHON_EOF' > /tmp/twitter_auth_url.txt
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from auth.oauth_manager import oauth_manager

TWITTER_CLIENT_ID = "YOUR_TWITTER_CLIENT_ID"
REDIRECT_URI = "http://localhost:8501/twitter_callback"

auth_data = oauth_manager.get_twitter_auth_url(TWITTER_CLIENT_ID, REDIRECT_URI)
print(auth_data['auth_url'])
PYTHON_EOF

AUTH_URL=$(cat /tmp/twitter_auth_url.txt | tail -1)

echo "✅ Authorization URL generated!"
echo ""
echo "Opening Twitter in your browser..."
echo ""

# Open URL
open "$AUTH_URL"

echo "========================================================================"
echo "⚡ IMPORTANT: You have 60 seconds to authorize!"
echo "========================================================================"
echo ""
echo "After authorizing on Twitter:"
echo "1. You'll see 'Page not found' - that's OK!"
echo "2. Copy the FULL URL from your browser's address bar"
echo "3. Paste it below IMMEDIATELY (authorization codes expire fast!)"
echo ""
echo "========================================================================"
echo ""

# Get redirect URL
read -p "📋 Paste redirect URL here: " REDIRECT_URL

# Extract code and state, then link account
python3 << PYTHON_EOF
import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from auth.oauth_manager import oauth_manager

TWITTER_CLIENT_ID = "YOUR_TWITTER_CLIENT_ID"
TWITTER_CLIENT_SECRET = "YOUR_TWITTER_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8501/twitter_callback"

redirect_url = "${REDIRECT_URL}"

code_match = re.search(r'code=([^&]+)', redirect_url)
state_match = re.search(r'state=([^&]+)', redirect_url)

if not code_match or not state_match:
    print("❌ Could not extract code/state from URL!")
    sys.exit(1)

code = code_match.group(1)
state = state_match.group(1)

print(f"\n✅ Extracted code and state")
print("🔗 Linking account...")

try:
    result = oauth_manager.exchange_twitter_code(
        code=code,
        client_id=TWITTER_CLIENT_ID,
        client_secret=TWITTER_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        state=state
    )

    print("\n" + "=" * 70)
    print("🎉 SUCCESS! Your Twitter account is now linked!")
    print("=" * 70)
    print(f"✅ Access token received")
    print(f"✅ Expires in: {result['expires_in']//3600} hours")
    print(f"✅ Account is linked: {oauth_manager.is_linked('twitter')}")
    print("=" * 70)
    print("\nYou can now use the Streamlit app to publish to Twitter!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
PYTHON_EOF

# Cleanup
rm -f /tmp/twitter_auth_url.txt

echo ""
echo "Done!"
