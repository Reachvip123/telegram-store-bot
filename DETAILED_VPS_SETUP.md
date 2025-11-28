# 🇰🇭 Complete Cambodia VPS Setup Guide
## Step-by-Step Instructions for Bakong KHQR Proxy

---

## 📋 What You'll Need:
1. ✅ Cambodia VPS (you already have this)
2. ✅ SSH access to your VPS (root or sudo user)
3. ✅ Your Bakong API token
4. ✅ PuTTY or Terminal to connect to VPS

---

## 🚀 PART 1: Connect to Your VPS

### Windows Users (Using PuTTY):

1. **Download PuTTY** (if you don't have it)
   - Go to: https://www.putty.org/
   - Download and install

2. **Connect to VPS:**
   - Open PuTTY
   - Enter your VPS IP address in "Host Name"
   - Port: `22`
   - Click "Open"
   
3. **Login:**
   - Login as: `root` (or your username)
   - Password: (your VPS password)

### Mac/Linux Users (Using Terminal):

```bash
ssh root@YOUR_VPS_IP_ADDRESS
# Enter your password when prompted
```

---

## 🚀 PART 2: Automatic Setup (EASY METHOD)

Once connected to your VPS, follow these steps:

### **Step 1: Download Setup Script**

Copy and paste this command (press Enter):

```bash
curl -o setup_vps.sh https://raw.githubusercontent.com/Reachvip123/telegram-store-bot/main/setup_vps.sh
```

### **Step 2: Make Script Executable**

```bash
chmod +x setup_vps.sh
```

### **Step 3: Run Setup Script**

```bash
sudo bash setup_vps.sh
```

This will automatically:
- ✅ Update your system
- ✅ Install Python and dependencies
- ✅ Clone your bot repository
- ✅ Install required packages
- ✅ Create configuration files
- ✅ Setup systemd service
- ✅ Configure firewall

**Wait for it to complete** (takes 2-3 minutes)

### **Step 4: Edit Configuration File**

Add your Bakong token:

```bash
nano /root/telegram-store-bot/.env
```

You'll see:
```
BAKONG_TOKEN=your_bakong_token_here
```

**Change `your_bakong_token_here` to your actual Bakong token**

**To save and exit:**
- Press `Ctrl + X`
- Press `Y`
- Press `Enter`

### **Step 5: Start the Proxy**

```bash
systemctl start bakong-proxy
```

### **Step 6: Check if Running**

```bash
systemctl status bakong-proxy
```

You should see:
```
● bakong-proxy.service - Bakong KHQR Proxy Server
   Active: active (running)
```

If you see **"active (running)"** in green - SUCCESS! ✅

Press `q` to exit the status view.

### **Step 7: Test the Proxy**

```bash
curl http://localhost:5000/health
```

Should return:
```json
{"service":"bakong-khqr-proxy","status":"ok"}
```

### **Step 8: Get Your VPS IP Address**

```bash
curl ifconfig.me
```

Write down this IP address - you'll need it for Railway!

Example output: `123.45.67.89`

---

## 🚀 PART 3: Configure Railway

### **Step 1: Go to Railway Dashboard**

1. Open https://railway.app
2. Go to your project
3. Click on your bot service
4. Click "Variables" tab

### **Step 2: Add Environment Variable**

Click "+ New Variable" and add:

**Variable name:**
```
BAKONG_PROXY_URL
```

**Value:**
```
http://YOUR_VPS_IP:5000
```

Replace `YOUR_VPS_IP` with the IP from Step 8 above.

Example: `http://123.45.67.89:5000`

### **Step 3: Make Sure These Variables Are Set:**

```
BOT_TOKEN = your_telegram_bot_token
BAKONG_PROXY_URL = http://YOUR_VPS_IP:5000
BAKONG_ACCOUNT = vorn_sovannareach@wing
MERCHANT_NAME = SOVANNAREACH VORN
ADMIN_ID = 7948968436
ADMIN_USERNAME = @dzy4u2
```

**DO NOT set BAKONG_TOKEN on Railway** - it's only on the VPS!

### **Step 4: Deploy**

Railway will automatically redeploy your bot.

---

## 🧪 PART 4: Test Everything

### **Test 1: Test VPS Proxy from Your Computer**

Open PowerShell on your computer and run:

```powershell
curl http://YOUR_VPS_IP:5000/health
```

Should return: `{"service":"bakong-khqr-proxy","status":"ok"}`

### **Test 2: Test in Telegram Bot**

1. Open Telegram
2. Find your bot
3. Send command: `/testkhqr`
4. You should see: ✅ **KHQR Test SUCCESSFUL**

### **Test 3: Try a Real Purchase**

1. Send `/start` to your bot
2. Click "🛍 List Products"
3. Select a product
4. Try to buy it
5. You should see a green Bakong QR code!

---

## 🔧 PART 5: Useful Commands

### Check Proxy Status:
```bash
systemctl status bakong-proxy
```

### View Proxy Logs (Real-time):
```bash
journalctl -u bakong-proxy -f
```
Press `Ctrl+C` to exit

### Restart Proxy:
```bash
systemctl restart bakong-proxy
```

### Stop Proxy:
```bash
systemctl stop bakong-proxy
```

### Start Proxy:
```bash
systemctl start bakong-proxy
```

### Update Proxy Code (if you push changes to GitHub):
```bash
cd /root/telegram-store-bot
git pull
systemctl restart bakong-proxy
```

---

## ❌ Troubleshooting

### Problem: "Connection refused" when testing

**Solution:**
```bash
# Check if proxy is running
systemctl status bakong-proxy

# Check firewall
sudo ufw status

# Make sure port 5000 is open
sudo ufw allow 5000
```

### Problem: "Invalid QR Code" in bot

**Solution:**
```bash
# Check proxy logs for errors
journalctl -u bakong-proxy -n 50

# Make sure BAKONG_TOKEN is correct
nano /root/telegram-store-bot/.env

# Restart proxy after editing
systemctl restart bakong-proxy
```

### Problem: Bot can't connect to proxy

**Solution:**
```bash
# Test from VPS itself
curl http://localhost:5000/health

# Test from outside
curl http://YOUR_VPS_IP:5000/health

# If second test fails, check firewall:
sudo ufw allow 5000
```

### Problem: Proxy not starting

**Solution:**
```bash
# Check detailed logs
journalctl -u bakong-proxy -n 100 --no-pager

# Check if Python packages are installed
pip3 list | grep bakong

# Reinstall if needed
pip3 install --upgrade bakong-khqr flask
systemctl restart bakong-proxy
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  Customer in Telegram                           │
│         ↓                                       │
│  Your Bot on Railway (USA/Europe)               │
│         ↓                                       │
│  HTTP Request to Proxy                          │
│         ↓                                       │
│  Proxy on Cambodia VPS ← You set this up!       │
│         ↓                                       │
│  Bakong API (Cambodia only)                     │
│         ↓                                       │
│  Payment Confirmed                              │
│         ↓                                       │
│  Product Auto-Delivered                         │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## ✅ Success Checklist

Before you finish, verify:

- [ ] VPS proxy is running: `systemctl status bakong-proxy` shows "active"
- [ ] Health check works: `curl http://localhost:5000/health` returns OK
- [ ] Firewall allows port 5000: `sudo ufw status` shows 5000/tcp ALLOW
- [ ] Railway has BAKONG_PROXY_URL set to `http://YOUR_VPS_IP:5000`
- [ ] `/testkhqr` in Telegram shows success
- [ ] Can generate QR code when buying a product
- [ ] QR code is green (Bakong color)

---

## 🎉 You're Done!

Your bot is now fully operational with Bakong KHQR payment!

Cambodian customers can pay with:
- ABA Mobile
- Wing Money  
- TrueMoney
- Pi Pay
- Any Bakong-enabled bank app

The bot will automatically verify payments and deliver products! 🚀

---

## 📞 Need Help?

If something doesn't work:

1. Check the troubleshooting section above
2. Run: `journalctl -u bakong-proxy -n 100` to see errors
3. Contact: @dzy4u2 (your admin)

---

**Last Updated:** November 28, 2025
