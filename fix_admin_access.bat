@echo off
echo.
echo 🔧 Quick Fix for Web Admin Access Issues
echo ========================================
echo.
echo The issue is likely one of these:
echo.
echo 1. ❌ FIREWALL BLOCKING PORT 5000
echo    Your VPS firewall is blocking port 5000
echo.
echo 2. ❌ VPS PROVIDER FIREWALL  
echo    Your VPS provider might block certain ports
echo.
echo 3. ❌ WRONG IP ADDRESS
echo    Make sure you're using the correct IP
echo.
echo 💡 QUICK SOLUTIONS:
echo ==================
echo.
echo 🔥 SOLUTION 1: Use different port (8080)
echo    SSH to VPS and run:
echo    python3 admin_panel.py 8080
echo    Then access: http://157.10.73.90:8080
echo.
echo 🔥 SOLUTION 2: Open firewall on VPS
echo    SSH to VPS and run these commands:
echo    sudo ufw allow 5000/tcp
echo    sudo ufw allow 8080/tcp
echo.
echo 🔥 SOLUTION 3: Check VPS provider panel
echo    Log into your VPS provider's control panel
echo    Look for firewall/security settings
echo    Open ports 5000 and 8080
echo.
echo 🔥 SOLUTION 4: Run on common port (80)
echo    python3 admin_panel.py 80
echo    Access: http://157.10.73.90
echo    (Might need sudo: sudo python3 admin_panel.py 80)
echo.
echo 📋 COMMANDS TO RUN ON VPS:
echo =========================
echo.
echo # Connect to VPS
echo ssh root@157.10.73.90
echo.
echo # Go to bot directory  
echo cd /root/telegram-store-bot
echo.
echo # Try different ports
echo python3 admin_panel.py 8080
echo python3 admin_panel.py 3000
echo python3 admin_panel.py 80
echo.
echo # Open firewall
echo sudo ufw allow 5000/tcp
echo sudo ufw allow 8080/tcp
echo sudo ufw allow 3000/tcp
echo.
echo # Check what's running
echo netstat -tulpn | grep python
echo.
echo 🎯 Most likely solution: Use port 8080!
echo    Port 5000 might be blocked by your provider.
echo.
pause