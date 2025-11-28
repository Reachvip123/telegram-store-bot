#!/bin/bash
# Troubleshoot Admin Panel Access Issues
echo "🔍 Diagnosing admin panel access issues..."
echo ""

# Check if admin panel service is running
echo "1️⃣ Checking admin panel service status:"
sudo systemctl status telegram-admin-panel --no-pager -l
echo ""

# Check if process is running
echo "2️⃣ Checking if admin panel process is running:"
ps aux | grep admin_panel.py
echo ""

# Check if port 8080 is open and listening
echo "3️⃣ Checking if port 8080 is listening:"
sudo netstat -tlnp | grep :8080
echo ""

# Check firewall status
echo "4️⃣ Checking firewall status:"
sudo ufw status
echo ""

# Check admin panel logs
echo "5️⃣ Recent admin panel logs:"
sudo journalctl -u telegram-admin-panel -n 20 --no-pager
echo ""

# Test if we can connect locally
echo "6️⃣ Testing local connection:"
curl -I http://localhost:8080 2>/dev/null || echo "Cannot connect to localhost:8080"
echo ""

# Check if MongoDB connection works
echo "7️⃣ Testing MongoDB connection:"
cd /root/telegram-store-bot
python3 -c "
try:
    from pymongo import MongoClient
    import os
    from dotenv import load_dotenv
    load_dotenv()
    uri = os.getenv('MONGODB_URI', '')
    if uri:
        client = MongoClient(uri)
        client.admin.command('ping')
        print('✅ MongoDB connection OK')
    else:
        print('❌ No MONGODB_URI found')
except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
"
echo ""

# Provide solutions
echo "🔧 SOLUTIONS:"
echo ""
echo "If service not running:"
echo "  sudo systemctl start telegram-admin-panel"
echo ""
echo "If port not listening:"
echo "  sudo systemctl restart telegram-admin-panel"
echo ""
echo "If firewall blocking:"
echo "  sudo ufw allow 8080"
echo ""
echo "If MongoDB issues:"
echo "  Check MONGODB_URI in .env file"
echo ""
echo "Manual start (for testing):"
echo "  cd /root/telegram-store-bot"
echo "  python3 admin_panel.py"
echo ""

# Show .env file (without sensitive data)
echo "8️⃣ Environment configuration:"
echo "MONGODB_URI present: $(grep -q 'MONGODB_URI' /root/telegram-store-bot/.env && echo 'YES' || echo 'NO')"
echo "ADMIN_PASSWORD present: $(grep -q 'ADMIN_PASSWORD' /root/telegram-store-bot/.env && echo 'YES' || echo 'NO')"
echo ""