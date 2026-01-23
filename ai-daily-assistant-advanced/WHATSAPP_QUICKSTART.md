# WhatsApp Integration - Quick Start

Get your AI Daily Assistant working on WhatsApp in 10 minutes!

## What You'll Get

Send WhatsApp messages like:
- "What are my unread emails?"
- "Show me emails from john@example.com"
- "Summarize recent emails"

And get instant responses! 📱

## Prerequisites

- ✅ AI Daily Assistant already set up (AI key + Gmail OAuth)
- ✅ WhatsApp on your phone
- ✅ 10 minutes of time

## Step-by-Step Setup

### 1. Install Dependencies (1 minute)

```bash
pip install twilio flask flask-cors
```

### 2. Create Twilio Account (3 minutes)

1. Go to https://www.twilio.com/try-twilio
2. Sign up (you get $15 free credit!)
3. Verify your email and phone

### 3. Connect WhatsApp Sandbox (2 minutes)

1. In Twilio Console, go to:
   **Messaging** → **Try it out** → **Send a WhatsApp message**

2. You'll see instructions like:
   ```
   Send "join <your-code>" to whatsapp:+1-415-523-8886
   ```

3. Open WhatsApp on your phone and send that message
4. You'll get a confirmation!

### 4. Get Your Credentials (1 minute)

Still in Twilio Console:

1. Go to **Account** → **Account Info** (or Dashboard)
2. Copy these:
   - **Account SID** (starts with AC...)
   - **Auth Token** (click to reveal)
3. Note your sandbox number (e.g., +1 415-523-8886)

### 5. Add to .env (1 minute)

Edit `.env` and add:

```bash
# WhatsApp/Twilio Configuration
TWILIO_ACCOUNT_SID=AC1234567890abcdef  # Your Account SID
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886  # Your sandbox number
```

### 6. Start the Webhook Server (1 minute)

In one terminal:

```bash
python3 run_whatsapp.py
```

You should see:
```
WhatsApp Webhook Server Ready!
Webhook endpoint: /webhook/whatsapp
```

### 7. Expose with ngrok (1 minute)

In another terminal:

```bash
# Install ngrok (one time)
brew install ngrok
# Or download from https://ngrok.com/download

# Start ngrok
ngrok http 5000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:5000
```

**Copy that https URL!**

### 8. Configure Twilio Webhook (1 minute)

1. Go back to Twilio Console
2. Navigate to: **Messaging** → **Try it out** → **Send a WhatsApp message**
3. Scroll down to **Sandbox Settings**
4. In "When a message comes in" field, paste:
   ```
   https://your-ngrok-url.ngrok.io/webhook/whatsapp
   ```
   Replace `your-ngrok-url` with your actual ngrok URL!
5. Keep method as **POST**
6. Click **Save**

### 9. Test It! 🎉

Open WhatsApp and send a message to your Twilio sandbox number:

```
What are my unread emails?
```

You should get a response within seconds!

## Example Conversations

```
You: help
Bot: 👋 Welcome to AI Daily Assistant!
     I can help you with your Gmail emails. Try:
     • "What are my unread emails?"
     • "Show me emails from john@example.com"
     ...

You: What are my unread emails?
Bot: *Unread Emails*
     1. 📧 From: john@example.com
        Subject: Meeting tomorrow
        Date: Jan 23, 2026
     ...

You: Show me more details about the first one
Bot: 📧 Email Details
     From: john@example.com
     Subject: Meeting tomorrow
     Message: Hi, can we meet tomorrow...
```

## Troubleshooting

### "Webhook not receiving messages"
- Check ngrok is still running (it stops after 2 hours on free plan)
- Verify webhook URL in Twilio matches your ngrok URL exactly
- Check `run_whatsapp.py` is still running

### "Error: Missing Twilio configuration"
- Make sure you added all three Twilio variables to `.env`
- Restart `run_whatsapp.py` after editing `.env`

### "Bot not responding"
- Check terminal running `run_whatsapp.py` for errors
- Verify Gmail and AI credentials are still valid
- Send "help" to test basic connectivity

## Commands

Send these to the bot:
- `help` - Show help message
- `clear` - Clear your chat history
- Any question about your emails!

## Architecture

```
Your WhatsApp Message
    ↓
Twilio (receives)
    ↓
ngrok (tunnels to localhost)
    ↓
Flask Server (run_whatsapp.py)
    ↓
WhatsApp Handler
    ↓
AI Agent (same as Slack/Streamlit!)
    ↓
Email Tools (searches your Gmail)
    ↓
Response sent back to WhatsApp
```

## Next Steps

### For Development
- ngrok free tier resets URL every restart
- Just update Twilio webhook URL when it changes

### For Production
- Get a real Twilio WhatsApp number (no sandbox)
- Deploy webhook to Heroku/AWS/Google Cloud
- Use proper domain instead of ngrok

## Cost

- **Twilio Free Tier**: $15 credit (lots of messages!)
- **After free tier**: ~$0.005 per message
- **ngrok Free**: Works fine for testing
- **Production WhatsApp**: $0.01-0.05 per conversation

## Files Created

- `src/whatsapp/` - WhatsApp integration code
- `run_whatsapp.py` - Webhook server
- `WHATSAPP_INTEGRATION.md` - Detailed documentation

## Tips

1. **Keep ngrok running** - If it stops, you'll need to update the webhook URL
2. **Test with simple queries first** - "help" or "What are my unread emails?"
3. **Check logs** - The `run_whatsapp.py` terminal shows all activity
4. **Session persistence** - The bot remembers your conversation!

## What's Next?

Try these features:
- Multi-turn conversations (bot remembers context)
- Search emails by sender, date, subject
- Summarize email threads
- Get email counts and stats

Enjoy your WhatsApp email assistant! 🚀📧
