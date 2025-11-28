#!/bin/bash
# Complete Bot Setup for Cambodia VPS
# Run this on your Cambodia VPS to run the entire bot there

echo "=================================="
echo "Telegram Store Bot - Cambodia VPS Setup"
echo "=================================="
echo ""

# Go to project directory
cd /root/telegram-store-bot || exit

echo "Step 1: Pulling latest code from GitHub..."
git pull origin main

echo "Step 2: Installing Python packages..."
pip3 install -r requirements.txt

echo "Step 3: Checking .env file..."
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'ENVEOF'
# Telegram Bot Configuration
BOT_TOKEN=8197112968:AAFGBGjBRFmJzSe-UEKww3DJsFF9woa1wtY
BAKONG_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImlkIjoiZDBmMzk2NTAzMTcyNGE3NiJ9LCJpYXQiOjE3NjQxNjM4NDYsImV4cCI6MTc3MTkzOTg0Nn0.xrFGRwFstiyjzDwoe2g_F4bJAUdn7oUrQnH5ns8WZCU
BAKONG_ACCOUNT=vorn_sovannareach@wing
MERCHANT_NAME=SOVANNAREACH VORN
ADMIN_ID=7948968436
ADMIN_USERNAME=@dzy4u2

# Optional: MongoDB Configuration (leave as false for local storage)
USE_MONGODB=false
MONGODB_URI=

# DO NOT SET BAKONG_PROXY_URL - running directly on Cambodia VPS
BAKONG_PROXY_URL=
ENVEOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

echo "Step 4: Creating database directory..."
mkdir -p database

echo "Step 5: Creating systemd service for the bot..."
cat > /etc/systemd/system/telegram-store-bot.service << 'SERVICEEOF'
[Unit]
Description=Telegram Store Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/telegram-store-bot
EnvironmentFile=/root/telegram-store-bot/.env
ExecStart=/usr/bin/python3 /root/telegram-store-bot/storebot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICEEOF

echo "Step 6: Reloading systemd and enabling bot service..."
systemctl daemon-reload
systemctl enable telegram-store-bot

echo "Step 7: Starting the bot..."
systemctl start telegram-store-bot

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "📋 Useful Commands:"
echo ""
echo "Check bot status:"
echo "  systemctl status telegram-store-bot"
echo ""
echo "View bot logs (real-time):"
echo "  journalctl -u telegram-store-bot -f"
echo ""
echo "Restart bot:"
echo "  systemctl restart telegram-store-bot"
echo ""
echo "Stop bot:"
echo "  systemctl stop telegram-store-bot"
echo ""
echo "Update bot code:"
echo "  cd /root/telegram-store-bot && git pull && systemctl restart telegram-store-bot"
echo ""
echo "=================================="
echo ""
echo "🎉 Your bot is now running on Cambodia VPS!"
echo "Go to Telegram and send /start to your bot!"
echo ""
