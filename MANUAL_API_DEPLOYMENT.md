# 📋 Manual API Deployment Guide for Cambodia VPS

If the automated scripts don't work, follow these manual steps:

## 📤 Step 1: Upload Files to VPS

### Option A: Using File Manager (Easiest)
1. **Access your VPS file manager** (through hosting control panel)
2. **Navigate to:** `/root/telegram-store-bot/`
3. **Upload these files:**
   - `api_bridge.py`
   - `.env_api` (created by the script)

### Option B: Using SCP/SFTP
```bash
scp api_bridge.py .env_api root@157.10.73.90:/root/telegram-store-bot/
```

### Option C: Copy-Paste Method
1. **SSH into your VPS:**
   ```bash
   ssh root@157.10.73.90
   ```

2. **Create API file:**
   ```bash
   cd /root/telegram-store-bot
   nano api_bridge.py
   ```
   Copy-paste the entire content of `api_bridge.py`

3. **Create environment file:**
   ```bash
   nano .env_api
   ```
   Copy-paste this content:
   ```env
   MONGODB_URI=mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net
   DATABASE_NAME=storebot
   API_KEY=DZT-SECURE-API-2024-CHANGE-THIS-KEY
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

## ⚙️ Step 2: Install Dependencies on VPS

**SSH into your VPS and run:**
```bash
ssh root@157.10.73.90
cd /root/telegram-store-bot

# Install required packages
pip install flask flask-cors python-dotenv pymongo

# Or if pip3 is required:
pip3 install flask flask-cors python-dotenv pymongo
```

## 🚀 Step 3: Start the API Bridge

```bash
# Stop any existing API process
pkill -f api_bridge.py

# Start API in background
nohup python3 api_bridge.py > api.log 2>&1 &

# Save process ID
echo $! > api.pid
```

## 🔍 Step 4: Test API

```bash
# Test locally on VPS
curl http://localhost:8081/health

# Check if port is open
netstat -tlnp | grep 8081

# View logs if there are issues
tail -f api.log
```

## 🔥 Step 5: Open Firewall Port

```bash
# Open port 8081
ufw allow 8081

# Or if using iptables:
iptables -I INPUT -p tcp --dport 8081 -j ACCEPT
```

## ✅ Step 6: Verify External Access

**Test from your computer:**
```bash
curl http://157.10.73.90:8081/health
```

**Or visit in browser:**
http://157.10.73.90:8081/health

**Expected response:**
```json
{
  "status": "ok",
  "service": "Store Bot API",
  "timestamp": "2025-11-28T...",
  "location": "Cambodia VPS"
}
```

## 🛠️ Management Commands

```bash
# Check if API is running
ps aux | grep api_bridge

# View logs
tail -f /root/telegram-store-bot/api.log

# Stop API
kill $(cat /root/telegram-store-bot/api.pid)

# Start API
cd /root/telegram-store-bot
nohup python3 api_bridge.py > api.log 2>&1 &

# Restart API
pkill -f api_bridge.py
sleep 2
nohup python3 api_bridge.py > api.log 2>&1 &
```

## 🚨 Troubleshooting

### API won't start:
```bash
# Check logs for errors
cat /root/telegram-store-bot/api.log

# Check Python version
python3 --version

# Test MongoDB connection
python3 -c "import pymongo; print('MongoDB lib OK')"
```

### Port not accessible:
```bash
# Check if port is listening
ss -tlnp | grep 8081
netstat -tlnp | grep 8081

# Check firewall status
ufw status
iptables -L
```

### Permission issues:
```bash
# Make sure files are executable
chmod +x api_bridge.py
chmod 644 .env_api

# Check file ownership
ls -la /root/telegram-store-bot/
```

## 🎯 Success Indicators

✅ **API responds to health check**
✅ **Port 8081 is listening**
✅ **No errors in api.log**
✅ **Process shows in ps aux**
✅ **External access works**

## 📱 Next Steps

Once API is working:
1. **Upload hostinger_index.php to Hostinger**
2. **Edit configuration in the PHP file**
3. **Access web admin at yourdomain.com/admin**

Your Cambodia VPS API bridge is now ready! 🚀