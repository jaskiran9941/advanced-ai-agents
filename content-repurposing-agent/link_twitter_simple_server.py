#!/usr/bin/env python3
"""
Simple Twitter Account Linking - Single Process Solution
Runs a temporary server, opens browser, links account automatically
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import subprocess
import time
from auth.oauth_manager import oauth_manager

# Twitter credentials - Set these from your Twitter Developer Portal
TWITTER_CLIENT_ID = "YOUR_TWITTER_CLIENT_ID"
TWITTER_CLIENT_SECRET = "YOUR_TWITTER_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:5000/twitter_callback"

# Global flag to track success
link_success = False
link_error = None

class TwitterCallbackHandler(BaseHTTPRequestHandler):
    """Handles Twitter OAuth callback"""

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

    def do_GET(self):
        """Handle GET requests"""
        global link_success, link_error

        parsed_path = urlparse(self.path)

        if parsed_path.path == '/twitter_callback':
            params = parse_qs(parsed_path.query)

            if 'error' in params:
                link_error = f"Authorization denied: {params['error'][0]}"
                self.send_error_page(link_error)
                return

            if 'code' not in params or 'state' not in params:
                link_error = "Missing code or state parameter"
                self.send_error_page(link_error)
                return

            code = params['code'][0]
            state = params['state'][0]

            print(f"\n✅ Received callback from Twitter")
            print(f"   Processing authorization...")

            try:
                # Exchange code for token
                result = oauth_manager.exchange_twitter_code(
                    code=code,
                    client_id=TWITTER_CLIENT_ID,
                    client_secret=TWITTER_CLIENT_SECRET,
                    redirect_uri=REDIRECT_URI,
                    state=state
                )

                link_success = True
                print(f"\n🎉 SUCCESS! Twitter account linked!")
                print(f"   Access token received")
                print(f"   Expires in: {result['expires_in']//3600} hours")

                self.send_success_page()

            except Exception as e:
                link_error = str(e)
                print(f"\n❌ Error: {e}")
                self.send_error_page(str(e))

        else:
            self.send_response(404)
            self.end_headers()

    def send_success_page(self):
        """Send success page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Success!</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .container {
                    background: white;
                    padding: 60px 40px;
                    border-radius: 16px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 500px;
                }
                .icon { font-size: 80px; margin-bottom: 20px; }
                h1 { color: #10b981; margin: 0 0 15px 0; font-size: 32px; }
                p { color: #6b7280; font-size: 18px; line-height: 1.6; }
                .note { margin-top: 30px; padding: 20px; background: #f0fdf4; border-radius: 8px; color: #166534; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">🎉</div>
                <h1>Twitter Account Linked!</h1>
                <p>Your Twitter account has been successfully connected.</p>
                <div class="note">
                    <strong>✓ You can now close this window</strong><br>
                    Your account is ready to use in the Streamlit app
                </div>
            </div>
            <script>
                setTimeout(() => window.close(), 3000);
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def send_error_page(self, error):
        """Send error page"""
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                }}
                .container {{
                    background: white;
                    padding: 60px 40px;
                    border-radius: 16px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 500px;
                }}
                .icon {{ font-size: 80px; margin-bottom: 20px; }}
                h1 {{ color: #ef4444; margin: 0 0 15px 0; font-size: 32px; }}
                p {{ color: #6b7280; font-size: 16px; line-height: 1.6; }}
                .error {{ margin-top: 20px; padding: 20px; background: #fee2e2; border-radius: 8px; color: #991b1b; font-family: monospace; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">❌</div>
                <h1>Authorization Failed</h1>
                <p>There was an error linking your account.</p>
                <div class="error">{error}</div>
                <p style="margin-top: 20px;">Please close this window and try again.</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())


def run_server_thread(httpd):
    """Run server in thread"""
    httpd.serve_forever()


def main():
    global link_success, link_error

    print("\n" + "=" * 70)
    print("🐦 Twitter Account Linking")
    print("=" * 70)

    # Start server
    server = HTTPServer(('', 5000), TwitterCallbackHandler)
    server_thread = threading.Thread(target=run_server_thread, args=(server,), daemon=True)
    server_thread.start()

    print("\n✅ Temporary server started on http://localhost:5000")

    # Generate auth URL
    print("🔗 Generating authorization URL...")
    auth_data = oauth_manager.get_twitter_auth_url(TWITTER_CLIENT_ID, REDIRECT_URI)
    auth_url = auth_data['auth_url']

    print("✅ Opening Twitter in your browser...")
    print("\n" + "=" * 70)
    print("Please authorize the app on Twitter")
    print("Everything else will happen automatically!")
    print("=" * 70 + "\n")

    # Open browser
    try:
        subprocess.run(['open', auth_url], check=False)
    except:
        print(f"\nCouldn't open browser. Please open this URL manually:")
        print(f"\n{auth_url}\n")

    # Wait for callback (max 60 seconds)
    print("⏳ Waiting for authorization...")
    for i in range(60):
        time.sleep(1)
        if link_success:
            break
        if link_error:
            break

    # Stop server
    server.shutdown()

    print("\n" + "=" * 70)
    if link_success:
        print("✅ SUCCESS! Your Twitter account is now linked!")
        print("=" * 70)
        print("\nYou can now use the Streamlit app to publish to Twitter.")
        print("The temporary server has been stopped.")
    elif link_error:
        print("❌ FAILED")
        print("=" * 70)
        print(f"\nError: {link_error}")
        print("\nPlease try again.")
        sys.exit(1)
    else:
        print("⏱️  TIMEOUT")
        print("=" * 70)
        print("\nNo response received within 60 seconds.")
        print("Please try again and authorize more quickly.")
        sys.exit(1)

    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    main()
