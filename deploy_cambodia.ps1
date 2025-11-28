# Deploy Bot to Cambodia VPS
# Run this script from Windows PowerShell

$VPS_IP = "157.10.73.90"
$VPS_USER = "root"
$BOT_DIR = "/root/telegram-store-bot"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🚀 Deploying Bot to Cambodia VPS (157.10.73.90)" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Upload files
Write-Host "📤 Step 1: Uploading files to VPS..." -ForegroundColor Green
Write-Host "Uploading storebot.py..." -ForegroundColor White
scp storebot.py ${VPS_USER}@${VPS_IP}:${BOT_DIR}/

Write-Host "Uploading .env..." -ForegroundColor White
scp .env ${VPS_USER}@${VPS_IP}:${BOT_DIR}/

Write-Host "Uploading requirements.txt..." -ForegroundColor White
scp requirements.txt ${VPS_USER}@${VPS_IP}:${BOT_DIR}/

Write-Host ""
Write-Host "✅ Files uploaded successfully!" -ForegroundColor Green
Write-Host ""

# Step 2: Setup and run on VPS
Write-Host "🔧 Step 2: Setting up bot on VPS..." -ForegroundColor Green

$commands = @"
cd $BOT_DIR
echo '📦 Installing dependencies...'
pip3 install python-telegram-bot pymongo python-dotenv requests --quiet
echo '🛑 Stopping old bot...'
pkill -f storebot.py
sleep 2
echo '🚀 Starting bot...'
nohup python3 storebot.py > bot.log 2>&1 &
sleep 3
echo ''
echo '✅ Bot deployment complete!'
echo ''
if pgrep -f storebot.py > /dev/null; then
    echo '✅ Bot is RUNNING!'
    ps aux | grep storebot.py | grep -v grep
    echo ''
    echo '📋 Last 10 lines of log:'
    tail -10 bot.log
else
    echo '❌ Bot FAILED to start!'
    echo '📋 Error log:'
    tail -20 bot.log
fi
"@

ssh ${VPS_USER}@${VPS_IP} $commands

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Test bot: Send /start to your Telegram bot" -ForegroundColor White
Write-Host "   2. View logs: ssh root@157.10.73.90 'tail -f /root/telegram-store-bot/bot.log'" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Useful Commands:" -ForegroundColor Yellow
Write-Host "   Check status: ssh root@157.10.73.90 'ps aux | grep storebot.py'" -ForegroundColor White
Write-Host "   View logs: ssh root@157.10.73.90 'tail -50 /root/telegram-store-bot/bot.log'" -ForegroundColor White
Write-Host "   Stop bot: ssh root@157.10.73.90 'pkill -f storebot.py'" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
