# Security Guidelines

## ⚠️ IMPORTANT: Never Commit Sensitive Data

This repository is configured to protect your sensitive credentials. Please follow these guidelines:

### Files That Are Automatically Ignored

The following files are already in `.gitignore` and will **NOT** be committed:

- `.env` - Contains all API keys
- `data/user_tokens.json` - OAuth access tokens
- `data/oauth_state.json` - OAuth state data
- `data/` directory - All generated data
- Any `*.env` files

### Setup Your Environment

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys to `.env`:**
   - Get your API keys from respective service providers
   - NEVER commit the `.env` file
   - NEVER share your API keys publicly

### API Keys Required

#### For Content Generation:
- `ANTHROPIC_API_KEY` - Claude API (Anthropic)
- `GOOGLE_API_KEY` - Gemini API (Google)
- `OPENAI_API_KEY` - GPT API (OpenAI)

#### For Features:
- `REPLICATE_API_TOKEN` - Image generation
- `SERPAPI_API_KEY` - SEO research

#### For Social Media (OAuth):
Twitter and LinkedIn use OAuth 2.0 - you'll enter credentials in the app UI:
- Twitter: Client ID and Secret from Twitter Developer Portal
- LinkedIn: Client ID and Secret from LinkedIn Developer Portal

### OAuth Token Storage

When you link social media accounts:
- Tokens are stored in `data/user_tokens.json`
- This file is automatically ignored by git
- Delete this file to unlink all accounts

### Before Committing Code

Always verify no sensitive data is committed:

```bash
# Check what will be committed
git status

# Verify .env is ignored
git check-ignore .env

# Verify data directory is ignored
git check-ignore data/

# Search for potential secrets (should return nothing)
grep -r "sk-ant-" . --include="*.py" 2>/dev/null
grep -r "sk-proj-" . --include="*.py" 2>/dev/null
```

### What If I Accidentally Commit Secrets?

If you accidentally commit API keys or tokens:

1. **Immediately revoke the exposed keys** from the service provider
2. Generate new keys
3. Remove from git history:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch <FILE_WITH_SECRET>" \
     --prune-empty --tag-name-filter cat -- --all
   ```
4. Force push: `git push origin --force --all`

### Security Checklist Before Pushing

- [ ] All API keys are in `.env` file only
- [ ] `.env` file is in `.gitignore`
- [ ] No hardcoded credentials in code files
- [ ] `data/` directory is ignored
- [ ] No OAuth tokens in committed files
- [ ] Verified with `git status` and `git diff --cached`

## Support

If you find security vulnerabilities, please report them via GitHub Issues.
