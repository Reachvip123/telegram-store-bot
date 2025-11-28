#!/bin/bash
# Quick VPS MongoDB Update Script
# Run this on your VPS to switch to MongoDB

echo "🚀 Updating VPS to use MongoDB Atlas..."

# Navigate to bot directory
cd /root/telegram-store-bot

# Stop current bot
echo "⏸️ Stopping current bot..."
sudo systemctl stop telegram-store-bot

# Backup current setup
echo "💾 Creating backup..."
mkdir -p backups/$(date +%Y%m%d_%H%M%S)
cp -r database/ backups/$(date +%Y%m%d_%H%M%S)/
cp storebot.py backups/$(date +%Y%m%d_%H%M%S)/
cp .env backups/$(date +%Y%m%d_%H%M%S)/

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Install MongoDB dependencies
echo "📦 Installing MongoDB packages..."
pip install -r requirements.txt

# Add MongoDB URI to .env
echo "⚙️ Updating .env file..."
if ! grep -q "MONGODB_URI" .env; then
    echo "MONGODB_URI=mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net/telegram_store_bot?retryWrites=true&w=majority&appName=Cluster0" >> .env
    echo "✅ Added MongoDB URI to .env"
else
    echo "✅ MongoDB URI already in .env"
fi

# Run migration (if data exists)
echo "🔄 Migrating data to MongoDB..."
if [ -f "database/products.json" ]; then
    python3 migrate_to_mongodb.py
else
    echo "ℹ️ No local data to migrate"
fi

# Update systemd service to use MongoDB bot
echo "🔧 Updating systemd service..."
sudo sed -i 's|storebot.py|storebot_mongodb.py|g' /etc/systemd/system/telegram-store-bot.service

# Reload systemd and restart bot
echo "🔄 Restarting bot with MongoDB..."
sudo systemctl daemon-reload
sudo systemctl start telegram-store-bot

# Check status
echo "📊 Checking bot status..."
sleep 3
sudo systemctl status telegram-store-bot --no-pager -l

echo ""
echo "✅ MongoDB update complete!"
echo ""
echo "🔍 To verify:"
echo "sudo journalctl -u telegram-store-bot -f"
echo ""
echo "🌐 MongoDB Atlas Dashboard:"
echo "https://cloud.mongodb.com"