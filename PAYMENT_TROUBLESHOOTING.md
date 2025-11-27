# Payment & QR Code Troubleshooting Guide

## What Happens When You Click "Pay with KHQR"

1. **QR Code Generation**
   - Bot calls `generate_qr_data()` which uses your Bakong token
   - Creates a unique MD5 hash for this payment
   - Generates a styled QR image with amount displayed
   - Sends the QR image to you in Telegram

2. **Payment Scanning & Processing**
   - You scan the QR with your mobile banking app
   - You complete payment in your bank
   - The bot starts checking payment status every 5 seconds
   - Checks for up to 10 minutes (120 attempts)

3. **Payment Confirmation**
   - Once payment is detected, the bot:
     - Deletes the QR message
     - Sends you order confirmation with account details
     - Updates inventory (stock - qty)
     - Records transaction
     - Sends admin notification (optional)

## If Payment Shows Nothing After Scanning

### Possible Causes:

1. **QR Code Issue**
   - ❌ QR not generated properly
   - ❌ QR image not readable
   - ✅ Check bot logs: Look for `[OK] Using local file storage` message

2. **Bakong Token Problem**
   - ❌ Invalid BAKONG_TOKEN in .env
   - ❌ Token expired or revoked
   - ✅ Check bot logs: Look for `[KHQR CHECK]` messages

3. **Payment Not Detected**
   - ❌ Payment made to wrong Bakong account
   - ❌ Bakong API not responding
   - ❌ Check timeout (10 minutes max)
   - ✅ Check bot logs: Look for `[PAYMENT CHECK]` messages

4. **Bot Issues**
   - ❌ Bot crashed after QR was sent
   - ❌ Network connection lost
   - ✅ Check bot is still running and connected

## How to Debug

### Step 1: Check Bot Logs
Run the bot and watch the terminal for these log messages:

```
[OK] Using local file storage              ← Bot started OK
[OK] Store Bot Final V33 Running...         ← Bot is ready
INFO:httpx:HTTP Request: ... "HTTP/1.1 200 OK"  ← Bot is connected to Telegram
[PAYMENT CHECK] Started for md5=...         ← Payment loop started
[PAYMENT CHECK] Attempt 1: Response = ...   ← Checking payment status
[KHQR CHECK] MD5=..., Result=PAID           ← Payment confirmed!
[PAYMENT SUCCESS] ...                       ← Processing confirmed payment
```

### Step 2: Enable Test Mode (No Real Payment Needed)

If your Bakong token is not working, test with fake payments:

**Edit .env:**
```
USE_MONGODB=false
# Comment out or remove BAKONG_TOKEN to use test mode
# BAKONG_TOKEN=your_token
```

**In test mode:**
- QR code will show a simple test code
- After 5 seconds, payment auto-confirms
- You can test the flow without real money

### Step 3: Check .env Configuration

Make sure your `.env` has:
```
BOT_TOKEN=your_bot_token
BAKONG_TOKEN=your_bakong_token
BAKONG_ACCOUNT=your_account
MERCHANT_NAME=your_merchant_name
ADMIN_ID=your_id
ADMIN_USERNAME=@your_username
USE_MONGODB=false
```

### Step 4: Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| QR doesn't appear | Bot crashed | Check terminal for errors |
| QR appears but no confirmation | Payment not sent | Verify Bakong account matches |
| QR appears then disappears | Timeout after 10 min | Scan and pay faster |
| No log messages | Bot not running | Run: `python storebot.py` |
| HTTP 409 error | Previous webhook stuck | Safe to ignore, bot retries |

## Testing Payment Flow

### Test 1: Check QR Generation
```python
from storebot import generate_qr_data, create_styled_qr
qr_text, md5 = generate_qr_data(10.00)  # $10
filename = create_styled_qr(qr_text, 10.00)
print(f"QR saved as: {filename}")
# Check if image exists and is readable
```

### Test 2: Manual Payment Check
```python
from storebot import safe_check_payment
result = safe_check_payment("your_md5_hash")
print(f"Payment status: {result}")
```

### Test 3: Run Bot in Test Mode
1. Edit `.env`: Remove or comment out `BAKONG_TOKEN`
2. Run: `python storebot.py`
3. Click Pay → QR auto-confirms after 5 seconds
4. Check if confirmation message appears

## If It Still Doesn't Work

1. **Restart the bot** after fixing .env
2. **Check bot token** is correct (ask @BotFather)
3. **Verify Bakong token** is valid (check Bakong API docs)
4. **Check firewall** - bot needs internet access
5. **Check disk space** - QR images need space to save

## Log File Location

Bot logs are printed to terminal. To save logs:
```powershell
python storebot.py > bot.log 2>&1
```

Then check `bot.log` for detailed error messages.

## Next Steps

- **If QR works**: Payment confirmation should appear in 1-2 minutes
- **If QR broken**: Check Bakong token and try test mode
- **For Railway deployment**: Keep this troubleshooting guide updated with your findings
