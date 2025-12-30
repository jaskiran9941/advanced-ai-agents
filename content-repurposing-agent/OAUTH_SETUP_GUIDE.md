# OAuth Setup Guide - Social Media Account Linking

This guide explains how to set up OAuth for each social media platform so users can link their accounts and publish content automatically.

## Overview

The Content Repurposing Agent supports publishing to:
- **LinkedIn** - OAuth 2.0
- **Twitter/X** - OAuth 2.0 with PKCE
- **Instagram** - OAuth 2.0 via Facebook Graph API
- **Substack** - API Key based

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Streamlit │ ───> │ OAuth Manager│ ───> │ Platform APIs   │
│      UI     │      │              │      │ (LinkedIn, etc) │
└─────────────┘      └──────────────┘      └─────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ Token Storage│
                    │ (JSON file)  │
                    └──────────────┘
```

## Setup Instructions

### 1. LinkedIn OAuth Setup

**Step 1: Create LinkedIn App**

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Click "Create app"
3. Fill in app details:
   - App name: "Content Repurposing Agent"
   - LinkedIn Page: Select or create a company page
   - Privacy policy URL: Your privacy policy
   - App logo: Upload logo (optional)

**Step 2: Configure OAuth Settings**

1. Go to "Auth" tab
2. Add Redirect URLs:
   ```
   http://localhost:8501/linkedin_callback
   https://yourdomain.com/linkedin_callback  (for production)
   ```
3. Request access to products:
   - Sign In with LinkedIn using OpenID Connect
   - Share on LinkedIn

**Step 3: Get Credentials**

1. Copy your **Client ID**
2. Copy your **Client Secret**
3. Note the required scopes:
   - `w_member_social` - Post on behalf of user
   - `r_liteprofile` - Access user profile
   - `r_emailaddress` - Access email

**Step 4: Test OAuth Flow**

```python
# In Streamlit UI:
1. Navigate to "Account Linking" page
2. Go to LinkedIn tab
3. Enter Client ID and Client Secret
4. Click "Generate LinkedIn Auth URL"
5. Click the generated link to authorize
6. Copy authorization code from redirect URL
7. Complete the linking process
```

**OAuth Flow:**
```
User → LinkedIn Login → User Approves → Redirect with code →
Exchange code for access_token → Save token → Ready to publish!
```

---

### 2. Twitter/X OAuth Setup

**Step 1: Create Twitter App**

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Apply for developer access (if needed)
3. Create a new Project and App
4. App details:
   - App name: "Content Repurposing Agent"
   - Description: "Multi-platform content publishing"
   - Website: Your website URL

**Step 2: Configure OAuth 2.0**

1. Go to app settings → "User authentication settings"
2. Enable OAuth 2.0
3. Type of App: Web App
4. Callback URLs:
   ```
   http://localhost:8501/twitter_callback
   ```
5. Website URL: Your website
6. Enable PKCE (required for public clients)

**Step 3: Set Permissions**

Required scopes:
- `tweet.read` - Read tweets
- `tweet.write` - Post tweets
- `users.read` - Access user profile
- `offline.access` - Refresh token support

**Step 4: Get Credentials**

1. Copy your **Client ID**
2. Copy your **Client Secret**
3. Save for use in Streamlit UI

**OAuth Flow with PKCE:**
```
Generate code_verifier → Create code_challenge →
User authorizes → Get authorization code →
Exchange code + verifier for tokens → Save access & refresh tokens
```

**Token Refresh:**
Twitter access tokens expire after 2 hours. Use the refresh token to get a new access token:
```python
oauth_manager.refresh_token('twitter')
```

---

### 3. Instagram OAuth Setup

**Important:** Instagram requires a Facebook App and Instagram Business/Creator account.

**Step 1: Create Facebook App**

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click "Create App"
3. Use case: "Other"
4. App type: "Business"
5. Fill in app details

**Step 2: Add Instagram Product**

1. In app dashboard, click "Add Product"
2. Select "Instagram Graph API"
3. Complete setup

**Step 3: Configure OAuth**

1. Go to Facebook Login → Settings
2. Add Redirect URIs:
   ```
   http://localhost:8501/instagram_callback
   ```
3. Enable Instagram permissions:
   - `instagram_basic` - Access basic profile
   - `instagram_content_publish` - Publish content
   - `pages_show_list` - Access page info

**Step 4: Convert Instagram Account**

Instagram API only works with Business/Creator accounts:
1. Open Instagram app
2. Go to Settings → Account
3. Switch to Professional Account
4. Choose Business or Creator

**Step 5: Connect Facebook Page**

1. Link Instagram to a Facebook Page
2. The Facebook Page must be associated with your app

**Step 6: Get Credentials**

1. Copy **App ID** (Facebook App ID)
2. Copy **App Secret**
3. Note your Instagram Business Account ID

**OAuth Flow:**
```
Facebook OAuth → User approves → Short-lived token →
Exchange for long-lived token (60 days) → Save token
```

**Note:** Instagram tokens expire after 60 days and must be refreshed.

---

### 4. Substack Setup (API Key)

Substack uses API keys instead of OAuth.

**Step 1: Access Substack Settings**

1. Log into your Substack dashboard
2. Go to Settings

**Step 2: Generate API Key**

Note: As of 2024, Substack's API is limited. Check [Substack Documentation](https://substack.com/api) for latest status.

Alternative approaches:
1. Use Substack's email posting feature
2. Use browser automation (Selenium/Playwright)
3. Wait for official API access

**For now (Mock Implementation):**
```python
# In Streamlit UI:
1. Navigate to Substack tab
2. Enter any API key (will be used when API is available)
3. Enter your publication ID from URL
```

**Publication ID:**
Found in your Substack dashboard URL:
```
https://yourname.substack.com/publish/home
                     ^^^^^^^^
              Your publication name
