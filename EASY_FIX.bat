@echo off
echo ========================================
echo Fix Bot to Use MongoDB
echo ========================================
echo.
echo Step 1: Connecting to your VPS...
echo.

ssh root@157.10.73.90 "cd /root/telegram-store-bot && pkill -f storebot.py && nohup python3 storebot_mongodb.py > bot.log 2>&1 & && sleep 2 && ps aux | grep storebot"

echo.
echo ========================================
echo Done! Your bot is now using MongoDB!
echo ========================================
echo.
pause
