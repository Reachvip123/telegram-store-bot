# 🚀 EASY MANUAL DEPLOYMENT - Step by Step

## ✅ What We Need to Do:
1. **Upload 2 files** to your Cambodia VPS
2. **Run 4 simple commands** on your VPS  
3. **Test the API** is working

## 📤 Step 1: Upload Files to VPS

You have 2 files to upload:
- ✅ `api_bridge.py` (already created)
- ✅ `.env_api` (just created)

### Method A: Using VPS File Manager (Easiest)
1. **Log into your VPS control panel**
2. **Open File Manager** 
3. **Navigate to:** `/root/telegram-store-bot/`
4. **Upload these 2 files:**
   - `api_bridge.py`
   - `.env_api`

### Method B: Using SSH + nano (Copy-Paste)
1. **Connect to your VPS:**
   ```
   ssh root@157.10.73.90
   ```

2. **Go to bot directory:**
   ```
   cd /root/telegram-store-bot
   ```

3. **Create api_bridge.py file:**
   ```
   nano api_bridge.py
   ```
   - Copy the entire content from your local `api_bridge.py` file
   - Paste it in nano
   - Press `Ctrl+X`, then `Y`, then `Enter` to save

4. **Create .env_api file:**
   ```
   nano .env_api
   ```
   - Paste this content:
   ```
   MONGODB_URI=mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net
   DATABASE_NAME=storebot
   API_KEY=DZT-SECURE-API-2024-CHANGE-THIS-KEY
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```
   - Press `Ctrl+X`, then `Y`, then `Enter` to save

## ⚙️ Step 2: Install Dependencies on VPS

**SSH into your VPS and run these 4 commands:**

```bash
# 1. Go to bot directory
cd /root/telegram-store-bot

# 2. Install required packages
pip install flask flask-cors python-dotenv pymongo

# 3. Start the API bridge
nohup python3 api_bridge.py > api.log 2>&1 &

# 4. Open firewall port
ufw allow 8081
```

## 🔍 Step 3: Test API

**Still in SSH, test if API is working:**

```bash
# Test API locally
curl http://localhost:8081/health
```

**Expected result:**
```json
{
  "status": "ok",
  "service": "Store Bot API",
  "timestamp": "2025-11-28T...",
  "location": "Cambodia VPS"
}
```

## 🌐 Step 4: Test External Access

**From your computer (or browser), visit:**
```
http://157.10.73.90:8081/health
```

You should see the same JSON response.

## ✅ Success Checklist

- ✅ API responds to health check
- ✅ No errors in logs: `tail -f /root/telegram-store-bot/api.log`
- ✅ Process is running: `ps aux | grep api_bridge`
- ✅ Port is open: `netstat -tlnp | grep 8081`

## 🎯 What's Next?

Once your API is working:

1. **Upload web admin to Hostinger:**
   - File: `hostinger_index.php` → rename to `index.php`
   - Location: `public_html/admin/index.php`

2. **Edit configuration in the PHP file:**
   ```php
   $ADMIN_PASSWORD = 'your-password-here';  // Change this!
   $API_KEY = 'DZT-SECURE-API-2024-CHANGE-THIS-KEY';  // Same as .env_api
   ```

3. **Access your web admin:**
   ```
   http://yourdomain.com/admin
   ```

## 🚨 If Something Goes Wrong

**Check logs:**
```bash
tail -f /root/telegram-store-bot/api.log
```

**Restart API:**
```bash
pkill -f api_bridge.py
cd /root/telegram-store-bot  
nohup python3 api_bridge.py > api.log 2>&1 &
```

**Check if port is blocked:**
```bash
netstat -tlnp | grep 8081
ufw status
```

## 📞 Quick Help

If you get stuck, run this diagnostic:
```bash
cd /root/telegram-store-bot
echo "=== Files ==="
ls -la api_bridge.py .env_api
echo "=== Process ==="  
ps aux | grep api_bridge
echo "=== Port ==="
netstat -tlnp | grep 8081
echo "=== Logs ==="
tail -5 api.log
```

**Your Cambodia VPS API bridge will be ready! 🚀**