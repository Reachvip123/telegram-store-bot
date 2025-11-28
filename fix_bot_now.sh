#!/bin/bash
# Simple script to switch bot to MongoDB version

echo "======================================"
echo "Switching Bot to MongoDB Version"
echo "======================================"
echo ""

# Find where the bot is running
echo "Step 1: Finding your bot..."
BOT_LOCATION=$(ps aux | grep -E "storebot.*\.py" | grep -v grep | awk '{print $NF}' | head -1)

if [ -z "$BOT_LOCATION" ]; then
    echo "❌ Bot not found running!"
    echo "Let me check common locations..."
    
    # Check common locations
    if [ -f "/root/storebot.py" ]; then
        BOT_DIR="/root"
        echo "✅ Found bot in /root"
    elif [ -f "/home/ubuntu/storebot.py" ]; then
        BOT_DIR="/home/ubuntu"
        echo "✅ Found bot in /home/ubuntu"
    elif [ -f "$HOME/storebot.py" ]; then
        BOT_DIR="$HOME"
        echo "✅ Found bot in $HOME"
    else
        echo "❌ Cannot find storebot.py"
        echo "Please run: find / -name storebot.py 2>/dev/null"
        exit 1
    fi
else
    BOT_DIR=$(dirname "$BOT_LOCATION")
    echo "✅ Bot running from: $BOT_DIR"
fi

echo ""
echo "Step 2: Stopping old bot..."
pkill -f "storebot.py"
sleep 2

echo ""
echo "Step 3: Checking if MongoDB version exists..."
if [ ! -f "$BOT_DIR/storebot_mongodb.py" ]; then
    echo "❌ storebot_mongodb.py not found in $BOT_DIR"
    echo "Uploading it now..."
    # User needs to upload it first
    echo "Please run from your PC:"
    echo "scp storebot_mongodb.py root@157.10.73.90:$BOT_DIR/"
    exit 1
fi

echo "✅ MongoDB version found!"

echo ""
echo "Step 4: Starting MongoDB bot..."
cd "$BOT_DIR"
nohup python3 storebot_mongodb.py > bot_mongodb.log 2>&1 &
sleep 3

echo ""
echo "Step 5: Checking if it's running..."
if ps aux | grep -q "[s]torebot_mongodb.py"; then
    echo "✅ SUCCESS! Bot is now running with MongoDB!"
    echo ""
    echo "📊 Check logs:"
    echo "   tail -f $BOT_DIR/bot_mongodb.log"
    echo ""
    echo "🎉 All data now saves to MongoDB Atlas!"
else
    echo "❌ Bot failed to start. Check logs:"
    echo "   cat $BOT_DIR/bot_mongodb.log"
fi

echo ""
echo "======================================"
