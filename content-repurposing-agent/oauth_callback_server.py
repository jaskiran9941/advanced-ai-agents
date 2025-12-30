#!/usr/bin/env python3
"""
OAuth Callback Server
Runs a local server to automatically handle OAuth redirects from social media platforms
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from auth.oauth_manager import oauth_manager

# Twitter credentials
TWITTER_CLIENT_ID = "YOUR_TWITTER_CLIENT_ID"
TWITTER_CLIENT_SECRET = "YOUR_TWITTER_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:5000/twitter_callback"

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handles OAuth callbacks from social media platforms"""

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

    def do_GET(self):
        """Handle GET requests (OAuth redirects)"""
        parsed_path = urlparse(self.path)

        # Twitter callback
        if parsed_path.path == '/twitter_callback':
            self.handle_twitter_callback(parsed_path)

        # LinkedIn callback
        elif parsed_path.path == '/linkedin_callback':
            self.handle_linkedin_callback(parsed_path)

        # Instagram callback
        elif parsed_path.path == '/instagram_callback':
            self.handle_instagram_callback(parsed_path)

        # Health check
        elif parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"OK - OAuth Callback Server Running")

        else:
            self.send_response(404)
            self.end_headers()

    def handle_twitter_callback(self, parsed_path):
        """Handle Twitter OAuth callback"""
        params = parse_qs(parsed_path.query)

        if 'error' in params:
            self.send_error_page(f"Twitter authorization failed: {params['error'][0]}")
            return

        if 'code' not in params or 'state' not in params:
            self.send_error_page("Missing code or state parameter")
            return

        code = params['code'][0]
        state = params['state'][0]

        print(f"\n✅ Received Twitter callback")
        print(f"   Code: {code[:30]}...")
        print(f"   State: {state[:30]}...")

        try:
            # Exchange code for token
            print("🔗 Exchanging code for access token...")
            result = oauth_manager.exchange_twitter_code(
                code=code,
                client_id=TWITTER_CLIENT_ID,
                client_secret=TWITTER_CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                state=state
            )

            print("🎉 SUCCESS! Twitter account linked!")
            print(f"   Access token: {result['access_token'][:30]}...")
            print(f"   Expires in: {result['expires_in']//3600} hours")

            self.send_success_page("Twitter", result)

        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_error_page(f"Failed to link Twitter account: {str(e)}")

    def handle_linkedin_callback(self, parsed_path):
        """Handle LinkedIn OAuth callback"""
        # Similar implementation for LinkedIn
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"LinkedIn callback - Coming soon!")

    def handle_instagram_callback(self, parsed_path):
        """Handle Instagram OAuth callback"""
        # Similar implementation for Instagram
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Instagram callback - Coming soon!")

    def send_success_page(self, platform, result):
        """Send HTML success page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Account Linked Successfully</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                }}
                .success-icon {{
                    font-size: 64px;
                    margin-bottom: 20px;
                }}
                h1 {{
                    color: #10b981;
                    margin: 0 0 10px 0;
                }}
                p {{
                    color: #6b7280;
                    line-height: 1.6;
                }}
                .details {{
                    background: #f9fafb;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    text-align: left;
                }}
                .details-item {{
                    margin: 10px 0;
                }}
                .label {{
                    font-weight: 600;
                    color: #374151;
                }}
                .value {{
                    color: #6b7280;
                }}
                .button {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 24px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                }}
                .button:hover {{
                    background: #5568d3;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">🎉</div>
                <h1>Success!</h1>
                <p>Your {platform} account has been linked successfully.</p>

                <div class="details">
                    <div class="details-item">
                        <span class="label">Platform:</span>
                        <span class="value">{platform}</span>
                    </div>
                    <div class="details-item">
                        <span class="label">Status:</span>
                        <span class="value">✅ Active</span>
                    </div>
                    <div class="details-item">
                        <span class="label">Token expires in:</span>
                        <span class="value">{result['expires_in']//3600} hours</span>
                    </div>
                </div>

                <p><strong>You can now close this window and return to the app.</strong></p>
                <a href="http://localhost:8501" class="button">Go to App</a>
            </div>
        </body>
        </html>
        """

        self.wfile.write(html.encode())

    def send_error_page(self, error_message):
        """Send HTML error page"""
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
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                }}
                .error-icon {{
                    font-size: 64px;
                    margin-bottom: 20px;
                }}
                h1 {{
                    color: #ef4444;
                    margin: 0 0 10px 0;
                }}
                p {{
                    color: #6b7280;
                    line-height: 1.6;
                }}
                .error-details {{
                    background: #fee2e2;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                    color: #991b1b;
                    font-family: monospace;
                    font-size: 14px;
                }}
                .button {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 24px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">❌</div>
                <h1>Authorization Failed</h1>
                <p>There was an error linking your account.</p>

                <div class="error-details">{error_message}</div>

                <p>Please try again or contact support if the problem persists.</p>
                <a href="http://localhost:8501" class="button">Return to App</a>
            </div>
        </body>
        </html>
        """

        self.wfile.write(html.encode())


def run_server(port=5000):
    """Run the OAuth callback server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, OAuthCallbackHandler)

    print("=" * 70)
    print("🚀 OAuth Callback Server Started")
    print("=" * 70)
    print(f"\n✅ Server running on http://localhost:{port}")
    print("\nCallback endpoints:")
    print(f"   Twitter:   http://localhost:{port}/twitter_callback")
    print(f"   LinkedIn:  http://localhost:{port}/linkedin_callback")
    print(f"   Instagram: http://localhost:{port}/instagram_callback")
    print("\n💡 Keep this server running while linking accounts")
    print("   Press Ctrl+C to stop")
    print("\n" + "=" * 70 + "\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        httpd.server_close()


if __name__ == '__main__':
    run_server()
