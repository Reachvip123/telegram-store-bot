#!/bin/bash

# Telegram Store Bot Deployment Script for Cambodia VPS
# This script will set up and deploy your bot on a fresh VPS

set -e

echo "=========================================="
echo "Telegram Store Bot Deployment"
echo "=========================================="

# Update system
echo "[1/8] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo "[2/8] Installing Python and required packages..."
sudo apt install -y python3 python3-pip python3-venv git

# Create project directory
PROJECT_DIR="$HOME/telegram-store-bot"
echo "[3/8] Creating project directory at $PROJECT_DIR..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create virtual environment
echo "[4/8] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "[5/8] Installing Python packages..."
pip install --upgrade pip
pip install python-telegram-bot==20.7 python-dotenv==1.0.0 qrcode==7.4.2 Pillow==10.1.0 bakong-khqr==1.3.0 pymongo==4.6.0 requests==2.31.0

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "[6/8] Creating .env file (please edit it with your credentials)..."
    cat > .env << 'EOF'
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# Bakong Payment Configuration
BAKONG_TOKEN=your_bakong_token_here
BAKONG_ACCOUNT=vorn_sovannareach@wing
MERCHANT_NAME=SOVANNAREACH VORN

# Admin Configuration
ADMIN_ID=7948968436
ADMIN_USERNAME=@dzy4u2

# Optional: Bakong Proxy (leave empty if in Cambodia)
BAKONG_PROXY_URL=

# Database Configuration
USE_MONGODB=false
MONGODB_URI=
EOF
    echo "⚠️  IMPORTANT: Edit .env file with your actual credentials!"
    echo "   nano .env"
else
    echo "[6/8] .env file already exists, skipping..."
fi

# Create database directory
echo "[7/8] Creating database directory..."
mkdir -p database

# Setup systemd service
echo "[8/8] Setting up systemd service..."
SERVICE_FILE="/etc/systemd/system/storebot.service"
sudo bash -c "cat > $SERVICE_FILE" << EOF
[Unit]
Description=Telegram Store Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/storebot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable storebot.service

echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Copy your storebot.py to: $PROJECT_DIR/"
echo "2. Edit .env with your credentials: nano $PROJECT_DIR/.env"
echo "3. Copy template.png (if you have one) to: $PROJECT_DIR/"
echo ""
echo "Commands to manage the bot:"
echo "  Start bot:   sudo systemctl start storebot"
echo "  Stop bot:    sudo systemctl stop storebot"
echo "  Restart bot: sudo systemctl restart storebot"
echo "  View logs:   sudo journalctl -u storebot -f"
echo "  Check status: sudo systemctl status storebot"
echo ""
echo "=========================================="
