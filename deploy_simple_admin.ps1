# Simple VPS Web Admin Deployment
# Copy-paste the simple_vps_admin.py to your VPS easily

Write-Host "🎯 Simple Web Admin Panel for Cambodia VPS" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""

Write-Host "📋 What you need to do:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. SSH to your VPS:" -ForegroundColor White
Write-Host "   ssh root@157.10.73.90" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Go to your bot directory:" -ForegroundColor White
Write-Host "   cd /root/telegram-store-bot" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Create the admin file:" -ForegroundColor White
Write-Host "   nano admin_panel.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Copy the content from simple_vps_admin.py and paste it" -ForegroundColor White
Write-Host ""
Write-Host "5. Install required packages:" -ForegroundColor White
Write-Host "   pip install flask pymongo python-dotenv" -ForegroundColor Cyan
Write-Host ""
Write-Host "6. Run the admin panel:" -ForegroundColor White
Write-Host "   python3 admin_panel.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "7. Access in browser:" -ForegroundColor White
Write-Host "   http://157.10.73.90:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "8. Login with password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Benefits:" -ForegroundColor Green
Write-Host "✅ Everything on one VPS (bot + admin)" -ForegroundColor White
Write-Host "✅ Easy stock management" -ForegroundColor White
Write-Host "✅ Live dashboard" -ForegroundColor White
Write-Host "✅ No complex setup" -ForegroundColor White
Write-Host "✅ Same database as your bot" -ForegroundColor White
Write-Host ""
Write-Host "⚡ After setup, you can run both:" -ForegroundColor Yellow
Write-Host "  Terminal 1: python3 storebot.py     (your bot)" -ForegroundColor Cyan
Write-Host "  Terminal 2: python3 admin_panel.py  (web admin)" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to see the admin file content
$showContent = Read-Host "Do you want to see the admin panel code to copy? (y/n)"

if ($showContent -eq "y" -or $showContent -eq "Y") {
    Write-Host ""
    Write-Host "📄 simple_vps_admin.py content to copy:" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    
    if (Test-Path "simple_vps_admin.py") {
        Get-Content "simple_vps_admin.py" | Write-Host
    } else {
        Write-Host "❌ simple_vps_admin.py not found in current directory" -ForegroundColor Red
        Write-Host "Make sure you're in the correct folder" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🔥 This is the simplest solution!" -ForegroundColor Green
Write-Host "Everything runs on your Cambodia VPS!" -ForegroundColor Green