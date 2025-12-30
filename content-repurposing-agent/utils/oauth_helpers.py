"""
OAuth Helper Functions for Streamlit Integration
Provides one-click OAuth linking functionality
"""
import threading
import subprocess
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from auth.oauth_manager import oauth_manager

# Global flags for OAuth callbacks
oauth_status = {
    'twitter': {'success': False, 'error': None, 'in_progress': False, 'client_id': None, 'client_secret': None},
    'linkedin': {'success': False, 'error': None, 'in_progress': False, 'client_id': None, 'client_secret': None},
    'instagram': {'success': False, 'error': None, 'in_progress': False, 'app_id': None, 'app_secret': None},
}


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handles OAuth callbacks from all platforms"""

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

    def do_GET(self):
        """Handle GET requests (OAuth redirects)"""
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/twitter_callback':
            self.handle_twitter_callback(parsed_path)
        elif parsed_path.path == '/linkedin_callback':
            self.handle_linkedin_callback(parsed_path)
        elif parsed_path.path == '/instagram_callback':
            self.handle_instagram_callback(parsed_path)
        else:
            self.send_response(404)
            self.end_headers()

    def handle_twitter_callback(self, parsed_path):
        """Handle Twitter OAuth callback"""
        params = parse_qs(parsed_path.query)

        if 'error' in params:
            oauth_status['twitter']['error'] = f"Authorization denied: {params['error'][0]}"
            oauth_status['twitter']['in_progress'] = False
            self.send_error_page("Twitter", oauth_status['twitter']['error'])
            return

        if 'code' not in params or 'state' not in params:
            oauth_status['twitter']['error'] = "Missing code or state parameter"
            oauth_status['twitter']['in_progress'] = False
            self.send_error_page("Twitter", oauth_status['twitter']['error'])
            return

        code = params['code'][0]
        state = params['state'][0]

        try:
            from auth.oauth_manager import oauth_manager

            # Get stored credentials
            client_id = oauth_status['twitter'].get('client_id')
            client_secret = oauth_status['twitter'].get('client_secret')

            if not client_id or not client_secret:
                oauth_status['twitter']['error'] = "Twitter credentials not found"
                oauth_status['twitter']['in_progress'] = False
                self.send_error_page("Twitter", "Please provide Twitter Client ID and Secret")
                return

            result = oauth_manager.exchange_twitter_code(
                code=code,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri="http://localhost:5000/twitter_callback",
                state=state
            )

            oauth_status['twitter']['success'] = True
            oauth_status['twitter']['in_progress'] = False
            self.send_success_page("Twitter")

        except Exception as e:
            oauth_status['twitter']['error'] = str(e)
            oauth_status['twitter']['in_progress'] = False
            self.send_error_page("Twitter", str(e))

    def handle_linkedin_callback(self, parsed_path):
        """Handle LinkedIn OAuth callback"""
        params = parse_qs(parsed_path.query)

        if 'error' in params:
            oauth_status['linkedin']['error'] = f"Authorization denied: {params['error'][0]}"
            oauth_status['linkedin']['in_progress'] = False
            self.send_error_page("LinkedIn", oauth_status['linkedin']['error'])
            return

        if 'code' not in params or 'state' not in params:
            oauth_status['linkedin']['error'] = "Missing code or state parameter"
            oauth_status['linkedin']['in_progress'] = False
            self.send_error_page("LinkedIn", oauth_status['linkedin']['error'])
            return

        code = params['code'][0]
        state = params['state'][0]

        try:
            from auth.oauth_manager import oauth_manager

            # Get stored credentials
            client_id = oauth_status['linkedin'].get('client_id')
            client_secret = oauth_status['linkedin'].get('client_secret')

            if not client_id or not client_secret:
                oauth_status['linkedin']['error'] = "LinkedIn requires client credentials to complete linking"
                oauth_status['linkedin']['in_progress'] = False
                self.send_error_page("LinkedIn", "Please provide LinkedIn Client ID and Secret to complete linking")
                return

            # Exchange code for token
            result = oauth_manager.exchange_linkedin_code(
                code=code,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri="http://localhost:5000/linkedin_callback",
                state=state
            )

            oauth_status['linkedin']['success'] = True
            oauth_status['linkedin']['in_progress'] = False
            self.send_success_page("LinkedIn")

        except Exception as e:
            oauth_status['linkedin']['error'] = str(e)
            oauth_status['linkedin']['in_progress'] = False
            self.send_error_page("LinkedIn", str(e))

    def handle_instagram_callback(self, parsed_path):
        """Handle Instagram OAuth callback"""
        params = parse_qs(parsed_path.query)

        if 'error' in params:
            oauth_status['instagram']['error'] = f"Authorization denied: {params['error'][0]}"
            oauth_status['instagram']['in_progress'] = False
            self.send_error_page("Instagram", oauth_status['instagram']['error'])
            return

        if 'code' not in params or 'state' not in params:
            oauth_status['instagram']['error'] = "Missing code or state parameter"
            oauth_status['instagram']['in_progress'] = False
            self.send_error_page("Instagram", oauth_status['instagram']['error'])
            return

        code = params['code'][0]
        state = params['state'][0]

        try:
            from auth.oauth_manager import oauth_manager

            # Get stored credentials
            app_id = oauth_status['instagram'].get('app_id')
            app_secret = oauth_status['instagram'].get('app_secret')

            if not app_id or not app_secret:
                oauth_status['instagram']['error'] = "Instagram requires app credentials to complete linking"
                oauth_status['instagram']['in_progress'] = False
                self.send_error_page("Instagram", "Please provide Instagram App ID and Secret to complete linking")
                return

            # Exchange code for token
            result = oauth_manager.exchange_instagram_code(
                code=code,
                client_id=app_id,
                client_secret=app_secret,
                redirect_uri="http://localhost:5000/instagram_callback",
                state=state
            )

            oauth_status['instagram']['success'] = True
            oauth_status['instagram']['in_progress'] = False
            self.send_success_page("Instagram")

        except Exception as e:
            oauth_status['instagram']['error'] = str(e)
            oauth_status['instagram']['in_progress'] = False
            self.send_error_page("Instagram", str(e))

    def send_success_page(self, platform):
        """Send HTML success page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Success!</title>
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
                    padding: 60px 40px;
                    border-radius: 16px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 500px;
                }}
                .icon {{ font-size: 80px; margin-bottom: 20px; }}
                h1 {{ color: #10b981; margin: 0 0 15px 0; font-size: 32px; }}
                p {{ color: #6b7280; font-size: 18px; line-height: 1.6; }}
                .note {{ margin-top: 30px; padding: 20px; background: #f0fdf4; border-radius: 8px; color: #166534; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">🎉</div>
                <h1>{platform} Account Linked!</h1>
                <p>Your {platform} account has been successfully connected.</p>
                <div class="note">
                    <strong>✓ You can now close this window</strong><br>
                    Return to the app to see your linked account
                </div>
            </div>
            <script>
                setTimeout(() => window.close(), 3000);
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def send_error_page(self, platform, error):
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
                    padding: 60px 40px;
                    border-radius: 16px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 500px;
                }}
                .icon {{ font-size: 80px; margin-bottom: 20px; }}
                h1 {{ color: #ef4444; margin: 0 0 15px 0; font-size: 32px; }}
                p {{ color: #6b7280; font-size: 16px; line-height: 1.6; }}
                .error {{ margin-top: 20px; padding: 20px; background: #fee2e2; border-radius: 8px; color: #991b1b; font-family: monospace; font-size: 14px; word-break: break-word; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">❌</div>
                <h1>{platform} Authorization Failed</h1>
                <p>There was an error linking your account.</p>
                <div class="error">{error}</div>
                <p style="margin-top: 20px;">Please close this window and try again.</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())


# Global server instance
_oauth_server = None
_server_thread = None


def start_oauth_server():
    """Start the OAuth callback server if not already running"""
    global _oauth_server, _server_thread

    if _oauth_server is not None:
        return True  # Already running

    try:
        _oauth_server = HTTPServer(('', 5000), OAuthCallbackHandler)
        _server_thread = threading.Thread(
            target=_oauth_server.serve_forever,
            daemon=True
        )
        _server_thread.start()
        time.sleep(0.5)  # Give server time to start
        return True
    except Exception as e:
        print(f"Failed to start OAuth server: {e}")
        return False


def link_twitter_account(client_id, client_secret):
    """
    Start Twitter OAuth flow with one click
    Returns: (success, auth_url, error_message)
    """
    # Start server if not running
    if not start_oauth_server():
        return False, None, "Failed to start OAuth server"

    # Reset status and store credentials
    oauth_status['twitter'] = {
        'success': False,
        'error': None,
        'in_progress': True,
        'client_id': client_id,
        'client_secret': client_secret
    }

    try:
        # Generate auth URL
        auth_data = oauth_manager.get_twitter_auth_url(
            client_id=client_id,
            redirect_uri="http://localhost:5000/twitter_callback"
        )

        auth_url = auth_data['auth_url']

        # Open browser
        try:
            subprocess.run(['open', auth_url], check=False)
        except:
            pass  # Browser opening is optional

        return True, auth_url, None

    except Exception as e:
        oauth_status['twitter']['in_progress'] = False
        return False, None, str(e)


def get_oauth_status(platform):
    """Get current OAuth status for a platform"""
    return oauth_status.get(platform, {'success': False, 'error': None, 'in_progress': False})


def reset_oauth_status(platform):
    """Reset OAuth status for a platform"""
    oauth_status[platform] = {'success': False, 'error': None, 'in_progress': False}


def link_linkedin_account(client_id, client_secret):
    """
    Start LinkedIn OAuth flow with one click
    Returns: (success, auth_url, error_message)
    """
    # Start server if not running
    if not start_oauth_server():
        return False, None, "Failed to start OAuth server"

    # Reset status and store credentials
    oauth_status['linkedin'] = {
        'success': False,
        'error': None,
        'in_progress': True,
        'client_id': client_id,
        'client_secret': client_secret
    }

    try:
        # Generate auth URL
        auth_data = oauth_manager.get_linkedin_auth_url(
            client_id=client_id,
            redirect_uri="http://localhost:5000/linkedin_callback"
        )

        auth_url = auth_data['auth_url']

        # Open browser
        try:
            subprocess.run(['open', auth_url], check=False)
        except:
            pass

        return True, auth_url, None

    except Exception as e:
        oauth_status['linkedin']['in_progress'] = False
        return False, None, str(e)


def link_instagram_account(app_id, app_secret):
    """
    Start Instagram OAuth flow with one click
    Returns: (success, auth_url, error_message)
    """
    # Start server if not running
    if not start_oauth_server():
        return False, None, "Failed to start OAuth server"

    # Reset status and store credentials
    oauth_status['instagram'] = {
        'success': False,
        'error': None,
        'in_progress': True,
        'app_id': app_id,
        'app_secret': app_secret
    }

    try:
        # Generate auth URL
        auth_data = oauth_manager.get_instagram_auth_url(
            client_id=app_id,
            redirect_uri="http://localhost:5000/instagram_callback"
        )

        auth_url = auth_data['auth_url']

        # Open browser
        try:
            subprocess.run(['open', auth_url], check=False)
        except:
            pass

        return True, auth_url, None

    except Exception as e:
        oauth_status['instagram']['in_progress'] = False
        return False, None, str(e)


def link_substack_account(api_key, publication_id):
    """
    Link Substack account using API key (not OAuth)
    Returns: (success, error_message)
    """
    try:
        result = oauth_manager.link_substack_api_key(api_key, publication_id)
        return True, None
    except Exception as e:
        return False, str(e)
