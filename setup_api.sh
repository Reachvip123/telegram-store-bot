#!/bin/bash
# VPS Setup Script for Bot API

echo "==========================================="
echo "Setting up Bot API on VPS"
echo "==========================================="

# Navigate to home directory
cd /root

# Check if bot directory exists
if [ ! -d "telegram-store-bot" ]; then
    echo "Cloning repository..."
    git clone https://github.com/Reachvip123/telegram-store-bot.git
fi

cd telegram-store-bot

# Pull latest code
echo "Pulling latest code..."
git pull origin main

# Install dependencies
echo "Installing dependencies..."
pip3 install flask flask-cors requests

# Check if database folder exists
if [ ! -d "database" ]; then
    echo "Creating database folder..."
    mkdir -p database
fi

# Stop any existing API server
echo "Stopping existing API server..."
pkill -f bot_api.py 2>/dev/null || true

# Open firewall
echo "Opening firewall port 5000..."
sudo ufw allow 5000/tcp 2>/dev/null || true

# Start API server
echo "Starting API server..."
nohup python3 bot_api.py > bot_api.log 2>&1 &

sleep 2

echo ""
echo "==========================================="
echo "Bot API Setup Complete!"
echo "==========================================="
echo "API running at: http://157.10.73.90:5000"
echo "API Key: your-secret-api-key-change-this"
echo ""
echo "To check status: tail -f /root/telegram-store-bot/bot_api.log"
echo "To stop API: pkill -f bot_api.py"
echo "==========================================="
