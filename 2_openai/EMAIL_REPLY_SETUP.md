# Email Reply System - Setup Instructions

## What You Get

A **turnkey email reply system** that automatically responds to prospect emails using AI agents. No server required - runs entirely in your Jupyter notebook!

## Quick Start (3 Steps)

### Step 1: Get Your Email App Password

Choose your email provider:

#### For Gmail:
1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not already enabled)
3. Search for "**App passwords**"
4. Click "**Generate**" and select "**Mail**"
5. Copy the 16-character password (no spaces)

#### For iCloud:
1. Go to https://appleid.apple.com
2. Sign in → **App-Specific Passwords**
3. Click "**Generate password**" and label it "Mail Access"
4. Copy the password

### Step 2: Update Your .env File

Add these 3 lines to your `.env` file in the project root:

```bash
IMAP_SERVER=imap.gmail.com
IMAP_EMAIL=your-email@gmail.com
IMAP_PASSWORD=your-16-char-app-password-here
```

**For iCloud users:** Change `IMAP_SERVER` to `imap.mail.me.com`

### Step 3: Run the Notebook

1. Open `2_lab2_with_replies.ipynb` in Jupyter
2. Run all cells from top to bottom
3. When you reach "Part 4: Email Reply Capability", you're ready!
4. Test with the manual reply cell first
5. Then start the monitoring loop

## How It Works

```
Incoming Email → IMAP Poll (every 60s) → Reply Analyzer Agent
                                               ↓
                                    ┌──────────┴──────────┐
                                    ↓                     ↓
                            Interested?            Objection/Question?
                                    ↓                     ↓
                        Interested Agent      Objection/Question Agent
                                    ↓                     ↓
                                    └──────────┬──────────┘
                                               ↓
                                   Conversation Manager
                                               ↓
                                       Send Reply Email
```

## Testing

### Test 1: Manual Reply (Recommended First)
```python
# In the test cell, uncomment this line:
await process_reply(test_reply['from'], test_reply['subject'], test_reply['body'])
```

### Test 2: Limited Monitoring
```python
# Runs 5 checks, then stops
await monitor_emails(check_interval=30, max_iterations=5)
```

### Test 3: Send Yourself an Email
1. Send an email to your `SENDER_EMAIL` address
2. Watch the notebook console for activity
3. Check OpenAI traces: https://platform.openai.com/traces

## Troubleshooting

### "IMAP_PASSWORD not set"
- ✅ Check `.env` file has `IMAP_PASSWORD=...`
- ✅ Restart notebook kernel
- ✅ Run `load_dotenv(override=True)` again

### "Authentication failed"
- ✅ Verify app password is correct (no spaces)
- ✅ For Gmail: Ensure 2FA is enabled first
- ✅ For iCloud: Generate a new app-specific password

### "No new messages" but you sent one
- ✅ Check email went to correct inbox
- ✅ Verify email is **unread**
- ✅ Check spam folder
- ✅ Wait 60 seconds for next poll

### Emails not being processed
- ✅ Verify `IMAP_EMAIL` matches your actual email
- ✅ Check `IMAP_SERVER` is correct for your provider
- ✅ Look for error messages in notebook output

## Features

✅ **No Server Required** - Runs in notebook using IMAP polling  
✅ **Multi-Agent System** - Different agents for different reply types  
✅ **Sentiment Analysis** - Automatically routes to appropriate responder  
✅ **Conversation History** - Maintains context across emails  
✅ **OpenAI Traces** - Full visibility into agent decisions  
✅ **Easy Testing** - Test with manual replies before going live  

## File Structure

After running, you'll see:

```
2_openai/
├── 2_lab2_with_replies.ipynb    ← Your new notebook
├── EMAIL_REPLY_SETUP.md          ← This file
└── conversations/                 ← Created automatically
    └── prospect_at_company.json   ← Conversation histories
```

## Security Notes

- ✅ App passwords are safer than real passwords
- ✅ Never commit `.env` file to git
- ✅ Revoke app passwords when done testing
- ✅ Use environment variables in production

## What's Next?

1. **Customize Agent Instructions** - Edit agent prompts to match your style
2. **Add More Agent Types** - Create specialized agents for pricing, technical questions, etc.
3. **Adjust Check Interval** - Change from 60s to whatever works for you
4. **Monitor Traces** - Watch agent decision-making in OpenAI dashboard
5. **Scale Up** - Remove `max_iterations` to run continuously

## Support

If you encounter issues:
1. Check error messages in notebook output
2. Verify `.env` configuration
3. Test IMAP connection separately
4. Check OpenAI traces for agent errors
5. Review conversation history in `conversations/` folder

## Advanced Configuration

### Change Check Frequency
```python
# Check every 30 seconds instead of 60
await monitor_emails(check_interval=30)
```

### Run Indefinitely
```python
# Remove max_iterations for continuous monitoring
await monitor_emails(check_interval=60)
```

### Customize Agent Behavior
Edit the agent `instructions` in the notebook cells to change how they respond.

---

**That's it!** You now have a fully automated email reply system. 🎉

Happy automating! 🚀
