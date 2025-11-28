# 🎯 SIMPLE 3-STEP DEPLOYMENT

## ✅ You Need:
- Bot file: `storebot.py` ✓
- Config file: `.env` ✓
- VPS IP: `157.10.73.90` ✓
- VPS Password (ask your VPS provider)

---

## 🚀 FASTEST WAY - Run This Command:

Open PowerShell in this folder and run:

```powershell
.\deploy_cambodia.ps1
```

**That's it!** The script will:
1. Upload your bot to Cambodia VPS
2. Install all dependencies
3. Start the bot automatically

---

## 📱 OR Do It Manually (3 Steps):

### Step 1: Upload Files to VPS

```powershell
scp storebot.py root@157.10.73.90:/root/telegram-store-bot/
scp .env root@157.10.73.90:/root/telegram-store-bot/
```

### Step 2: Connect to VPS

```powershell
ssh root@157.10.73.90
```

### Step 3: Run Bot

```bash
cd /root/telegram-store-bot
pip3 install python-telegram-bot pymongo python-dotenv requests
pkill -f storebot.py
nohup python3 storebot.py > bot.log 2>&1 &
```

**Done!** Send `/start` to your bot on Telegram.

---

## 📊 Check If Bot is Running

```powershell
ssh root@157.10.73.90 "ps aux | grep storebot.py"
```

You should see: `python3 storebot.py`

---

## 📋 View Bot Logs

```powershell
ssh root@157.10.73.90 "tail -50 /root/telegram-store-bot/bot.log"
```

---

## 🔄 Update Bot Later

After changing `storebot.py`, just run this:

```powershell
.\deploy_cambodia.ps1
```

It will upload and restart automatically!

---

## ❌ Stop Bot

```powershell
ssh root@157.10.73.90 "pkill -f storebot.py"
```

---

## 🆘 Troubleshooting

**Bot not responding?**
1. Check if running: `ssh root@157.10.73.90 "ps aux | grep storebot.py"`
2. Check logs: `ssh root@157.10.73.90 "tail -100 /root/telegram-store-bot/bot.log"`
3. Try restarting: `.\deploy_cambodia.ps1`

**Can't connect to VPS?**
- Make sure you have VPS password
- Check VPS is online: `ping 157.10.73.90`

**Permission denied when uploading?**
- Make sure directory exists on VPS
- Use correct VPS username (usually `root`)

---

## 📞 Your Configuration

- **Bot Token:** 8197112968:AAF...wtY (in .env)
- **Admin ID:** 7948968436
- **Database:** MongoDB Atlas
- **VPS:** 157.10.73.90 (Cambodia)
- **Bot Location:** /root/telegram-store-bot/

---

## ✨ That's All!

1. Run: `.\deploy_cambodia.ps1`
2. Wait 30 seconds
3. Send `/start` to your bot
4. ✅ Done!