```

---

## Security Best Practices

### 1. Token Storage

**Development (Current):**
- Tokens stored in `data/user_tokens.json`
- File-based storage with restricted permissions

**Production (Recommended):**
```python
# Use a secure vault
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Google Secret Manager
```

### 2. Token Encryption

For production, encrypt tokens at rest:
```python
from cryptography.fernet import Fernet

# Generate key (do this once, store securely)
key = Fernet.generate_key()

# Encrypt token before saving
cipher = Fernet(key)
encrypted_token = cipher.encrypt(token.encode())

# Decrypt when retrieving
decrypted_token = cipher.decrypt(encrypted_token).decode()
```

### 3. Environment Variables

Store app credentials in environment variables, never in code:
```bash
# .env file
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
TWITTER_CLIENT_ID=your_client_id
TWITTER_CLIENT_SECRET=your_client_secret
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
```

### 4. HTTPS for Production

Always use HTTPS in production:
```python
# Redirect URIs should use HTTPS
redirect_uri = "https://yourdomain.com/oauth/callback"
```

### 5. State Parameter Validation

Always validate state parameter to prevent CSRF:
```python
# Already implemented in OAuthManager
if state != stored_state:
    raise ValueError("Invalid state - possible CSRF attack")
```

---

## Usage in the App

### 1. Check if Account is Linked

```python
from auth.oauth_manager import oauth_manager

if oauth_manager.is_linked('linkedin'):
    # Ready to publish
    post_to_linkedin(content)
else:
    # Show "Link Account" message
    st.warning("Please link your LinkedIn account first")
```

### 2. Get Access Token

```python
token_data = oauth_manager.get_token('twitter')
if token_data:
    access_token = token_data['access_token']
    # Use token to post
```

### 3. Handle Token Expiration

```python
token_data = oauth_manager.get_token('instagram')
if not token_data:
    # Token expired or not linked
    st.error("Please re-link your Instagram account")
elif oauth_manager.refresh_token('instagram'):
    # Token refreshed successfully
    token_data = oauth_manager.get_token('instagram')
```

---

## Testing OAuth Flow

### Local Testing

1. Start Streamlit app:
```bash
python3 -m streamlit run ui/app.py
```

2. Navigate to http://localhost:8501
3. Click "Account Linking" in sidebar
4. Follow platform-specific instructions

### Testing Without Real Accounts

Use mock mode (already implemented):
```python
# In social_tools.py, functions automatically use mocks
# when credentials are not configured

result = post_to_linkedin(content)
if result.get('mock'):
    print("Mock posting - no real account needed")
```

---

## Troubleshooting

### Common Issues

**1. "Invalid redirect_uri"**
- Ensure redirect URI in app settings exactly matches the one you're using
- Check for trailing slashes: `http://localhost:8501/callback` vs `http://localhost:8501/callback/`

**2. "Invalid state parameter"**
- State may have expired (restart OAuth flow)
- Check that state is copied correctly

**3. "Insufficient permissions"**
- Verify all required scopes are enabled in app settings
- For Instagram, ensure account is Business/Creator type

**4. "Token expired"**
- Implement token refresh
- For platforms without refresh tokens, prompt user to re-authenticate

**5. "Rate limit exceeded"**
- Most platforms have rate limits (e.g., LinkedIn: 100 posts/day)
- Implement exponential backoff
- Cache responses when possible

---

## Platform-Specific Limits

### LinkedIn
- 100 posts per person per day
- 25 posts per organization per day
- Images: Max 10MB, formats: PNG, JPG, GIF

### Twitter/X
- Free tier: Limited to basic posting
- Paid API: Higher rate limits
- Tweet length: 280 characters (4000 for subscribers)
- Images: Max 5MB each, up to 4 images per tweet

### Instagram
- 25 API requests per user per hour
- 200 API requests per user per day
- Images: Min 320px, max 1080px
- Requires Business/Creator account

### Substack
- No official public API yet
- Email posting available
- Check latest API documentation

---

## Next Steps

1. **For Development:**
   - Use mock mode to test without real credentials
   - Test UI flow with dummy data

2. **For Production:**
   - Create apps on each platform
   - Implement proper token encryption
   - Use secret management service
   - Set up HTTPS
   - Implement token refresh logic
   - Add error handling and retries

3. **Advanced Features:**
   - Analytics integration
   - Scheduled posting
   - Content calendar
   - Multi-account support
   - Team collaboration

---

## Resources

- [LinkedIn OAuth Documentation](https://docs.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [Twitter OAuth 2.0 Guide](https://developer.twitter.com/en/docs/authentication/oauth-2-0)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/)
- [OAuth 2.0 Specification](https://oauth.net/2/)
