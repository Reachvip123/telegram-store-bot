# MongoDB VPS Deployment Guide

This guide shows you how to upgrade your VPS from JSON files to MongoDB Atlas.

---

## Prerequisites

Before you begin:
- ✅ MongoDB Atlas account created
- ✅ Connection string ready
- ✅ VPS IP (157.10.73.90) added to MongoDB Network Access
- ✅ Current bot is working with JSON files

---

## Step 1: Prepare Updated Files

On your local computer:

```bash
cd C:\Users\Reach\OneDrive\Desktop\telegrambot

# Add and commit new files to GitHub
git add storebot_mongodb.py migrate_to_mongodb.py requirements.txt MONGODB_SETUP.md
git commit -m "Add MongoDB support"
git push origin main
```

---

## Step 2: SSH to Your VPS

```bash
ssh root@157.10.73.90
```

---

## Step 3: Stop the Current Bot

```bash
# Stop the bot service
sudo systemctl stop telegram-store-bot

# Verify it's stopped
sudo systemctl status telegram-store-bot
```

---

## Step 4: Backup Current Data

```bash
cd /root/telegram-store-bot

# Create backup directory
mkdir -p backups
cp -r database/ backups/database_$(date +%Y%m%d_%H%M%S)
cp storebot.py backups/storebot_old.py
cp .env backups/.env.backup

echo "✅ Backup created"
```

---

## Step 5: Pull Latest Code

```bash
cd /root/telegram-store-bot

# Pull new files from GitHub
git pull origin main
```

---

## Step 6: Install MongoDB Dependencies

```bash
# Install new Python packages
pip install -r requirements.txt

# Verify pymongo and motor are installed
pip list | grep -E "pymongo|motor"
```

You should see:
```
motor         3.3.2
pymongo       4.6.1
```

---

## Step 7: Update .env File

```bash
nano /root/telegram-store-bot/.env
```

Add this line at the bottom:
```
MONGODB_URI=mongodb+srv://botadmin:YourPassword@your-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

**Important:** Replace with YOUR actual connection string from MongoDB Atlas!

Save and exit: `Ctrl+X`, `Y`, `Enter`

---

## Step 8: Run Migration Script

```bash
cd /root/telegram-store-bot

# Run the migration
python3 migrate_to_mongodb.py
```

You should see:
```
✅ Connected to MongoDB successfully!
📦 Starting Data Migration
✅ Migrated X products with Y variants
✅ Migrated Z stock items
✅ Migration complete!
```

---

## Step 9: Verify Data in MongoDB Atlas

1. Go to https://cloud.mongodb.com
2. Click **Database** → **Browse Collections**
3. You should see:
   - `products` collection with your products
   - `stock` collection with your inventory
   - `users` collection with customer data
   - `config` collection with settings

---

## Step 10: Update Bot Service

```bash
# Edit the systemd service
sudo nano /etc/systemd/system/telegram-store-bot.service
```

Change the `ExecStart` line to use the MongoDB version:
```ini
ExecStart=/usr/bin/python3 /root/telegram-store-bot/storebot_mongodb.py
```

Save and exit: `Ctrl+X`, `Y`, `Enter`

```bash
# Reload systemd
sudo systemctl daemon-reload
```

---

## Step 11: Start the MongoDB Bot

```bash
# Start the bot with MongoDB
sudo systemctl start telegram-store-bot

# Check status
sudo systemctl status telegram-store-bot
```

You should see:
```
🚀 MONGODB VERSION - Store Bot
✅ Connected to MongoDB Atlas
[OK] MongoDB collections initialized
[OK] Store Bot Running...
```

---

## Step 12: Test the Bot

1. Open Telegram
2. Send `/start` to your bot
3. Try viewing products
4. Check stock with `/stock`
5. Admin: use `/stats` to see MongoDB statistics

---

## Step 13: Monitor Logs

```bash
# Watch live logs
sudo journalctl -u telegram-store-bot -f

# Check for errors
sudo journalctl -u telegram-store-bot -n 50
```

---

## Troubleshooting

### Bot won't start
```bash
# Check detailed error
sudo journalctl -u telegram-store-bot -n 100

# Common issues:
# 1. Wrong MongoDB URI - check .env file
# 2. IP not whitelisted - add 157.10.73.90 to MongoDB Network Access
# 3. Wrong password in connection string
```

### Can't connect to MongoDB
```bash
# Test connection manually
python3 -c "from pymongo import MongoClient; client = MongoClient('YOUR_MONGODB_URI'); print('Connected:', client.admin.command('ping'))"
```

### Data not migrated
```bash
# Re-run migration
cd /root/telegram-store-bot
python3 migrate_to_mongodb.py
```

---

## Rollback (If Needed)

If something goes wrong, rollback to JSON version:

```bash
# Stop MongoDB bot
sudo systemctl stop telegram-store-bot

# Edit service to use old bot
sudo nano /etc/systemd/system/telegram-store-bot.service
# Change ExecStart back to: /usr/bin/python3 /root/telegram-store-bot/storebot.py

# Reload and start
sudo systemctl daemon-reload
sudo systemctl start telegram-store-bot
```

Your JSON files are still there as backup!

---

## Managing MongoDB from Web UI

### View Data:
1. Go to https://cloud.mongodb.com
2. Click **Database** → **Browse Collections**
3. Select `telegram_store_bot` database

### Edit Products:
1. Click `products` collection
2. Click on any document to edit
3. Modify fields (name, price, description)
4. Click **Update**

### View Orders:
1. Click `orders` collection
2. See all customer purchases with timestamps
3. Filter by user_id or date

### Manage Stock:
1. Click `stock` collection
2. Filter: `{sold: false}` to see available items
3. Filter: `{sold: true}` to see sold items
4. Delete out-of-date stock items

### Export Data:
1. Select any collection
2. Click **Export Collection**
3. Choose JSON or CSV format

---

## Benefits You Now Have

✅ **Web Access**: Manage data from anywhere via MongoDB Atlas
✅ **Automatic Backups**: MongoDB handles this for you
✅ **Better Performance**: Indexed queries, faster searches
✅ **Order History**: All transactions saved in `orders` collection
✅ **Analytics Ready**: Query sales data, user behavior
✅ **Scalable**: Upgrade storage as you grow
✅ **No SSH Needed**: Update products from web interface

---

## New Admin Commands

- `/stats` - View MongoDB database statistics
- All existing commands still work the same!

---

## MongoDB Atlas Tips

### Create Indexes for Better Performance:
1. In Atlas, click **Database** → **Browse Collections**
2. Select `products` collection
3. Click **Indexes** tab
4. Create index on `name` field (for faster searches)

### Set Up Alerts:
1. Click **Alerts** (left sidebar)
2. Create alert for:
   - Storage usage > 80%
   - Connection failures
   - High query latency

### View Performance:
1. Click **Metrics** tab
2. Monitor:
   - Operations per second
   - Network traffic
   - Connection count

---

## Next Steps After Migration

1. ✅ Test all bot features (buy products, check stock)
2. ✅ Verify orders appear in MongoDB
3. ✅ Check `/stats` command works
4. ✅ Try editing a product in Atlas web UI
5. ✅ Keep JSON backup for 1 week, then can delete

---

## Support

If you encounter issues:

1. Check logs: `sudo journalctl -u telegram-store-bot -n 100`
2. Verify MongoDB connection in Atlas
3. Test migration script output
4. Check .env file has correct MONGODB_URI

---

**Congratulations!** 🎉

Your bot now uses MongoDB Atlas with full web-based management!
