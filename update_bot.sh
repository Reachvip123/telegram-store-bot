#!/bin/bash
# Update bot script - downloads latest storebot.py from GitHub

echo "Updating bot from GitHub..."

# Download latest storebot.py
wget -O storebot.py https://raw.githubusercontent.com/Reachvip123/telegram-store-bot/main/storebot.py

echo "✅ Bot updated!"
echo ""
echo "Now restart your bot:"
echo "  pkill -f storebot.py"
echo "  nohup python3 storebot.py > bot.log 2>&1 &"
