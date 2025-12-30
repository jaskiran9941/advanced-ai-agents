"""
OAuth Manager for Social Media Account Linking

Handles OAuth flows for:
- LinkedIn (OAuth 2.0)
- Twitter/X (OAuth 2.0)
- Instagram (via Facebook Graph API)
- Substack (API key based)
"""
import secrets
import json
import hashlib
import base64
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from utils.logger import setup_logger
import requests

logger = setup_logger("oauth_manager")

# Database file for storing tokens
TOKENS_DB_PATH = Path("data/user_tokens.json")
STATE_STORAGE_PATH = Path("data/oauth_state.json")
TOKENS_DB_PATH.parent.mkdir(exist_ok=True)

class OAuthManager:
    """Manages OAuth flows and token storage for social media platforms."""

    def __init__(self):
        self.tokens = self._load_tokens()
        self.state_storage = self._load_state()  # Store OAuth state for CSRF protection

    def _load_tokens(self) -> Dict[str, Any]:
        """Load saved OAuth tokens from disk."""
        if TOKENS_DB_PATH.exists():
            try:
                with open(TOKENS_DB_PATH, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load tokens: {e}")
                return {}
        return {}

    def _save_tokens(self):
        """Save OAuth tokens to disk."""
        try:
            with open(TOKENS_DB_PATH, 'w') as f:
                json.dump(self.tokens, f, indent=2)
            logger.info("Tokens saved successfully")
        except Exception as e:
            logger.error(f"Failed to save tokens: {e}")

    def _load_state(self) -> Dict[str, Any]:
        """Load OAuth state from disk."""
        if STATE_STORAGE_PATH.exists():
            try:
                with open(STATE_STORAGE_PATH, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
                return {}
        return {}

    def _save_state(self):
        """Save OAuth state to disk."""
        try:
            with open(STATE_STORAGE_PATH, 'w') as f:
                json.dump(self.state_storage, f, indent=2)
            logger.info("OAuth state saved successfully")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    # =========================================================================
    # LINKEDIN OAUTH
    # =========================================================================

    def get_linkedin_auth_url(self, client_id: str, redirect_uri: str) -> Dict[str, str]:
        """
        Generate LinkedIn OAuth authorization URL.

        Args:
            client_id: LinkedIn app client ID
            redirect_uri: OAuth redirect URI (must match app settings)

        Returns:
            Dict with auth_url and state
        """
        state = secrets.token_urlsafe(32)
        self.state_storage['linkedin'] = state
        self._save_state()

        auth_url = (
            f"https://www.linkedin.com/oauth/v2/authorization?"
            f"response_type=code&"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"state={state}&"
            f"scope=w_member_social,openid,profile"
        )

        return {
            "auth_url": auth_url,
            "state": state,
            "platform": "linkedin"
        }

    def exchange_linkedin_code(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Exchange LinkedIn authorization code for access token.

        Args:
            code: Authorization code from OAuth callback
            client_id: LinkedIn app client ID
            client_secret: LinkedIn app client secret
            redirect_uri: OAuth redirect URI
            state: State parameter for CSRF validation

        Returns:
            Token data with access_token, expires_in, etc.
        """
        # Validate state
        if state != self.state_storage.get('linkedin'):
            raise ValueError("Invalid state parameter - possible CSRF attack")

        try:
            response = requests.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": client_id,
                    "client_secret": client_secret
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()

            token_data = response.json()

            # Save token with metadata
            self.tokens['linkedin'] = {
                "access_token": token_data['access_token'],
                "expires_in": token_data['expires_in'],
                "expires_at": (datetime.now() + timedelta(seconds=token_data['expires_in'])).isoformat(),
                "linked_at": datetime.now().isoformat(),
                "platform": "linkedin"
            }
            self._save_tokens()

            logger.info("LinkedIn account linked successfully")
            return self.tokens['linkedin']

        except Exception as e:
            logger.error(f"LinkedIn OAuth failed: {e}")
            raise

    # =========================================================================
    # TWITTER/X OAUTH
    # =========================================================================

    def get_twitter_auth_url(self, client_id: str, redirect_uri: str) -> Dict[str, str]:
        """
        Generate Twitter OAuth 2.0 authorization URL.

        Args:
            client_id: Twitter app client ID
            redirect_uri: OAuth redirect URI

        Returns:
            Dict with auth_url and state
        """
        state = secrets.token_urlsafe(32)
        code_verifier = secrets.token_urlsafe(32)

        # Compute code_challenge for PKCE (S256 method)
        # code_challenge = base64url(sha256(code_verifier))
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('ascii')).digest()
        ).decode('ascii').rstrip('=')

        self.state_storage['twitter'] = {
            'state': state,
            'code_verifier': code_verifier
        }
        self._save_state()

        auth_url = (
            f"https://twitter.com/i/oauth2/authorize?"
            f"response_type=code&"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"state={state}&"
            f"scope=tweet.read%20tweet.write%20users.read%20offline.access&"
            f"code_challenge={code_challenge}&"
            f"code_challenge_method=S256"
        )

        return {
            "auth_url": auth_url,
            "state": state,
            "platform": "twitter"
        }

    def exchange_twitter_code(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Exchange Twitter authorization code for access token.

        Args:
            code: Authorization code
            client_id: Twitter app client ID
            client_secret: Twitter app client secret
            redirect_uri: OAuth redirect URI
            state: State parameter

        Returns:
            Token data
        """
        twitter_state = self.state_storage.get('twitter', {})
        if state != twitter_state.get('state'):
            raise ValueError("Invalid state parameter")

        try:
            response = requests.post(
                "https://api.twitter.com/2/oauth2/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "code_verifier": twitter_state['code_verifier']
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                auth=(client_id, client_secret)
            )
            response.raise_for_status()

            token_data = response.json()

            self.tokens['twitter'] = {
                "access_token": token_data['access_token'],
                "refresh_token": token_data.get('refresh_token'),
                "expires_in": token_data['expires_in'],
                "expires_at": (datetime.now() + timedelta(seconds=token_data['expires_in'])).isoformat(),
                "linked_at": datetime.now().isoformat(),
                "platform": "twitter"
            }
            self._save_tokens()

            logger.info("Twitter account linked successfully")
            return self.tokens['twitter']

        except Exception as e:
            logger.error(f"Twitter OAuth failed: {e}")
            raise

    # =========================================================================
    # INSTAGRAM (via Facebook Graph API)
    # =========================================================================

    def get_instagram_auth_url(self, client_id: str, redirect_uri: str) -> Dict[str, str]:
        """
        Generate Instagram (Facebook) OAuth URL.

        Note: Instagram requires Facebook Graph API

        Args:
            client_id: Facebook app ID
            redirect_uri: OAuth redirect URI

        Returns:
            Dict with auth_url and state
        """
        state = secrets.token_urlsafe(32)
        self.state_storage['instagram'] = state
        self._save_state()

        auth_url = (
            f"https://www.facebook.com/v18.0/dialog/oauth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"state={state}&"
            f"scope=instagram_basic,instagram_content_publish"
        )

        return {
            "auth_url": auth_url,
            "state": state,
            "platform": "instagram"
        }

    def exchange_instagram_code(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        state: str
    ) -> Dict[str, Any]:
        """Exchange Instagram/Facebook code for access token."""
        if state != self.state_storage.get('instagram'):
            raise ValueError("Invalid state parameter")

        try:
            # Get short-lived token
            response = requests.get(
                "https://graph.facebook.com/v18.0/oauth/access_token",
                params={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri
                }
            )
            response.raise_for_status()
            short_token = response.json()['access_token']

            # Exchange for long-lived token
            long_response = requests.get(
                "https://graph.facebook.com/v18.0/oauth/access_token",
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "fb_exchange_token": short_token
                }
            )
            long_response.raise_for_status()
            token_data = long_response.json()

            self.tokens['instagram'] = {
                "access_token": token_data['access_token'],
                "expires_in": token_data['expires_in'],
                "expires_at": (datetime.now() + timedelta(seconds=token_data['expires_in'])).isoformat(),
                "linked_at": datetime.now().isoformat(),
                "platform": "instagram"
            }
            self._save_tokens()

            logger.info("Instagram account linked successfully")
            return self.tokens['instagram']

        except Exception as e:
            logger.error(f"Instagram OAuth failed: {e}")
            raise

    # =========================================================================
    # SUBSTACK (API Key Based)
    # =========================================================================

    def link_substack_api_key(self, api_key: str, publication_id: str) -> Dict[str, Any]:
        """
        Link Substack account using API key.

        Note: Substack uses API keys, not OAuth

        Args:
            api_key: Substack API key
            publication_id: Substack publication ID

        Returns:
            Success data
        """
        # Verify API key by making a test request
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Test the API key (you'd need actual Substack API endpoint)
            # For now, just save it

            self.tokens['substack'] = {
                "api_key": api_key,
                "publication_id": publication_id,
                "linked_at": datetime.now().isoformat(),
                "platform": "substack"
            }
            self._save_tokens()

            logger.info("Substack account linked successfully")
            return self.tokens['substack']

        except Exception as e:
            logger.error(f"Substack linking failed: {e}")
            raise

    # =========================================================================
    # TOKEN MANAGEMENT
    # =========================================================================

    def get_token(self, platform: str) -> Optional[Dict[str, Any]]:
        """Get token for a platform."""
        token_data = self.tokens.get(platform)

        if not token_data:
            return None

        # Check if token is expired
        if 'expires_at' in token_data:
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            if datetime.now() >= expires_at:
                logger.warning(f"{platform} token expired")
                return None

        return token_data

    def is_linked(self, platform: str) -> bool:
        """Check if a platform is linked and has valid token."""
        token = self.get_token(platform)
        return token is not None

    def unlink_platform(self, platform: str) -> bool:
        """Unlink a platform by removing its tokens."""
        if platform in self.tokens:
            del self.tokens[platform]
            self._save_tokens()
            logger.info(f"{platform} account unlinked")
            return True
        return False

    def get_all_linked_platforms(self) -> Dict[str, Dict[str, Any]]:
        """Get all linked platforms with their metadata."""
        linked = {}
        for platform, data in self.tokens.items():
            if self.is_linked(platform):
                # Return safe subset (no sensitive tokens)
                linked[platform] = {
                    "platform": platform,
                    "linked_at": data.get("linked_at"),
                    "expires_at": data.get("expires_at"),
                    "is_valid": True
                }
        return linked

    def refresh_token(self, platform: str) -> bool:
        """
        Refresh access token for platforms that support it.

        Currently supports: Twitter
        """
        if platform == "twitter":
            token_data = self.tokens.get('twitter')
            if not token_data or 'refresh_token' not in token_data:
                return False

            # Implement Twitter token refresh
            # This would make a request to Twitter's token endpoint
            # with the refresh_token to get a new access_token
            pass

        return False


# Singleton instance
oauth_manager = OAuthManager()
