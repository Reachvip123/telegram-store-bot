# 🔄 Switch Your Bot to MongoDB (Super Easy!)

Your bot is currently using **JSON files** instead of MongoDB.
You have a **MongoDB version ready** - just need to switch to it!

## 📋 Quick Fix (3 Steps)

### Step 1: Connect to VPS
```bash
ssh root@157.10.73.90
```

### Step 2: Stop Old Bot & Start MongoDB Version
```bash
cd /root/telegram-store-bot

# Stop old bot
pkill -f storebot.py

# Start MongoDB version
nohup python3 storebot_mongodb.py > bot.log 2>&1 &

# Check it's running
ps aux | grep storebot_mongodb
```

### Step 3: Test It
Open Telegram and send `/start` to your bot

---

## ✅ What This Does

- **Old bot (storebot.py)**: Saves to JSON files
- **New bot (storebot_mongodb.py)**: Saves to MongoDB Atlas ✨

Your `.env` file is already configured with MongoDB credentials!

---

## 🔍 Verify MongoDB Connection

After starting the bot, check the log:
```bash
tail -f /root/telegram-store-bot/bot.log
```

You should see:
```
[OK] Connected to MongoDB Atlas
[OK] MongoDB collections initialized
```

---

## 🎯 Now Your Data Goes to MongoDB!

All your data will be saved to MongoDB Atlas:
- Products → `products` collection
- Users → `users` collection
- Stock → `stock` collection
- Orders → `orders` collection
- Config → `config` collection

**Database name:** `telegram_store_bot`
**Connection:** `mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net`

---

## 💡 Manage Everything via Telegram

No web panel needed! Just use bot commands:
- `/addproduct` - Add products
- `/manageproducts` - Manage products & stock
- `/stats` - View statistics
- All data saves to MongoDB automatically! 🎉
