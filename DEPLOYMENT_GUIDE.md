# 🚀 VPS Deployment Guide - Telegram Store Bot

This guide will help you deploy your Telegram store bot to your Cambodia VPS.

## 📋 Prerequisites

- ✅ Cambodia VPS (Bakong API requires Cambodia IP)
- ✅ Telegram Bot Token from [@BotFather](https://t.me/botfather)
- ✅ Bakong API Token from [https://api-bakong.nbc.gov.kh/](https://api-bakong.nbc.gov.kh/)
- ✅ SSH access to your VPS
- ✅ Ubuntu/Debian based VPS (recommended)

## 🔧 Option 1: Automated Deployment (Recommended)

### Step 1: Upload Files to VPS

From your Windows PC, upload these files to your VPS:

```powershell
# Using SCP (replace with your VPS details)
scp storebot.py your_username@your_vps_ip:~/
scp deploy.sh your_username@your_vps_ip:~/
scp .env.example your_username@your_vps_ip:~/
scp template.png your_username@your_vps_ip:~/  # if you have it
```

**OR use FileZilla/WinSCP** (easier GUI option):
1. Connect to your VPS IP
2. Upload: `storebot.py`, `deploy.sh`, `.env.example`, `template.png`

### Step 2: Run Deployment Script

SSH into your VPS and run:

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Step 3: Configure Environment

```bash
# Copy example env file
cd ~/telegram-store-bot
cp .env.example .env

# Edit with your credentials
nano .env
```

Update these values in `.env`:
- `BOT_TOKEN` - Your Telegram bot token
- `BAKONG_TOKEN` - Your Bakong API token
- `BAKONG_ACCOUNT` - Your payment account
- `ADMIN_ID` - Your Telegram user ID

Save: `Ctrl+X`, then `Y`, then `Enter`

### Step 4: Upload Your Bot File

```bash
# Copy storebot.py to project directory
cp ~/storebot.py ~/telegram-store-bot/
cp ~/template.png ~/telegram-store-bot/  # if you have it
```

### Step 5: Start the Bot

```bash
sudo systemctl start storebot
sudo systemctl status storebot
```

---

## 🔨 Option 2: Manual Deployment

### Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git
```

### Step 2: Create Project Directory

```bash
mkdir -p ~/telegram-store-bot
cd ~/telegram-store-bot
```

### Step 3: Setup Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install python-telegram-bot==20.7
pip install python-dotenv==1.0.0
pip install qrcode==7.4.2
pip install Pillow==10.1.0
pip install bakong-khqr==1.3.0
pip install pymongo==4.6.0
pip install requests==2.31.0
```

### Step 5: Create .env File

```bash
nano .env
```

Add this content (replace with your actual values):

```env
BOT_TOKEN=your_telegram_bot_token_here
BAKONG_TOKEN=your_bakong_token_here
BAKONG_ACCOUNT=vorn_sovannareach@wing
MERCHANT_NAME=SOVANNAREACH VORN
ADMIN_ID=7948968436
ADMIN_USERNAME=@dzy4u2
BAKONG_PROXY_URL=
USE_MONGODB=false
MONGODB_URI=
```

### Step 6: Upload Bot Files

Upload `storebot.py` and `template.png` to `~/telegram-store-bot/`

### Step 7: Create Database Directory

```bash
mkdir -p database
```

### Step 8: Create Systemd Service

```bash
sudo nano /etc/systemd/system/storebot.service
```

Add this content (replace `YOUR_USERNAME` with your actual username):

```ini
[Unit]
Description=Telegram Store Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/telegram-store-bot
Environment="PATH=/home/YOUR_USERNAME/telegram-store-bot/venv/bin"
ExecStart=/home/YOUR_USERNAME/telegram-store-bot/venv/bin/python storebot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 9: Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable storebot
sudo systemctl start storebot
```

---

## 📊 Managing Your Bot

### Check Status
```bash
sudo systemctl status storebot
```

### View Live Logs
```bash
sudo journalctl -u storebot -f
```

### View Recent Logs
```bash
sudo journalctl -u storebot -n 100
```

### Restart Bot
```bash
sudo systemctl restart storebot
```

### Stop Bot
```bash
sudo systemctl stop storebot
```

### Check if Running
```bash
ps aux | grep storebot
```

---

## 🔍 Troubleshooting

### Bot Won't Start

1. **Check logs for errors:**
   ```bash
   sudo journalctl -u storebot -n 50
   ```

2. **Common issues:**
   - ❌ Invalid `BOT_TOKEN` - verify from @BotFather
   - ❌ Missing `BAKONG_TOKEN` - get from Bakong API portal
   - ❌ Wrong file paths in service file
   - ❌ Python packages not installed
   - ❌ Permission issues

3. **Manual test:**
   ```bash
   cd ~/telegram-store-bot
   source venv/bin/activate
   python storebot.py
   ```
   This will show any errors directly

### Payment Issues

1. **Verify Bakong configuration:**
   ```bash
   # In your bot, send /testkhqr to verify KHQR works
   ```

2. **Check VPS location:**
   - Bakong API only works from Cambodia IPs
   - If outside Cambodia, use `BAKONG_PROXY_URL`

### Database Issues

```bash
# Check database directory exists
ls -la ~/telegram-store-bot/database/

# Create if missing
mkdir -p ~/telegram-store-bot/database
```

### Service Issues

```bash
# Reload systemd after editing service file
sudo systemctl daemon-reload

# Re-enable service
sudo systemctl disable storebot
sudo systemctl enable storebot
sudo systemctl restart storebot
```

---

## 🔐 Security Recommendations

1. **Protect your .env file:**
   ```bash
   chmod 600 ~/telegram-store-bot/.env
   ```

2. **Use firewall:**
   ```bash
   sudo ufw allow ssh
   sudo ufw allow 443
   sudo ufw enable
   ```

3. **Regular backups:**
   ```bash
   # Backup database folder
   tar -czf backup-$(date +%Y%m%d).tar.gz ~/telegram-store-bot/database/
   ```

4. **Keep system updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

---

## 📱 Testing Your Bot

After deployment:

1. **Start conversation:**
   - Message `/start` to your bot
   - Check welcome message appears

2. **Test KHQR:**
   - Send `/testkhqr` (admin only)
   - Verify QR code generates

3. **Add products:**
   - Use `/addpd Name | Variant | Price | Description`

4. **Add stock:**
   - Use `/addstock` and follow prompts

5. **Test purchase:**
   - Try buying a product
   - Verify payment flow works

---

## 🆘 Getting Help

If you encounter issues:

1. Check logs: `sudo journalctl -u storebot -f`
2. Verify all environment variables are set correctly
3. Ensure VPS is in Cambodia (for Bakong)
4. Check file permissions
5. Test Python packages are installed: `pip list`

---

## 📝 File Structure

After deployment, your structure should look like:

```
/home/YOUR_USERNAME/telegram-store-bot/
├── venv/                    # Python virtual environment
├── database/                # Local database storage
│   ├── products.json
│   ├── config.json
│   ├── users.json
│   └── stock_*.txt
├── storebot.py             # Main bot code
├── template.png            # QR template (optional)
├── .env                    # Environment variables
└── qr_*.png               # Generated QR codes (temporary)
```

---

## ✅ Success Checklist

- [ ] VPS is in Cambodia
- [ ] Python 3.8+ installed
- [ ] All dependencies installed
- [ ] `.env` file configured with correct tokens
- [ ] `storebot.py` uploaded
- [ ] Systemd service created and enabled
- [ ] Bot is running: `sudo systemctl status storebot`
- [ ] Bot responds to `/start`
- [ ] `/testkhqr` generates QR code
- [ ] Can add products and stock
- [ ] Payment verification works

---

## 🎉 Your Bot is Live!

Once deployed successfully, your bot will:
- ✅ Run 24/7 automatically
- ✅ Auto-restart on crashes
- ✅ Start on VPS reboot
- ✅ Handle payments via Bakong KHQR
- ✅ Store data locally in database folder
- ✅ Log all activities for monitoring

Happy selling! 🛍️
