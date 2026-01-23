#!/usr/bin/env python3
"""Gmail OAuth setup wizard.

This script helps you set up Gmail API credentials and obtain OAuth tokens.
"""

import os
import sys
import pickle
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def print_instructions() -> None:
    """Print setup instructions."""
    print("=" * 70)
    print("Gmail API Setup Wizard")
    print("=" * 70)
    print()
    print("Before running this script, you need to:")
    print()
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project (or select existing)")
    print("3. Enable the Gmail API:")
    print("   - Navigate to 'APIs & Services' > 'Library'")
    print("   - Search for 'Gmail API'")
    print("   - Click 'Enable'")
    print("4. Create OAuth 2.0 credentials:")
    print("   - Navigate to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'OAuth client ID'")
    print("   - Application type: 'Desktop app'")
    print("   - Download the credentials JSON file")
    print("5. Save the downloaded file as 'credentials.json' in the project root")
    print()
    print("=" * 70)
    print()


def check_credentials_file() -> str:
    """Check if credentials.json exists.

    Returns:
        Path to credentials file

    Raises:
        FileNotFoundError: If credentials.json not found
    """
    creds_file = project_root / "credentials.json"

    if not creds_file.exists():
        print("ERROR: credentials.json not found!")
        print()
        print("Please download your OAuth credentials from Google Cloud Console")
        print("and save them as 'credentials.json' in the project root directory.")
        print()
        print(f"Expected location: {creds_file}")
        print()
        raise FileNotFoundError("credentials.json not found")

    print(f"✓ Found credentials file: {creds_file}")
    return str(creds_file)


def authenticate(credentials_file: str, token_file: str) -> Credentials:
    """Authenticate with Gmail API.

    Args:
        credentials_file: Path to credentials JSON
        token_file: Path to save token

    Returns:
        OAuth credentials
    """
    creds = None

    # Load existing token if available
    if os.path.exists(token_file):
        print(f"Loading existing token from {token_file}...")
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    # Refresh or create new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print()
            print("Starting OAuth flow...")
            print("A browser window will open. Please authorize the application.")
            print()
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials
        print(f"Saving token to {token_file}...")
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    print("✓ Authentication successful!")
    return creds


def test_connection(creds: Credentials) -> None:
    """Test Gmail API connection.

    Args:
        creds: OAuth credentials
    """
    from googleapiclient.discovery import build

    print()
    print("Testing Gmail API connection...")

    try:
        service = build('gmail', 'v1', credentials=creds)

        # Get profile info
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress')
        total_messages = profile.get('messagesTotal', 0)

        print("✓ Connection successful!")
        print()
        print(f"  Email: {email}")
        print(f"  Total messages: {total_messages}")
        print()

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        raise


def main() -> None:
    """Main setup flow."""
    print_instructions()

    try:
        # Check for credentials file
        credentials_file = check_credentials_file()

        # Set token file path
        token_file = str(project_root / "token.json")

        # Authenticate
        creds = authenticate(credentials_file, token_file)

        # Test connection
        test_connection(creds)

        print("=" * 70)
        print("Setup Complete!")
        print("=" * 70)
        print()
        print("Your Gmail API is now configured.")
        print()
        print("Next steps:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your Slack tokens and AI API keys in .env")
        print("3. Run: python src/main.py")
        print()

    except FileNotFoundError as e:
        print()
        print("Setup failed. Please follow the instructions above.")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
