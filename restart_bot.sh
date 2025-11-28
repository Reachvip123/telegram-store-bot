#!/bin/bash
# Complete bot restart script

echo "🔄 Stopping all bot instances..."
sudo pkill -9 -f storebot.py
sleep 2

echo "📥 Downloading latest bot code..."
cd /root/telegram-store-bot
sudo wget https://raw.githubusercontent.com/Reachvip123/telegram-store-bot/main/storebot.py -O storebot.py

echo "🚀 Starting bot..."
sudo /root/telegram-store-bot/venv/bin/python storebot.py > bot.log 2>&1 &

sleep 3

echo ""
echo "✅ Bot restarted!"
echo ""
echo "Check if running:"
ps aux | grep storebot.py | grep -v grep
echo ""
echo "View logs: tail -f /root/telegram-store-bot/bot.log"
