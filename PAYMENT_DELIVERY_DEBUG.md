# Payment Delivery Checklist

When you scan QR code and payment doesn't deliver, follow this checklist:

## Step 1: Check Stock Files Exist

Run this in PowerShell:

```powershell
cd "C:\Users\Reach\OneDrive\Desktop\telegrambot"
Get-ChildItem database/ -Filter "stock_*.txt"
```

You should see files like:
```
stock_1_1M.txt
stock_2_STANDARD.txt
etc.
```

If you don't see any files:
- ❌ Stock files don't exist
- ✅ Add stock using `/addstock` command before testing payment

---

## Step 2: Check Stock File Content

View a stock file:

```powershell
Get-Content database/stock_1_1M.txt
```

Expected format (each account on a new line):
```
email1@example.com,password123,extra_info
email2@example.com,password456,more_data
```

If empty or missing:
- ❌ No accounts in file
- ✅ Add accounts using `/addstock` command

---

## Step 3: Watch Bot Logs During Payment

Keep the bot running and watch terminal. When you pay, look for:

```
[PAYMENT CHECK] Started for md5=abc123...
[GET ACCOUNTS] Looking for stock file: database/stock_1_1M.txt
[GET ACCOUNTS] Stock file has X lines
[GET ACCOUNTS] Valid lines after filtering: X
[GET ACCOUNTS] Got 1 accounts, remaining: X-1
[PAYMENT SUCCESS] Got accounts: ['email@example.com,password123,...']
[PAYMENT SUCCESS] Processing 1 accounts
[PAYMENT SUCCESS] Accounts found and message prepared
[PAYMENT SUCCESS] Confirmation message sent to user
```

---

## Step 4: Understand the Flow

1. **User clicks Pay** → `/pay` callback triggered
2. **QR Generated** → Image sent to user
3. **Payment Loop Starts** → Bot checks every 5 seconds
4. **User Pays** → Bakong confirms payment (md5 match)
5. **Stock Retrieved** → Accounts pulled from stock file
6. **Delivery Sent** → Confirmation message with accounts

---

## Common Issues & Fixes

| Log Message | Problem | Solution |
|---|---|---|
| `[GET ACCOUNTS] Stock file NOT found` | File doesn't exist | Add stock with `/addstock` |
| `[GET ACCOUNTS] Not enough valid accounts` | Not enough lines in file | Add more accounts to stock file |
| `[PAYMENT CHECK] Attempt 120: Response = None` | No payment detected | Payment might have failed or wrong account |
| `[PAYMENT SUCCESS] Failed to send confirmation` | Message sending failed | Check bot token, Telegram API status |

---

## Test Without Real Payment (Test Mode)

1. Edit `.env` - comment out BAKONG_TOKEN:
```
# BAKONG_TOKEN=your_token
```

2. Run bot:
```powershell
python storebot.py
```

3. Click `/start` → Select product → Click Pay → Wait 5 seconds → Auto-confirms

4. Watch logs for:
```
[PAYMENT CHECK] Testing mode - auto confirming payment
[GET ACCOUNTS] Got 1 accounts...
[PAYMENT SUCCESS] Confirmation message sent to user
```

---

## If It Still Doesn't Work

1. **Check .env file:**
```powershell
Get-Content .env
```

2. **Verify bot is running (watch for HTTP 200 OK):**
```
INFO:httpx:HTTP Request: ... "HTTP/1.1 200 OK"
```

3. **Check stock file manually:**
```powershell
(Get-Content database/stock_1_1M.txt).Count  # Should be > 0
```

4. **Restart bot after any changes to files**

5. **Check logs output - copy-paste logs here for debugging**

---

## Quick Test Commands

```powershell
# Check if stock file exists
Test-Path "database/stock_1_1M.txt"

# Count lines in stock file
(Get-Content database/stock_1_1M.txt | Measure-Object -Line).Lines

# View first account
(Get-Content database/stock_1_1M.txt)[0]

# Run bot and save logs
python storebot.py > bot_debug.log 2>&1
```

---

**When testing, share the log output from Step 3 and I'll help debug!**
