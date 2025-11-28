# 🚀 Deploy Your Bot to Cambodia VPS

**VPS IP:** 157.10.73.90  
**Bot File:** storebot.py  
**Database:** MongoDB Atlas

---

## 📋 Step 1: Upload Files to VPS

### Option A: Using WinSCP (Easier - Drag & Drop)

1. **Download WinSCP:** https://winscp.net/eng/download.php
2. **Connect to VPS:**
   - File protocol: `SFTP`
   - Host name: `157.10.73.90`
   - Port: `22`
   - User name: `root`
   - Password: (your VPS password)

3. **Upload these files to `/root/telegram-store-bot/`:**
   - `storebot.py`
   - `.env`
   - `requirements.txt`

### Option B: Using Command Line (PowerShell)

```powershell
# Upload bot file
scp storebot.py root@157.10.73.90:/root/telegram-store-bot/

# Upload .env file
scp .env root@157.10.73.90:/root/telegram-store-bot/

# Upload requirements
scp requirements.txt root@157.10.73.90:/root/telegram-store-bot/
```

---

## 🔧 Step 2: Connect to VPS

Using PuTTY or PowerShell:

```powershell
ssh root@157.10.73.90
```

Enter your VPS password when prompted.

---

## 📦 Step 3: Install Dependencies

Once connected to VPS, run:

```bash
cd /root/telegram-store-bot

# Install Python packages
pip3 install python-telegram-bot pymongo python-dotenv requests

# Or use requirements file
pip3 install -r requirements.txt
```

---

## 🚀 Step 4: Run Your Bot

### Quick Test (Foreground):

```bash
cd /root/telegram-store-bot
python3 storebot.py
```

Press `Ctrl+C` to stop.

### Run in Background (Recommended):

```bash
cd /root/telegram-store-bot

# Stop any old bot first
pkill -f storebot.py

# Start bot in background
nohup python3 storebot.py > bot.log 2>&1 &

# Check if running
ps aux | grep storebot.py
```

---

## 📊 Step 5: Monitor Your Bot

### View Live Logs:

```bash
tail -f /root/telegram-store-bot/bot.log
```

Press `Ctrl+C` to exit logs.

### Check if Bot is Running:

```bash
ps aux | grep storebot.py
```

### View Last 50 Lines of Log:

```bash
tail -50 /root/telegram-store-bot/bot.log
```

---

## 🔄 Common Commands

### Stop Bot:
```bash
pkill -f storebot.py
```

### Restart Bot:
```bash
pkill -f storebot.py
cd /root/telegram-store-bot
nohup python3 storebot.py > bot.log 2>&1 &
```

### Update Bot (after making changes):
```bash
# From Windows, upload new storebot.py
scp storebot.py root@157.10.73.90:/root/telegram-store-bot/

# On VPS, restart
ssh root@157.10.73.90
pkill -f storebot.py
cd /root/telegram-store-bot
nohup python3 storebot.py > bot.log 2>&1 &
```

---

## ✅ Verify Bot is Working

1. **Send `/start` to your bot** on Telegram
2. **Check logs on VPS:**
   ```bash
   tail -f /root/telegram-store-bot/bot.log
   ```
3. **You should see:** "Bot started successfully" in logs

---

## 🆘 Troubleshooting

### Bot Not Starting?

```bash
# Check the log for errors
cat /root/telegram-store-bot/bot.log

# Make sure .env file has correct token
cat /root/telegram-store-bot/.env

# Try running directly to see errors
cd /root/telegram-store-bot
python3 storebot.py
```

### Database Connection Issues?

Your `.env` file should have:
```
MONGODB_URI=mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net/telegram_store_bot?retryWrites=true&w=majority&appName=Cluster0
USE_MONGODB=true
```

### Port Already in Use?

```bash
# Find what's using the port
netstat -tulpn | grep python

# Kill old process
pkill -f storebot.py
```

---

## 🎯 Quick Deploy Script

Save this as `deploy.ps1` on Windows:

```powershell
# Upload files
scp storebot.py root@157.10.73.90:/root/telegram-store-bot/
scp .env root@157.10.73.90:/root/telegram-store-bot/

# Restart bot
ssh root@157.10.73.90 "pkill -f storebot.py; cd /root/telegram-store-bot && nohup python3 storebot.py > bot.log 2>&1 &"

Write-Host "✅ Bot deployed and started!" -ForegroundColor Green
Write-Host "Check logs: ssh root@157.10.73.90 'tail -f /root/telegram-store-bot/bot.log'"
```

Run with: `.\deploy.ps1`

---

## 📞 Your Bot Info

- **Bot Token:** 8197112968:AAFGBGjBRFmJzSe-UEKww3DJsFF9woa1wtY
- **Admin ID:** 7948968436
- **Database:** MongoDB Atlas (telegram_store_bot)
- **VPS:** Cambodia (157.10.73.90)

---

**Need help?** Check the bot logs first:
```bash
ssh root@157.10.73.90 'tail -100 /root/telegram-store-bot/bot.log'
```
